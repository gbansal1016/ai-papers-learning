"""
Dylan Framework Implementation

Dylan: Dynamic hierarchical multi-agent system

Key Features:
- Hierarchical task decomposition using Claude/Ollama reasoning
- Dynamic leadership (agents can take/relinquish leadership)
- Manager-Worker relationships
- Adaptive task allocation based on agent capabilities

Architecture:
    Manager (top-level coordinator)
      ├── Worker 1 (handles subtask A)
      ├── Worker 2 (handles subtask B)
      └── Worker 3 (handles subtask C)

The manager uses Claude or Ollama to decompose complex tasks and allocates them to workers.
Workers can also act as managers for sub-teams.

Real LLM Integration: Manager uses Claude API OR Local Ollama for intelligent task decomposition.

Requirements:
    Option 1 (Anthropic): pip install anthropic
    Option 2 (Local): pip install requests

Setup:
    OPTION 1: Use Anthropic API (Claude)
        1. Get your API key from https://console.anthropic.com
        2. Export: export ANTHROPIC_API_KEY='your-key'
        3. Run: python dylan_framework.py

    OPTION 2: Use Local Model (Ollama - NO API KEY NEEDED)
        1. Install Ollama: https://ollama.ai
        2. Run: ollama pull mistral && ollama serve
        3. Run: python dylan_framework.py
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import os
import requests
from anthropic import Anthropic
from multi_agent_framework import (
    BaseAgent, MultiAgentEnvironment, CoordinationProtocol,
    AgentRole, MessageType, TaskAllocation, Message,
    find_agents_by_role
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


@dataclass
class DynamicHierarchy:
    """Represents the dynamic hierarchy in Dylan"""
    leader_id: str
    subordinates: List[str] = field(default_factory=list)
    task_assignments: Dict[str, str] = field(default_factory=dict)  # task_id -> agent_id


class DylanAgent(BaseAgent):
    """Agent in the Dylan framework"""

    def __init__(self, agent_id: str, role: AgentRole, capabilities: List[str]):
        super().__init__(agent_id, role, capabilities)
        self.managed_tasks: List[TaskAllocation] = []
        self.is_leader = (role == AgentRole.MANAGER)

    def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming messages"""
        if message.message_type == MessageType.REQUEST:
            return self._handle_request(message)
        elif message.message_type == MessageType.COORDINATION:
            return self._handle_coordination(message)
        return None

    def _handle_request(self, message: Message) -> Optional[Message]:
        """Handle task request from manager"""
        if "execute" in message.content.lower():
            return Message(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type=MessageType.RESPONSE,
                content=f"Ready to execute task with capabilities: {', '.join(self.capabilities)}"
            )
        return None

    def _handle_coordination(self, message: Message) -> Optional[Message]:
        """Handle coordination message"""
        return Message(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content="Acknowledged coordination request"
        )

    def execute_task(self, task: TaskAllocation) -> str:
        """Execute an assigned task"""
        self.managed_tasks.append(task)
        task.status = "in_progress"

        # Simulate task execution
        result = f"[{self.agent_id}] Executed: {task.task_description}"
        task.result = result
        task.status = "completed"
        self.tasks_completed += 1

        return result


class DylanCoordinator(CoordinationProtocol):
    """Coordination logic for Dylan framework with Claude-based task decomposition"""

    def __init__(self, manager_agent_id: str):
        self.manager_id = manager_agent_id
        self.hierarchy = DynamicHierarchy(leader_id=manager_agent_id)
        self.model = "claude-3-5-sonnet-20241022"

    def coordinate(self, environment: 'DylanEnvironment') -> bool:
        """
        Execute Dylan coordination:
        1. Manager receives task
        2. Manager decomposes into subtasks
        3. Manager allocates to workers
        4. Workers execute and report back
        """
        print(f"\n[Dylan] Manager '{self.manager_id}' coordinating...")

        # Get pending tasks
        pending = [t for t in environment.task_queue if t.status == "pending"]
        if not pending:
            return False

        for task in pending:
            # Decompose task (returns subtasks and capabilities)
            subtasks, worker_caps = self._decompose_task(task)
            print(f"[Dylan] Decomposed task into {len(subtasks)} subtasks")

            # Allocate to workers
            for subtask, worker_id in zip(subtasks, self.hierarchy.subordinates):
                worker = environment.agents.get(worker_id)
                if worker:
                    print(f"[Dylan] Allocating subtask to worker '{worker_id}'")
                    worker.execute_task(subtask)
                    self.hierarchy.task_assignments[subtask.task_id] = worker_id

            task.status = "completed"
            environment.completed_tasks.append(task)

        return True

    def _decompose_task(self, task: TaskAllocation) -> tuple[List[TaskAllocation], List[List[str]]]:
        """
        Decompose a task into subtasks using Claude reasoning

        Claude intelligently breaks down the complex task into logical subtasks
        that can be assigned to different workers.

        Returns: (subtasks, worker_capabilities)
        - subtasks: List of TaskAllocation objects
        - worker_capabilities: List of capability lists for each subtask
        """
        prompt = f"""You are a task manager decomposing a complex task into subtasks.

Task: {task.task_description}

Break this down into 3-4 logical subtasks that:
- Are independent and can be worked on in parallel
- Each have a clear, specific focus
- Together complete the original task

Format each subtask as:
SUBTASK: [name]
DESCRIPTION: [what needs to be done]
CAPABILITIES: [comma-separated skills needed, e.g., "analysis, data-processing, report-writing"]

Be concise and practical."""

        subtasks = []
        worker_capabilities = []

        try:
            if USE_LOCAL_MODEL:
                response = client.messages_create(
                    system="You are an expert task decomposition manager. Break tasks into logical, parallel-able subtasks. For each subtask, list the specific skills/capabilities needed.",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
            else:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    system="You are an expert task decomposition manager. Break tasks into logical, parallel-able subtasks. For each subtask, list the specific skills/capabilities needed.",
                    messages=[{"role": "user", "content": prompt}]
                )

            response_text = response.content[0].text
            print(f"\n[🤖 MODEL DECOMPOSITION - Task Breakdown & Capabilities]\n{response_text}\n")

            # Parse subtasks from response
            subtask_blocks = response_text.split("SUBTASK:")[1:]

            for i, block in enumerate(subtask_blocks):
                lines = block.strip().split("\n")
                subtask_name = lines[0].strip() if lines else f"Subtask {i+1}"
                subtask_desc = ""
                capabilities = ["execution", "reporting"]  # Default fallback

                for line in lines[1:]:
                    if line.startswith("DESCRIPTION:"):
                        subtask_desc = line.replace("DESCRIPTION:", "").strip()
                    elif line.startswith("CAPABILITIES:"):
                        caps_text = line.replace("CAPABILITIES:", "").strip()
                        # Parse comma-separated capabilities
                        capabilities = [cap.strip().lower() for cap in caps_text.split(",")]

                if not subtask_desc:
                    subtask_desc = f"{subtask_name}: {task.task_description}"

                subtask = TaskAllocation(
                    task_id=f"{task.task_id}_sub{i}",
                    task_description=subtask_desc,
                    assigned_agent=""
                )
                subtasks.append(subtask)
                worker_capabilities.append(capabilities)

        except Exception as e:
            print(f"Error decomposing task with Claude: {e}")
            # Fallback to simple decomposition
            subtask_names = ["analyze", "process", "verify"]
            fallback_caps = [
                ["data-analysis", "research"],
                ["data-processing", "validation"],
                ["quality-assurance", "verification"]
            ]
            for i, subname in enumerate(subtask_names):
                subtask = TaskAllocation(
                    task_id=f"{task.task_id}_sub{i}",
                    task_description=f"{subname}: {task.task_description}",
                    assigned_agent=""
                )
                subtasks.append(subtask)
                worker_capabilities.append(fallback_caps[i] if i < len(fallback_caps) else ["execution", "reporting"])

        return subtasks, worker_capabilities

    def resolve_conflicts(self, environment: 'DylanEnvironment'):
        """Resolve conflicts through hierarchical authority"""
        print("[Dylan] Resolving conflicts using hierarchical authority...")
        # In a real system, conflicts would be resolved by the manager


class DylanEnvironment(MultiAgentEnvironment):
    """Environment for Dylan multi-agent system"""

    def __init__(self, name: str = "DylanEnvironment"):
        super().__init__(name)
        self.coordinator: Optional[DylanCoordinator] = None

    def setup_hierarchy(self, manager_id: str):
        """Setup the hierarchical structure"""
        self.coordinator = DylanCoordinator(manager_id)

        # Assign workers to manager
        worker_agents = find_agents_by_role(self.agents, AgentRole.WORKER)
        self.coordinator.hierarchy.subordinates = [a.agent_id for a in worker_agents]

        print(f"[Dylan] Setup hierarchy with manager '{manager_id}' and {len(self.coordinator.hierarchy.subordinates)} workers")

    def step(self):
        """Execute one step of coordination"""
        self.step_count += 1

        # Process outgoing messages
        for agent in self.agents.values():
            for message in agent.outbox:
                self.route_message(message)
            agent.outbox.clear()

        # Allocate tasks
        self.allocate_tasks()

        # Coordinate
        if self.coordinator:
            self.coordinator.coordinate(self)

    def allocate_tasks(self):
        """Allocate tasks using Dylan's hierarchical approach"""
        if self.coordinator:
            manager = self.agents.get(self.coordinator.manager_id)
            if manager:
                for task in [t for t in self.task_queue if t.status == "pending"]:
                    # Manager takes task
                    print(f"Manager received task: {task.task_description}")
                    manager.send_message(
                        self.coordinator.manager_id,
                        f"Allocate task: {task.task_description}",
                        MessageType.COORDINATION
                    )

    def run(self, num_steps: int = 5):
        """Run the environment for a number of steps"""
        print(f"\n{'='*60}")
        print(f"Running Dylan Environment: {self.name}")
        print(f"{'='*60}\n")

        for _ in range(num_steps):
            self.step()
            if not self.task_queue:
                break

        self.print_status()


def main():
    """Interactive Dylan Framework - Hierarchical Task Decomposition"""

    print("\n" + "="*70)
    print("👥 DYLAN FRAMEWORK - Hierarchical Task Decomposition 👥".center(70))
    print("="*70)
    print("\nManager decomposes tasks → Workers execute subtasks in parallel!")
    print("Model: Mistral (via Ollama) | Architecture: Manager + Workers")
    print("="*70)

    while True:
        print("\n" + "-"*70)
        print("TASK SETUP")
        print("-"*70)

        # Get task description from user
        print("\nEnter a task to decompose (manager will break it into subtasks):")
        print("Examples:")
        print("  - Process customer data and generate report")
        print("  - Analyze market trends and create strategic summary")
        print("  - Design and implement a new feature for our product")
        print("  - Design a mobile app architecture")
        print("  - Build a e-commerce recommendation system")
        print("  - Create a marketing campaign for a new product")
        
        print("-"*70)

        task_desc = input("Task: ").strip()

        if not task_desc:
            print("❌ Task cannot be empty. Please try again.")
            continue

        # Get number of workers
        print("\nHow many workers should help? (default: 3, range: 1-5)")
        print("-"*70)

        workers_input = input("Number of workers (press Enter for 3): ").strip()

        num_workers = 3
        if workers_input:
            try:
                num_workers = int(workers_input)
                if num_workers < 1 or num_workers > 5:
                    print("⚠️  Must be 1-5. Using default: 3")
                    num_workers = 3
            except ValueError:
                print("⚠️  Invalid input. Using default: 3")
                num_workers = 3

        # Get simulation steps
        print("\nHow many simulation steps? (default: 10, range: 5-20)")
        print("(More steps = more detailed execution)")
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

        # Execute task decomposition
        print(f"\n{'='*70}")
        print(f"👥 EXECUTING DYLAN FRAMEWORK")
        print(f"{'='*70}")
        print(f"Manager: 1 | Workers: {num_workers} | Steps: {num_steps}\n")

        try:
            # Create environment and manager first
            env = DylanEnvironment("DylanInteractive")
            manager = DylanAgent("manager_1", AgentRole.MANAGER, ["decomposition", "coordination", "allocation"])
            env.register_agent(manager)

            # Create coordinator to decompose tasks
            coordinator = DylanCoordinator("manager_1")

            # Decompose the task to get capabilities
            temp_task = TaskAllocation(
                task_id="temp_task",
                task_description=task_desc,
                assigned_agent=""
            )
            subtasks, worker_caps_list = coordinator._decompose_task(temp_task)

            # Show matched capabilities
            print(f"[👥 MATCHED CAPABILITIES]")
            for i, (subtask, caps) in enumerate(zip(subtasks, worker_caps_list)):
                print(f"Subtask {i+1}: {subtask.task_description[:50]}...")
                print(f"  Required capabilities: {', '.join(caps)}\n")

            # Create workers with specific capabilities from decomposition
            print(f"[👥 CREATING WORKERS WITH MATCHED CAPABILITIES]\n")
            for i in range(min(num_workers, len(subtasks))):
                # Assign the capabilities extracted from decomposition
                worker_caps = worker_caps_list[i] if i < len(worker_caps_list) else ["execution", "reporting"]
                worker = DylanAgent(f"worker_{i+1}", AgentRole.WORKER, worker_caps)
                print(f"worker_{i+1}: {', '.join(worker_caps)}")
                env.register_agent(worker)

            # If more workers than subtasks, add generic workers
            for i in range(len(subtasks), num_workers):
                worker = DylanAgent(f"worker_{i+1}", AgentRole.WORKER, ["execution", "support"])
                print(f"worker_{i+1}: execution, support (backup)")
                env.register_agent(worker)

            print()

            # Setup hierarchy
            env.setup_hierarchy("manager_1")

            # Add user task
            task = TaskAllocation(
                task_id="user_task",
                task_description=task_desc,
                assigned_agent=""
            )
            env.add_task(task)

            # Run simulation
            env.run(num_steps=num_steps)

            print(f"\n{'='*70}")
            print(f"✅ TASK DECOMPOSITION COMPLETE")
            print(f"{'='*70}")
            print(f"Manager decomposed task into subtasks")
            print(f"Workers executed {num_workers} subtasks in parallel")
            print(f"Simulation ran for {num_steps} steps")

        except Exception as e:
            print(f"\n❌ Error during execution: {e}")
            import traceback
            traceback.print_exc()
            continue

        # Ask if user wants to try another task
        print(f"\n{'='*70}")
        again = input("Decompose another task? (yes/no): ").strip().lower()
        if again not in ["yes", "y"]:
            print("\n✨ Thank you for using Dylan Framework! Goodbye!\n")
            break


if __name__ == "__main__":
    # Check if API key is set (only needed for Anthropic API mode)
    if not USE_LOCAL_MODEL and not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your API key: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)

    main()
