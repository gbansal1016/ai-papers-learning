"""
Reflexion Agent Implementation

Reflexion enables language agents to learn from failures through self-reflection.
The agent attempts a task, evaluates its own failure, reflects on what went wrong,
and uses that reflection to improve subsequent attempts.

Key Pattern:
    Attempt → Evaluate → Reflect (if failed) → Improve → Retry

Real LLM Integration: Uses Claude API OR Local Ollama for actual attempt generation and reflection reasoning.

Requirements:
    Option 1 (Anthropic): pip install anthropic
    Option 2 (Local): pip install requests

Setup:
    OPTION 1: Use Anthropic API (Claude)
        1. Get your API key from https://console.anthropic.com
        2. Export: export ANTHROPIC_API_KEY='your-key'
        3. Run: python reflexion_agent.py

    OPTION 2: Use Local Model (Ollama - NO API KEY NEEDED)
        1. Install Ollama: https://ollama.ai
        2. Run: ollama pull mistral && ollama serve
        3. Run: python reflexion_agent.py
"""

from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import os
import requests
from anthropic import Anthropic

# ============================================================================
# OLLAMA CLIENT - Wrapper for calling Ollama API
# ============================================================================

class OllamaClient:
    """Wrapper for Ollama API optimized for local models like Mistral"""
    def __init__(self, model="mistral"):
        self.model = model
        self.api_url = "http://localhost:11434/api/generate"

    def messages_create(self, system, messages, max_tokens=1000):
        """Create a message using Ollama API with proper prompt formatting"""
        full_prompt = system + "\n\n"
        for msg in messages:
            role = msg["role"].upper()
            content = msg["content"]
            if role == "USER":
                full_prompt += f"User: {content}\n\n"
            elif role == "ASSISTANT":
                full_prompt += f"Assistant: {content}\n\n"
        full_prompt += "Assistant: "

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": 0.3,
                    "num_predict": max_tokens,
                },
                timeout=120
            )
            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.status_code}")
            response_text = response.json().get("response", "").strip()
            class MockResponse:
                def __init__(self, text):
                    self.content = [type('obj', (object,), {'text': text})]
            return MockResponse(response_text)
        except Exception as e:
            raise Exception(f"Ollama error: {e}")

# ============================================================================
# CONFIGURATION - Switch between Anthropic API and Local Models
# ============================================================================

USE_LOCAL_MODEL = True  # Set to False to use Anthropic API instead

if USE_LOCAL_MODEL:
    print("🚀 Using LOCAL model (Ollama)")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print(f"✓ Ollama is running with models: {[m['name'] for m in models]}\n")
            else:
                print("⚠️  Ollama running but no models. Running: ollama pull mistral\n")
                os.system("ollama pull mistral")
        else:
            raise Exception("Ollama not responding")
    except Exception as e:
        print(f"❌ ERROR: Ollama is not running!")
        print(f"   Error: {e}")
        print("   Start Ollama: /Users/gaurav/Documents/Ollama/restart_ollama.sh")
        exit(1)
    client = OllamaClient(model="mistral")
    MODEL_NAME = "mistral"
else:
    print("🔑 Using Anthropic API (Claude)")
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        exit(1)
    client = Anthropic()
    MODEL_NAME = "claude-3-5-sonnet-20241022"

print(f"✓ Model: {MODEL_NAME}\n")


@dataclass
class Reflection:
    """A reflection on a failed attempt"""
    attempt_num: int
    failed_action: str
    reason_for_failure: str
    lesson_learned: str
    improved_strategy: str


@dataclass
class AttemptResult:
    """Result of an attempt at solving a task"""
    attempt_num: int
    action: str
    outcome: str
    success: bool
    reflection: Reflection = None


class TaskValidator:
    """Validates if a task was completed successfully"""

    @staticmethod
    def validate_math_solution(problem: str, solution: str) -> Tuple[bool, str]:
        """Validate a math solution by extracting the expression from verbose output"""
        try:
            # Check if solution contains equals sign
            if "=" not in solution:
                return False, "Solution format incorrect (missing '=')"

            # Extract mathematical expression: look for pattern like "25 * 4 + 10 = 110"
            # This handles verbose model outputs by finding the actual math expression
            import re
            # Try to find pattern: number/expression = number/expression
            matches = re.findall(r'(\d+[\s\*\+\-\/\(\)]*\d+[\s\*\+\-\/\(\)]*)\s*=\s*(\d+)', solution)

            if matches:
                # Use the extracted expression
                left, right = matches[0]
                left = left.strip()
                right = right.strip()
            else:
                # Fallback to simple split if regex doesn't work
                parts = solution.split("=")
                if len(parts) < 2:
                    return False, "Solution format incorrect (missing '=')"
                left = parts[-2].strip()  # Get last equation part
                right = parts[-1].strip()

            print(f"[VALIDATOR] Evaluating: '{left}' = '{right}'")

            # Evaluate both sides
            answer = eval(left)
            expected = eval(right)

            print(f"[VALIDATOR] Result: {answer} = {expected} ? {answer == expected}")

            if answer == expected:
                return True, "Correct solution"
            else:
                return False, f"Incorrect math (got {answer}, expected {expected})"
        except Exception as e:
            print(f"[VALIDATOR] Exception: {e}")
            return False, f"Invalid mathematical expression: {str(e)}"

    @staticmethod
    def validate_logic_solution(problem: str, solution: str) -> Tuple[bool, str]:
        """Validate a logical solution"""
        solution_lower = solution.lower()
        problem_lower = problem.lower()

        # Simple validation rules
        if "correct" in solution_lower or "right" in solution_lower:
            return True, "Logical reasoning appears sound"
        elif "wrong" in solution_lower or "incorrect" in solution_lower:
            return False, "Solution identifies itself as incorrect"
        else:
            return True, "Logical conclusion provided"


class ReflexionAgent:
    """
    Reflexion Agent - Learns from failures through self-reflection

    This agent uses Claude to:
    - Generate attempts at solving a problem
    - Evaluate the result
    - If failed, reflect on what went wrong using Claude's reasoning
    - Use reflection to improve the next attempt
    """

    def __init__(self, name: str = "ReflexionAgent"):
        self.name = name
        self.max_attempts = 4
        self.attempts: List[AttemptResult] = []
        self.reflections: List[Reflection] = []
        self.validator = TaskValidator()
        self.model = "claude-3-5-sonnet-20241022"
        self.conversation_history: List[Dict[str, str]] = []

    def solve(self, problem: str, problem_type: str = "logic") -> str:
        """
        Solve a problem with reflection and improvement

        Args:
            problem: The problem to solve
            problem_type: Either 'math' or 'logic'
        """
        print(f"\n{'='*60}")
        print(f"Problem: {problem}")
        print(f"Problem Type: {problem_type}")
        print(f"{'='*60}\n")

        for attempt_num in range(1, self.max_attempts + 1):
            print(f"--- Attempt {attempt_num} ---")

            # STEP 1: ATTEMPT
            action = self._generate_attempt(problem, attempt_num, problem_type)
            print(f"Action: {action}")

            # STEP 2: EVALUATE
            success, feedback = self._evaluate(problem, action, problem_type)
            print(f"Outcome: {'✓ Success' if success else '✗ Failed'}")
            print(f"Feedback: {feedback}")

            # Store attempt
            attempt = AttemptResult(
                attempt_num=attempt_num,
                action=action,
                outcome=feedback,
                success=success
            )
            self.attempts.append(attempt)

            # STEP 3: REFLECT (if failed)
            if not success and attempt_num < self.max_attempts:
                reflection = self._reflect(problem, action, feedback, attempt_num)
                print(f"\nReflection:")
                print(f"  Why it failed: {reflection.reason_for_failure}")
                print(f"  Lesson learned: {reflection.lesson_learned}")
                print(f"  New strategy: {reflection.improved_strategy}")
                print()

                attempt.reflection = reflection
                self.reflections.append(reflection)
            elif success:
                print(f"\n✓ Successfully solved in {attempt_num} attempt(s)!\n")
                return action
            else:
                print(f"\nMax attempts reached.\n")

        # Return best attempt if no success
        return self.attempts[-1].action

    def _generate_attempt(self, problem: str, attempt_num: int, problem_type: str) -> str:
        """
        Generate an attempt at solving the problem using Claude API

        Claude reasons through the problem, potentially using reflections from
        previous failures to improve the solution.
        """
        # Build prompt with context
        if attempt_num == 1:
            system_prompt = f"You are a {problem_type} problem solver. Solve this problem carefully and show your work. Format your final answer clearly."
            user_message = f"Problem: {problem}\n\nPlease solve this step by step."
        else:
            # Include reflection context from previous attempts
            reflection_context = "\n".join([
                f"Attempt {ref.attempt_num}: Failed because - {ref.reason_for_failure}. Lesson: {ref.lesson_learned}"
                for ref in self.reflections[-min(attempt_num-1, 3):]
            ])
            system_prompt = f"You are a {problem_type} problem solver. You've learned from previous attempts. Use those lessons to solve this better. Format your final answer clearly."
            user_message = f"Problem: {problem}\n\nLessons from previous attempts:\n{reflection_context}\n\nPlease solve this step by step, applying the lessons learned."

        # Get Claude's attempt or Mistral's attempt
        try:
            if USE_LOCAL_MODEL:
                response = client.messages_create(
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                    max_tokens=500
                )
            else:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}]
                )
            assistant_message = response.content[0].text
            print(f"\n[🤖 MODEL GENERATED - Attempt]\n{assistant_message}\n")
            return assistant_message
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return f"Error generating attempt: {str(e)}"

    def _evaluate(self, problem: str, solution: str, problem_type: str) -> Tuple[bool, str]:
        """Evaluate if the solution is correct"""
        if problem_type == "math":
            return self.validator.validate_math_solution(problem, solution)
        else:
            return self.validator.validate_logic_solution(problem, solution)

    def _reflect(self, problem: str, failed_action: str, feedback: str, attempt_num: int) -> Reflection:
        """
        Generate a reflection on the failed attempt using Claude API

        Claude analyzes why the attempt failed and suggests improvements.
        """
        reflection_prompt = f"""Analyze this failed attempt at problem solving:

Problem: {problem}

Previous Attempt:
{failed_action}

Why it failed:
{feedback}

Please provide:
1. A concise reason for the failure (one sentence)
2. A key lesson learned from this failure (one sentence)
3. A specific improved strategy for the next attempt (one sentence)

Format your response exactly as:
REASON: [reason]
LESSON: [lesson]
STRATEGY: [strategy]"""

        try:
            if USE_LOCAL_MODEL:
                response = client.messages_create(
                    system="You are an analytical coach helping someone improve at problem solving. Focus on concrete, actionable insights.",
                    messages=[{"role": "user", "content": reflection_prompt}],
                    max_tokens=300
                )
            else:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=300,
                    system="You are an analytical coach helping someone improve at problem solving. Focus on concrete, actionable insights.",
                    messages=[{"role": "user", "content": reflection_prompt}]
                )

            response_text = response.content[0].text
            print(f"\n[🤖 MODEL GENERATED - Reflection]\n{response_text}\n")

            # Parse the response
            reason = "Analysis incomplete"
            lesson = "Continue improving"
            strategy = "Try a different approach"

            for line in response_text.split("\n"):
                if line.startswith("REASON:"):
                    reason = line.replace("REASON:", "").strip()
                elif line.startswith("LESSON:"):
                    lesson = line.replace("LESSON:", "").strip()
                elif line.startswith("STRATEGY:"):
                    strategy = line.replace("STRATEGY:", "").strip()

            return Reflection(
                attempt_num=attempt_num,
                failed_action=failed_action,
                reason_for_failure=reason,
                lesson_learned=lesson,
                improved_strategy=strategy
            )
        except Exception as e:
            print(f"Error generating reflection: {e}")
            return Reflection(
                attempt_num=attempt_num,
                failed_action=failed_action,
                reason_for_failure=f"Error: {str(e)}",
                lesson_learned="Retry with new approach",
                improved_strategy="Try alternative method"
            )

    def print_summary(self):
        """Print summary of reflexion process"""
        print(f"\n{'='*60}")
        print(f"Reflexion Agent Summary")
        print(f"{'='*60}")
        print(f"Total attempts: {len(self.attempts)}")
        print(f"Total reflections: {len(self.reflections)}")

        # Show final result
        for attempt in self.attempts:
            if attempt.success:
                print(f"\n✓ Success on attempt {attempt.attempt_num}")
                print(f"  Solution: {attempt.action}")
                return

        print(f"\n✗ No successful solution found")
        print(f"  Final attempt: {self.attempts[-1].action}")

    def show_learning_curve(self):
        """Show how the agent improved over time"""
        print(f"\n{'='*60}")
        print(f"Learning Progression")
        print(f"{'='*60}")

        for attempt in self.attempts:
            status = "✓ SUCCESS" if attempt.success else "✗ FAILED"
            print(f"\nAttempt {attempt.attempt_num}: {status}")
            print(f"  Action: {attempt.action}")
            print(f"  Outcome: {attempt.outcome}")

            if attempt.reflection:
                print(f"  Reflection:")
                print(f"    - Why: {attempt.reflection.reason_for_failure}")
                print(f"    - Lesson: {attempt.reflection.lesson_learned}")
                print(f"    - Next: {attempt.reflection.improved_strategy}")


def main():
    """Interactive Reflexion Agent"""

    print("\n" + "="*70)
    print("🧠 REFLEXION AGENT - Interactive Problem Solver 🧠".center(70))
    print("="*70)
    print("\nLearn from failures through self-reflection and improvement!")
    print("Max attempts: 4 | Local Model: Mistral (via Ollama)")
    print("="*70)

    while True:
        print("\n" + "-"*70)
        print("PROBLEM TYPE SELECTION")
        print("-"*70)
        print("1. Math Problem    (e.g., 'Solve: 3x + 5 = 20')")
        print("2. Logic Problem   (e.g., 'Is a square also a rectangle?')")
        print("3. Quit")
        print("-"*70)

        choice = input("\nSelect problem type (1/2/3): ").strip()

        if choice == "3":
            print("\n✨ Thank you for using Reflexion Agent! Goodbye!\n")
            break

        if choice not in ["1", "2"]:
            print("❌ Invalid choice. Please select 1, 2, or 3.")
            continue

        # Get problem type
        if choice == "1":
            problem_type = "math"
            type_name = "MATH PROBLEM"
            example = "Example: Solve 2x + 3 = 11 for x"
        else:
            problem_type = "logic"
            type_name = "LOGIC PROBLEM"
            example = "Example: If all cats are animals, and Fluffy is a cat, is Fluffy an animal?"

        # Get problem from user
        print(f"\n{type_name}")
        print(f"{example}")
        print("-"*70)
        problem = input("Enter your problem: ").strip()

        if not problem:
            print("❌ Problem cannot be empty. Please try again.")
            continue

        # Create agent and solve
        agent_name = f"Reflexion-{problem_type.upper()}"
        agent = ReflexionAgent(agent_name)

        print(f"\n{'='*70}")
        print(f"🤔 SOLVING YOUR {problem_type.upper()} PROBLEM")
        print(f"{'='*70}")

        try:
            answer = agent.solve(problem, problem_type=problem_type)
            agent.show_learning_curve()
        except Exception as e:
            print(f"\n❌ Error solving problem: {e}")
            continue

        # Ask if user wants to try another problem
        print(f"\n{'='*70}")
        again = input("Try another problem? (yes/no): ").strip().lower()
        if again not in ["yes", "y"]:
            print("\n✨ Thank you for using Reflexion Agent! Goodbye!\n")
            break


if __name__ == "__main__":
    # Check if API key is set (only needed for Anthropic API mode)
    if not USE_LOCAL_MODEL and not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your API key: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)

    main()
