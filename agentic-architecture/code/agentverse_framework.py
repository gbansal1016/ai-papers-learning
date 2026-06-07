"""
AGentverse Framework Implementation

AGentverse: Cooperative multi-agent environment for collaborative problem-solving

Key Features:
- Peer-to-peer agent communication with Claude/Ollama reasoning
- Consensus-based decision making
- Collaborative execution
- Shared knowledge base

Architecture:
    Agent A ←→ Agent B ←→ Agent C
    ↓           ↓          ↓
    Shared Knowledge Base & Communication Bus

Each agent is equal; they negotiate and collaborate to solve problems.
Agents use Claude or Ollama to discuss proposals and make voting decisions.
No single leader; decisions are made through discussion and consensus.

Real LLM Integration: Agents use Claude API OR Local Ollama for informed discussions and voting.

Requirements:
    Option 1 (Anthropic): pip install anthropic
    Option 2 (Local): pip install requests

Setup:
    OPTION 1: Use Anthropic API (Claude)
        1. Get your API key from https://console.anthropic.com
        2. Export: export ANTHROPIC_API_KEY='your-key'
        3. Run: python agenverse_framework.py

    OPTION 2: Use Local Model (Ollama - NO API KEY NEEDED)
        1. Install Ollama: https://ollama.ai
        2. Run: ollama pull mistral && ollama serve
        3. Run: python agenverse_framework.py
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum
import os
import requests
from anthropic import Anthropic
from multi_agent_framework import (
    BaseAgent, MultiAgentEnvironment, CoordinationProtocol,
    AgentRole, MessageType, TaskAllocation, Message
)

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


class ConsensusState(Enum):
    """States in consensus decision making"""
    PROPOSED = "proposed"
    DISCUSSING = "discussing"
    VOTING = "voting"
    AGREED = "agreed"
    DISAGREED = "disagreed"


@dataclass
class ConsensusProcess:
    """Represents an ongoing consensus decision"""
    proposal_id: str
    proposer_id: str
    proposal: str
    state: ConsensusState = ConsensusState.PROPOSED
    votes: Dict[str, bool] = field(default_factory=dict)  # agent_id -> vote (True/False)
    discussion_log: List[str] = field(default_factory=list)
    agreement_threshold: float = 0.66  # Need 66% agreement

    def is_agreed(self) -> bool:
        """Check if consensus is reached"""
        if not self.votes:
            return False
        positive_votes = sum(1 for v in self.votes.values() if v)
        return positive_votes / len(self.votes) >= self.agreement_threshold


class AGentverseAgent(BaseAgent):
    """Agent in the AGentverse cooperative framework with Claude reasoning"""

    def __init__(self, agent_id: str, capabilities: List[str]):
        super().__init__(agent_id, AgentRole.SPECIALIST, capabilities)
        self.agreed_proposals: List[str] = []
        self.discussions: Dict[str, List[str]] = field(default_factory=dict)
        self.knowledge: Dict[str, any] = {}
        self.model = "claude-3-5-sonnet-20241022"

    def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming messages"""
        if message.message_type == MessageType.BROADCAST:
            return self._handle_broadcast(message)
        elif message.message_type == MessageType.COORDINATION:
            return self._handle_coordination(message)
        elif message.message_type == MessageType.QUERY:
            return self._handle_query(message)
        return None

    def _handle_broadcast(self, message: Message) -> Optional[Message]:
        """Handle broadcast message (proposal or discussion)"""
        response_content = f"Agent {self.agent_id} acknowledges: {message.content[:50]}..."
        return Message(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content=response_content
        )

    def _handle_coordination(self, message: Message) -> Optional[Message]:
        """Handle coordination message"""
        if "vote" in message.content.lower():
            # Simulate voting based on message content
            vote = "agree" in message.content.lower()
            return Message(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type=MessageType.RESPONSE,
                content=f"Vote: {'YES' if vote else 'NO'}"
            )
        return None

    def _handle_query(self, message: Message) -> Optional[Message]:
        """Handle knowledge query"""
        key = message.content.lower()
        value = self.knowledge.get(key, f"No knowledge about {key}")
        return Message(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content=value
        )

    def execute_task(self, task: TaskAllocation) -> str:
        """Execute a collaboratively decided task"""
        task.status = "in_progress"
        result = f"[{self.agent_id}] Executed: {task.task_description}"
        task.result = result
        task.status = "completed"
        self.tasks_completed += 1
        return result

    def vote_on_proposal(self, proposal: str) -> bool:
        """Vote on a proposal using Claude reasoning based on capabilities and expertise"""
        prompt = f"""You are agent '{self.agent_id}' with expertise in: {', '.join(self.capabilities)}

Proposal: {proposal}

Based on your expertise and knowledge, should you support this proposal?
Consider:
- Does it align with your capabilities?
- Is it feasible and well-reasoned?
- Will it contribute to the team goal?

Respond with ONLY 'YES' or 'NO'."""

        try:
            if USE_LOCAL_MODEL:
                response = client.messages_create(
                    system="You are a thoughtful team member evaluating proposals. Be balanced and analytical.",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=20
                )
            else:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=20,
                    system="You are a thoughtful team member evaluating proposals. Be balanced and analytical.",
                    messages=[{"role": "user", "content": prompt}]
                )

            response_text = response.content[0].text.strip().upper()
            print(f"\n[🤖 MODEL VOTE - {self.agent_id}]\n{response_text}\n")
            return "YES" in response_text

        except Exception as e:
            print(f"Error voting on proposal: {e}")
            # Fallback: support if proposal mentions our capabilities
            for cap in self.capabilities:
                if cap.lower() in proposal.lower():
                    return True
            return False


class AGentverseCoordinator(CoordinationProtocol):
    """Coordination for AGentverse peer-to-peer collaboration with Claude facilitation"""

    def __init__(self):
        self.consensus_processes: Dict[str, ConsensusProcess] = {}
        self.consensus_counter = 0
        self.model = "claude-3-5-sonnet-20241022"

    def coordinate(self, environment: 'AGentverseEnvironment') -> bool:
        """
        Execute AGentverse coordination:
        1. Propose task solutions
        2. Discuss proposals (all agents participate)
        3. Vote on proposals
        4. Execute agreed solutions
        """
        print(f"\n[AGentverse] Running peer-to-peer coordination...")

        # Get pending tasks
        pending = [t for t in environment.task_queue if t.status == "pending"]
        if not pending:
            return False

        for task in pending:
            print(f"[AGentverse] Processing task: {task.task_description}")

            # Create consensus process
            proposal = f"Solve: {task.task_description}"
            consensus = self._create_consensus(proposal)

            # All agents discuss
            self._conduct_discussion(environment, consensus)

            # All agents vote
            self._conduct_voting(environment, consensus)

            # Execute if consensus reached
            if consensus.is_agreed():
                print(f"[AGentverse] ✓ Consensus reached ({consensus.votes})")
                for agent in environment.agents.values():
                    agent.execute_task(task)
                task.status = "completed"
            else:
                print(f"[AGentverse] ✗ No consensus ({consensus.votes})")
                task.status = "failed"

            environment.completed_tasks.append(task)

        return True

    def _create_consensus(self, proposal: str) -> ConsensusProcess:
        """Create a new consensus process"""
        self.consensus_counter += 1
        consensus = ConsensusProcess(
            proposal_id=f"consensus_{self.consensus_counter}",
            proposer_id="system",
            proposal=proposal,
            state=ConsensusState.DISCUSSING
        )
        self.consensus_processes[consensus.proposal_id] = consensus
        return consensus

    def _conduct_discussion(self, environment: 'AGentverseEnvironment', consensus: ConsensusProcess):
        """Conduct discussion phase using Claude for thoughtful analysis"""
        print(f"[AGentverse] Discussion phase for: {consensus.proposal}")

        for agent in environment.agents.values():
            if isinstance(agent, AGentverseAgent):
                # Use Claude to generate thoughtful input from this agent's perspective
                discussion_prompt = f"""You are agent '{agent.agent_id}' with expertise in: {', '.join(agent.capabilities)}

Team Proposal: {consensus.proposal}

Based on your expertise, what insights or concerns do you have about this proposal?
Be concise (1-2 sentences)."""

                try:
                    if USE_LOCAL_MODEL:
                        response = client.messages_create(
                            system="You are a thoughtful team member contributing to group discussion. Provide balanced, constructive input.",
                            messages=[{"role": "user", "content": discussion_prompt}],
                            max_tokens=100
                        )
                    else:
                        response = client.messages.create(
                            model=self.model,
                            max_tokens=100,
                            system="You are a thoughtful team member contributing to group discussion. Provide balanced, constructive input.",
                            messages=[{"role": "user", "content": discussion_prompt}]
                        )
                    comment = response.content[0].text.strip()
                    print(f"\n[🤖 MODEL DISCUSSION - {agent.agent_id}]\n{comment}\n")
                except Exception as e:
                    comment = f"Agent {agent.agent_id} analysis: {', '.join(agent.capabilities)}"

                consensus.discussion_log.append(comment)
                print(f"  - {agent.agent_id}: {comment}")

        consensus.state = ConsensusState.VOTING

    def _conduct_voting(self, environment: 'AGentverseEnvironment', consensus: ConsensusProcess):
        """Conduct voting phase (all agents vote)"""
        print(f"[AGentverse] Voting phase...")

        for agent in environment.agents.values():
            if isinstance(agent, AGentverseAgent):
                vote = agent.vote_on_proposal(consensus.proposal)
                consensus.votes[agent.agent_id] = vote
                print(f"  - {agent.agent_id}: {'✓ YES' if vote else '✗ NO'}")

    def resolve_conflicts(self, environment: 'AGentverseEnvironment'):
        """Resolve conflicts through discussion and negotiation"""
        print("[AGentverse] Resolving conflicts through peer discussion...")
        # In AGentverse, conflicts are resolved by discussing until consensus


class AGentverseEnvironment(MultiAgentEnvironment):
    """Environment for AGentverse peer-to-peer collaboration"""

    def __init__(self, name: str = "AGentverseEnvironment"):
        super().__init__(name)
        self.coordinator = AGentverseCoordinator()
        self.shared_knowledge: Dict[str, str] = {}

    def step(self):
        """Execute one step of peer-to-peer coordination"""
        self.step_count += 1

        # Process outgoing messages (peer-to-peer)
        for agent in self.agents.values():
            for message in agent.outbox:
                self.route_message(message)
            agent.outbox.clear()

        # Allocate tasks
        self.allocate_tasks()

        # Coordinate (consensus-based)
        self.coordinator.coordinate(self)

    def allocate_tasks(self):
        """Allocate tasks through peer consensus"""
        # Tasks are not pre-assigned; agents negotiate
        for task in [t for t in self.task_queue if t.status == "pending"]:
            # Broadcast to all agents
            self.broadcast_message(
                "system",
                f"New task for consensus: {task.task_description}"
            )

    def add_knowledge(self, key: str, value: str):
        """Add to shared knowledge base"""
        self.shared_knowledge[key] = value

    def get_knowledge(self, key: str) -> Optional[str]:
        """Query shared knowledge base"""
        return self.shared_knowledge.get(key)

    def run(self, num_steps: int = 5):
        """Run the environment for a number of steps"""
        print(f"\n{'='*60}")
        print(f"Running AGentverse Environment: {self.name}")
        print(f"{'='*60}\n")

        for _ in range(num_steps):
            self.step()
            if not self.task_queue:
                break

        self.print_status()


def main():
    """Interactive AGentverse Framework - Peer Consensus Problem Solving"""

    print("\n" + "="*70)
    print("🤝 AGENTVERSE FRAMEWORK - Peer Consensus Collaboration 🤝".center(70))
    print("="*70)
    print("\nEqual agents discuss & vote on proposals through consensus!")
    print("Model: Mistral (via Ollama) | Architecture: Peer-to-Peer")
    print("="*70)

    while True:
        print("\n" + "-"*70)
        print("CONSENSUS PROPOSAL SETUP")
        print("-"*70)

        # Get proposal from user
        print("\nEnter a proposal for the team to discuss and vote on:")
        print("Examples:")
        print("  - Adopt microservices architecture for our application")
        print("  - Migrate to cloud infrastructure next quarter")
        print("  - Implement automated testing across all modules")
        print("-"*70)

        proposal = input("Proposal: ").strip()

        if not proposal:
            print("❌ Proposal cannot be empty. Please try again.")
            continue

        # Get number of agents
        print("\nHow many agents should participate? (default: 3, range: 2-5)")
        print("(More agents = more diverse perspectives)")
        print("-"*70)

        agents_input = input("Number of agents (press Enter for 3): ").strip()

        num_agents = 3
        if agents_input:
            try:
                num_agents = int(agents_input)
                if num_agents < 2 or num_agents > 5:
                    print("⚠️  Must be 2-5. Using default: 3")
                    num_agents = 3
            except ValueError:
                print("⚠️  Invalid input. Using default: 3")
                num_agents = 3

        # Get simulation steps
        print("\nHow many simulation steps? (default: 10, range: 5-20)")
        print("(More steps = more detailed consensus process)")
        print("-"*70)

        steps_input = input("Simulation steps (press Enter for 10): ").strip()

        num_steps = 10
        if steps_input:
            try:
                num_steps = int(steps_input)
                if num_steps < 5 or num_steps > 20:
                    print("⚠️  Must be 5-20. Using default: 10")
                    num_steps = 10
            except ValueError:
                print("⚠️  Invalid input. Using default: 10")
                num_steps = 10

        # Execute consensus
        print(f"\n{'='*70}")
        print(f"🤝 EXECUTING AGENTVERSE CONSENSUS")
        print(f"{'='*70}")
        print(f"Agents: {num_agents} | Proposal: '{proposal[:50]}...' | Steps: {num_steps}\n")

        try:
            # Create environment
            env = AGentverseEnvironment("AGentverseInteractive")

            # Create agents with different capabilities
            agent_configs = [
                ("analyst", ["data-analysis", "research", "reasoning"]),
                ("strategist", ["planning", "strategy", "decision-making"]),
                ("implementer", ["execution", "implementation", "technical"]),
                ("reviewer", ["quality-assurance", "review", "verification"]),
                ("communicator", ["communication", "coordination", "negotiation"])
            ]

            for i in range(min(num_agents, len(agent_configs))):
                agent_id, capabilities = agent_configs[i]
                agent = AGentverseAgent(agent_id, capabilities)
                print(f"Created: {agent_id} with capabilities: {', '.join(capabilities)}")
                env.register_agent(agent)

            # Add shared knowledge
            env.add_knowledge("consensus_method", "democratic voting with discussion")
            env.add_knowledge("decision_framework", "majority-based consensus")

            # Add the proposal as a task
            task = TaskAllocation(
                task_id="proposal_task",
                task_description=proposal,
                assigned_agent=""
            )
            env.add_task(task)

            print()

            # Run consensus process
            env.run(num_steps=num_steps)

            print(f"\n{'='*70}")
            print(f"✅ CONSENSUS PROCESS COMPLETE")
            print(f"{'='*70}")
            print(f"All agents discussed and voted on: '{proposal}'")
            print(f"Simulation executed for {num_steps} coordination steps")

        except Exception as e:
            print(f"\n❌ Error during consensus: {e}")
            import traceback
            traceback.print_exc()
            continue

        # Ask if user wants another proposal
        print(f"\n{'='*70}")
        again = input("Propose another topic for consensus? (yes/no): ").strip().lower()
        if again not in ["yes", "y"]:
            print("\n✨ Thank you for using AGentverse Framework! Goodbye!\n")
            break


if __name__ == "__main__":
    # Check if API key is set (only needed for Anthropic API mode)
    if not USE_LOCAL_MODEL and not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your API key: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)

    main()
