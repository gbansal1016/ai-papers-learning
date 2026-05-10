"""
Dylan Framework Implementation

Dylan: Dynamic hierarchical multi-agent system

Key Features:
- Hierarchical task decomposition using Claude reasoning
- Dynamic leadership (agents can take/relinquish leadership)
- Manager-Worker relationships
- Adaptive task allocation based on agent capabilities

Architecture:
    Manager (top-level coordinator)
      ├── Worker 1 (handles subtask A)
      ├── Worker 2 (handles subtask B)
      └── Worker 3 (handles subtask C)

The manager uses Claude to decompose complex tasks and allocates them to workers.
Workers can also act as managers for sub-teams.

Real LLM Integration: Manager uses Claude API for intelligent task decomposition.

Requirements:
    pip install anthropic

Setup:
    1. Get your API key from https://console.anthropic.com
    2. Export: export ANTHROPIC_API_KEY='your-key'
    3. Run: python dylan_framework.py
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import os
from anthropic import Anthropic
from multi_agent_framework import (
    BaseAgent, MultiAgentEnvironment, CoordinationProtocol,
    AgentRole, MessageType, TaskAllocation, Message,
    find_agents_by_role
)

# Initialize Anthropic client
client = Anthropic()


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
            # Decompose task
            subtasks = self._decompose_task(task)
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

    def _decompose_task(self, task: TaskAllocation) -> List[TaskAllocation]:
        """
        Decompose a task into subtasks using Claude reasoning

        Claude intelligently breaks down the complex task into logical subtasks
        that can be assigned to different workers.
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

Be concise and practical."""

        subtasks = []

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=500,
                system="You are an expert task decomposition manager. Break tasks into logical, parallel-able subtasks.",
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text

            # Parse subtasks from response
            subtask_blocks = response_text.split("SUBTASK:")[1:]

            for i, block in enumerate(subtask_blocks):
                lines = block.strip().split("\n")
                subtask_name = lines[0].strip() if lines else f"Subtask {i+1}"
                subtask_desc = ""

                for line in lines[1:]:
                    if line.startswith("DESCRIPTION:"):
                        subtask_desc = line.replace("DESCRIPTION:", "").strip()
                        break

                if not subtask_desc:
                    subtask_desc = f"{subtask_name}: {task.task_description}"

                subtask = TaskAllocation(
                    task_id=f"{task.task_id}_sub{i}",
                    task_description=subtask_desc,
                    assigned_agent=""
                )
                subtasks.append(subtask)

        except Exception as e:
            print(f"Error decomposing task with Claude: {e}")
            # Fallback to simple decomposition
            subtask_names = ["analyze", "process", "verify"]
            for i, subname in enumerate(subtask_names):
                subtask = TaskAllocation(
                    task_id=f"{task.task_id}_sub{i}",
                    task_description=f"{subname}: {task.task_description}",
                    assigned_agent=""
                )
                subtasks.append(subtask)

        return subtasks

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


# Demo
def main():
    """Demo of Dylan framework with Claude-based task decomposition"""

    print("="*60)
    print("Dylan Framework Demo - Hierarchical Task Decomposition")
    print("="*60)

    # Create environment
    env = DylanEnvironment("DylanDemo")

    # Create manager
    manager = DylanAgent("manager_1", AgentRole.MANAGER, ["decomposition", "coordination", "allocation"])
    env.register_agent(manager)

    # Create workers
    for i in range(3):
        worker = DylanAgent(f"worker_{i+1}", AgentRole.WORKER, ["execution", "reporting"])
        env.register_agent(worker)

    # Setup hierarchy
    env.setup_hierarchy("manager_1")

    # Add tasks
    tasks = [
        TaskAllocation(
            task_id="task_1",
            task_description="Process customer data and generate report",
            assigned_agent=""
        ),
        TaskAllocation(
            task_id="task_2",
            task_description="Analyze market trends and create strategic summary",
            assigned_agent=""
        )
    ]

    for task in tasks:
        env.add_task(task)

    # Run
    env.run(num_steps=10)


if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your API key: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)

    main()
