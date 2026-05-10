"""
LATS (Language Agent Tree Search) Implementation

LATS combines language agent reasoning with tree search over trajectories.
Instead of a single path, the agent explores multiple possible action sequences,
evaluating and pruning to find the optimal solution.

Key Pattern:
    State → Generate multiple actions → Evaluate branches → Prune weak paths → Best path

Real LLM Integration: Uses Claude API to generate reasoning trajectories and evaluate them.

Requirements:
    pip install anthropic

Setup:
    1. Get your API key from https://console.anthropic.com
    2. Export: export ANTHROPIC_API_KEY='your-key'
    3. Run: python lats_agent.py
"""

from typing import List, Dict, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import os
from anthropic import Anthropic

# Initialize Anthropic client
client = Anthropic()


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
            response = client.messages.create(
                model=self.model,
                max_tokens=800,
                system="You are exploring multiple solution paths for a complex problem. Generate diverse, thoughtful strategies.",
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text

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
            response = client.messages.create(
                model=self.model,
                max_tokens=50,
                system="You are evaluating problem-solving progress. Be analytical and fair.",
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()

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

    def print_search_tree(self, node: SearchNode = None, indent: str = ""):
        """Print the search tree structure"""
        if node is None:
            node = self.root

        print(f"{indent}├─ {node.state} (score: {node.value:.2f}, depth: {node.depth})")

        for i, child in enumerate(node.children):
            is_last = i == len(node.children) - 1
            next_indent = indent + ("   " if is_last else "│  ")
            self.print_search_tree(child, next_indent)

    def print_summary(self):
        """Print summary of the search process"""
        print(f"\n{'='*60}")
        print(f"LATS Agent Summary")
        print(f"{'='*60}")
        print(f"Explored states: {len(self.explored_states)}")
        print(f"Beam width: {self.beam_width}")
        print(f"Best path found: {' → '.join(self.best_path) if self.best_path else 'None'}")


def main():
    """Demo of LATS agent"""

    # Example 1: Mathematical problem solving with multiple paths
    print("\n" + "="*60)
    print("Example 1: Math Problem with Tree Search")
    print("="*60)

    agent1 = LATSAgent("LATS-Math", beam_width=3)
    path1, score1 = agent1.solve(
        problem="How to calculate 25 * 4 + 10?",
        goal_state="Find the numerical solution"
    )
    agent1.print_summary()

    print(f"\nFinal Score: {score1:.2f}")

    # Example 2: Logic problem with tree search
    print("\n" + "="*60)
    print("Example 2: Logic Problem with Explored Paths")
    print("="*60)

    agent2 = LATSAgent("LATS-Logic", beam_width=3)
    path2, score2 = agent2.solve(
        problem="If A is larger than B, and B is larger than C, what is the order?",
        goal_state="Determine the correct ordering"
    )

    print(f"\nFinal Score: {score2:.2f}")
    print(f"\nSearch Tree Structure:")
    agent2.print_search_tree()

    # Example 3: Complex reasoning with larger beam
    print("\n" + "="*60)
    print("Example 3: Complex Reasoning with Beam Search")
    print("="*60)

    agent3 = LATSAgent("LATS-Complex", beam_width=3)
    path3, score3 = agent3.solve(
        problem="What are effective strategies for debugging software?",
        goal_state="Identify debugging strategies and best practices"
    )

    agent3.print_summary()


if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your API key: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)

    main()
