"""
LATS (Language Agent Tree Search) Implementation

LATS combines language agent reasoning with tree search over trajectories.
Instead of a single path, the agent explores multiple possible action sequences,
evaluating and pruning to find the optimal solution.

Key Pattern:
    State → Generate multiple actions → Evaluate branches → Prune weak paths → Best path

Real LLM Integration: Uses Claude API OR Local Ollama to generate reasoning trajectories and evaluate them.

Requirements:
    Option 1 (Anthropic): pip install anthropic
    Option 2 (Local): pip install requests

Setup:
    OPTION 1: Use Anthropic API (Claude)
        1. Get your API key from https://console.anthropic.com
        2. Export: export ANTHROPIC_API_KEY='your-key'
        3. Run: python lats_agent.py

    OPTION 2: Use Local Model (Ollama - NO API KEY NEEDED)
        1. Install Ollama: https://ollama.ai
        2. Run: ollama pull mistral && ollama serve
        3. Run: python lats_agent.py
"""

from typing import List, Dict, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
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
class SearchNode:
    """A node in the search tree"""
    state: str
    depth: int
    parent: 'SearchNode' = None
    children: List['SearchNode'] = None
    value: float = 0.0
    is_terminal: bool = False

    def __post_init__(self):
        if self.children is None:
            self.children = []


class LATSAgent:
    """
    LATS Agent - Language Agent Tree Search

    This agent uses Claude to explore multiple reasoning paths simultaneously,
    evaluating and pruning branches to find optimal solutions.
    """

    def __init__(self, name: str = "LATSAgent", beam_width: int = 3):
        self.name = name
        self.beam_width = beam_width  # Number of best paths to keep
        self.root = None
        self.best_path = None
        self.explored_states: Set[str] = set()
        self.model = "claude-3-5-sonnet-20241022"

    def solve(self, problem: str, goal_state: str) -> Tuple[List[str], float]:
        """
        Solve a problem using tree search over language agent trajectories

        Args:
            problem: Initial problem statement
            goal_state: Target state to reach

        Returns:
            Tuple of (path_taken, final_score)
        """
        print(f"\n{'='*60}")
        print(f"Problem: {problem}")
        print(f"Goal: {goal_state}")
        print(f"Beam Width: {self.beam_width} (explore top {self.beam_width} branches)")
        print(f"{'='*60}\n")

        # Initialize root node
        self.root = SearchNode(state=problem, depth=0)
        self.explored_states = set()

        # BEAM SEARCH
        current_level = [self.root]
        level = 0

        while current_level and level < 5:  # Max 5 levels
            level += 1
            print(f"--- Level {level} ---")
            print(f"Exploring {len(current_level)} nodes with beam width {self.beam_width}\n")

            next_level = []
            all_candidates = []

            # EXPAND: Generate children for each node in current level
            for node in current_level:
                children = self._generate_children(node, problem, goal_state)
                print(f"From state '{node.state}' → generated {len(children)} actions")

                for child in children:
                    all_candidates.append(child)
                    node.children.append(child)

            # EVALUATE & PRUNE: Keep only top beam_width candidates
            all_candidates.sort(key=lambda x: x.value, reverse=True)

            print(f"\nEvaluated {len(all_candidates)} candidates, keeping top {self.beam_width}:")
            for i, node in enumerate(all_candidates[:self.beam_width]):
                print(f"  {i+1}. State: '{node.state}' (score: {node.value:.2f})")
                next_level.append(node)

                # Check if terminal (goal reached)
                if node.is_terminal:
                    self.best_path = self._reconstruct_path(node)
                    print(f"\n✓ Goal reached! Path: {' → '.join(self.best_path)}")
                    return self.best_path, node.value

            current_level = next_level
            print()

        # Return best path found
        if self.best_path is None:
            self.best_path = self._reconstruct_path(all_candidates[0] if all_candidates else self.root)

        print(f"✓ Best path found: {' → '.join(self.best_path)}")
        return self.best_path, all_candidates[0].value if all_candidates else 0.0

    def _generate_children(self, node: SearchNode, problem: str, goal: str) -> List[SearchNode]:
        """
        Generate child nodes by having Claude explore different reasoning strategies

        Claude generates multiple distinct approaches to solve the problem.
        """
        children = []

        prompt = f"""Given this problem: {problem}
Goal: {goal}
Current state: {node.state}

Generate 5 different reasoning strategies to explore. For each strategy:
- Think about a distinct approach (different from others)
- Explain how it could help reach the goal
- Rate how promising it is (0-1)

Format each as:
STRATEGY: [strategy name]
APPROACH: [how to apply it]
SCORE: [0-1]

Be concise but specific."""

        try:
            if USE_LOCAL_MODEL:
                response = client.messages_create(
                    system="You are exploring multiple solution paths for a complex problem. Generate diverse, thoughtful strategies.",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=800
                )
            else:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=800,
                    system="You are exploring multiple solution paths for a complex problem. Generate diverse, thoughtful strategies.",
                    messages=[{"role": "user", "content": prompt}]
                )

            response_text = response.content[0].text
            print(f"\n[🤖 MODEL GENERATED - Strategy Generation]\n{response_text}\n")

            # Parse Claude's strategies
            strategies_text = response_text.split("STRATEGY:")

            for strategy_block in strategies_text[1:]:  # Skip first empty split
                lines = strategy_block.strip().split("\n")

                strategy_name = lines[0].strip() if lines else "Unknown"
                approach = ""
                score = 0.5

                for line in lines[1:]:
                    if line.startswith("APPROACH:"):
                        approach = line.replace("APPROACH:", "").strip()
                    elif line.startswith("SCORE:"):
                        try:
                            score = float(line.replace("SCORE:", "").strip())
                        except:
                            score = 0.5

                new_state = f"{strategy_name}: {approach}"

                # Skip if already explored
                if new_state in self.explored_states:
                    continue

                self.explored_states.add(new_state)

                # Evaluate proximity to goal using Claude
                proximity_bonus = self._evaluate_proximity(new_state, goal, node.depth)
                final_score = min(score + proximity_bonus, 1.0)

                child = SearchNode(
                    state=new_state,
                    depth=node.depth + 1,
                    parent=node,
                    value=final_score,
                    is_terminal=(proximity_bonus > 0.3)
                )

                children.append(child)

        except Exception as e:
            print(f"Error generating children with Claude: {e}")

        return children

    def _evaluate_proximity(self, state: str, goal: str, depth: int) -> float:
        """
        Evaluate how close a state is to the goal using Claude's reasoning

        Returns a score from 0 to 0.4
        """
        prompt = f"""Evaluate how close this state is to reaching the goal:

Goal: {goal}
Current State: {state}

How much progress has been made? Rate from 0 (no progress) to 1 (goal reached).
Also consider path efficiency (shorter paths are better).

Respond with only a number between 0 and 1."""

        try:
            if USE_LOCAL_MODEL:
                response = client.messages_create(
                    system="You are evaluating problem-solving progress. Be analytical and fair.",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50
                )
            else:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=50,
                    system="You are evaluating problem-solving progress. Be analytical and fair.",
                    messages=[{"role": "user", "content": prompt}]
                )

            response_text = response.content[0].text.strip()
            print(f"[🤖 MODEL EVALUATION]\n{response_text}\n")

            # Extract score from response
            try:
                score = float(response_text.split()[0])
                score = max(0, min(score, 1.0))  # Clamp to 0-1
            except:
                score = 0.5

        except Exception as e:
            print(f"Error evaluating proximity: {e}")
            score = 0.5

        # Apply depth penalty (prefer shorter paths)
        depth_penalty = max(0, 0.1 - depth * 0.02)
        final_score = (score * 0.4) + depth_penalty

        return min(final_score, 0.4)

    def _reconstruct_path(self, node: SearchNode) -> List[str]:
        """Reconstruct the path from root to given node"""
        path = []
        current = node

        while current is not None:
            path.append(current.state)
            current = current.parent

        return list(reversed(path))

    def print_search_tree(self, node: SearchNode = None, indent: str = "", is_root: bool = True):
        """Print the search tree structure with enhanced labels"""
        if node is None:
            node = self.root

        # Format node display
        state_text = node.state[:60] + "..." if len(node.state) > 60 else node.state

        # Add depth label
        depth_label = "ROOT" if node.depth == 0 else f"Level {node.depth}"

        # Add score interpretation
        if node.value >= 0.95:
            score_label = "✓ GOAL!"
        elif node.value >= 0.8:
            score_label = "✓ Strong"
        elif node.value >= 0.6:
            score_label = "○ Medium"
        else:
            score_label = "○ Weak"

        print(f"{indent}├─ [{depth_label}] {state_text}")
        print(f"{indent}│  └─ Score: {node.value:.2f} ({score_label})")

        # Show children
        if node.children:
            print(f"{indent}│  Explored {len(node.children)} path(s):")
            for i, child in enumerate(node.children):
                is_last = i == len(node.children) - 1
                child_indent = indent + ("     " if is_last else "│    ")
                print(f"{child_indent}├─ {child.state[:50]}...")
                print(f"{child_indent}│  Score: {child.value:.2f}")

                if child.children:
                    next_indent = indent + ("     " if is_last else "│    ")
                    self.print_search_tree(child, next_indent, is_root=False)

        print()

    def print_summary(self):
        """Print summary of the search process"""
        print(f"\n{'='*60}")
        print(f"LATS Agent Summary")
        print(f"{'='*60}")
        print(f"Explored states: {len(self.explored_states)}")
        print(f"Beam width: {self.beam_width}")
        print(f"Best path found: {' → '.join(self.best_path) if self.best_path else 'None'}")


def main():
    """Interactive LATS Agent - Tree Search Problem Solver"""

    print("\n" + "="*70)
    print("🌳 LATS AGENT - Language Agent Tree Search 🌳".center(70))
    print("="*70)
    print("\nExplore multiple solution paths simultaneously!")
    print("Model: Mistral (via Ollama) | Beam Width: Control search breadth")
    print("="*70)

    while True:
        print("\n" + "-"*70)
        print("LATS TREE SEARCH SETUP")
        print("-"*70)

        # Get problem from user
        print("\nEnter your problem (what do you want to solve?):")
        print("Examples:")
        print("  - The shoe store has a large assortment of shoes and related items. They had 50 boxes of shoes and many pair of socks. The store put two pairs of socks in 1 out of every t10 shoes bozes as a gift. How many pairs of socks were given out altogether?")
        print("  - If A is larger than B, and B is larger than C, what is the order?")
        print("  - What are effective strategies for debugging code?")
        print("-"*70)

        problem = input("Problem: ").strip()

        if not problem:
            print("❌ Problem cannot be empty. Please try again.")
            continue

        # Get goal state from user
        print("\nWhat is your goal? (what do you want to achieve?)")
        print("Examples:")
        print("  - Find the numerical solution")
        print("  - Determine the correct ordering")
        print("  - Identify effective debugging strategies")
        print("-"*70)

        goal = input("Goal: ").strip()

        if not goal:
            print("❌ Goal cannot be empty. Please try again.")
            continue

        # Get beam width (optional)
        print("\nHow many paths should the agent explore at each level?")
        print("(Default: 3 - higher values explore more but take longer)")
        print("-"*70)

        beam_input = input("Beam width (1-5, press Enter for 3): ").strip()

        beam_width = 3  # Default
        if beam_input:
            try:
                beam_width = int(beam_input)
                if beam_width < 1 or beam_width > 5:
                    print("⚠️  Beam width must be 1-5. Using default: 3")
                    beam_width = 3
            except ValueError:
                print("⚠️  Invalid input. Using default beam width: 3")
                beam_width = 3

        # Solve using LATS
        print(f"\n{'='*70}")
        print(f"🌳 SOLVING WITH TREE SEARCH (Beam Width: {beam_width})")
        print(f"{'='*70}")

        agent = LATSAgent(f"LATS-Interactive", beam_width=beam_width)

        try:
            path, score = agent.solve(problem=problem, goal_state=goal)

            # Show results
            print(f"\n{'='*70}")
            print(f"SOLUTION FOUND")
            print(f"{'='*70}")
            print(f"\n✓ Path taken: {' → '.join(path)}")
            print(f"✓ Final Score: {score:.2f}")

            # Show summary
            print(f"\n{'='*70}")
            print(f"SEARCH SUMMARY")
            print(f"{'='*70}")
            agent.print_summary()

            print(f"\n{'='*70}")
            print(f"SEARCH TREE STRUCTURE")
            print(f"{'='*70}")
            agent.print_search_tree()

        except Exception as e:
            print(f"\n❌ Error solving problem: {e}")
            import traceback
            traceback.print_exc()
            continue

        # Ask if user wants to try another problem
        print(f"\n{'='*70}")
        again = input("Try another problem? (yes/no): ").strip().lower()
        if again not in ["yes", "y"]:
            print("\n✨ Thank you for using LATS Agent! Goodbye!\n")
            break


if __name__ == "__main__":
    # Check if API key is set (only needed for Anthropic API mode)
    if not USE_LOCAL_MODEL and not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your API key: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)

    main()
