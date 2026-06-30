"""
Multi-Agent Framework Base Classes

This module provides the foundation for multi-agent systems.
It defines the basic interfaces and communication patterns used by:
- Dylan (Dynamic hierarchical systems)
- AGentverse (Cooperative environments)
- MetaGPT (Role-based software engineering)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


class AgentRole(Enum):
    """Roles an agent can take in a multi-agent system"""
    MANAGER = "manager"
    WORKER = "worker"
    SPECIALIST = "specialist"
    COMMUNICATOR = "communicator"
    EVALUATOR = "evaluator"


class MessageType(Enum):
    """Types of messages agents can send"""
    REQUEST = "request"
    RESPONSE = "response"
    FEEDBACK = "feedback"
    QUERY = "query"
    BROADCAST = "broadcast"
    COORDINATION = "coordination"


@dataclass
class Message:
    """A message between agents"""
    sender_id: str
    recipient_id: str
    message_type: MessageType
    content: str
    timestamp: int = 0
    priority: int = 1  # Higher = more important


@dataclass
class TaskAllocation:
    """Allocation of a task to an agent"""
    task_id: str
    task_description: str
    assigned_agent: str
    status: str = "pending"  # pending, in_progress, completed
    result: Optional[str] = None


class BaseAgent(ABC):
    """
    Base class for all agents in a multi-agent system

    Provides common functionality for:
    - Communication with other agents
    - Task execution
    - State management
    """

    def __init__(self, agent_id: str, role: AgentRole, capabilities: List[str]):
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities
        self.inbox: List[Message] = []
        self.outbox: List[Message] = []
        self.knowledge_base: Dict[str, Any] = {}
        self.tasks_completed: int = 0

    @abstractmethod
    def process_message(self, message: Message) -> Optional[Message]:
        """Process an incoming message and generate a response"""
        pass

    @abstractmethod
    def execute_task(self, task: TaskAllocation) -> str:
        """Execute an assigned task"""
        pass

    def send_message(self, recipient_id: str, content: str, msg_type: MessageType):
        """Send a message to another agent"""
        message = Message(
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=msg_type,
            content=content
        )
        self.outbox.append(message)
        return message

    def receive_message(self, message: Message):
        """Receive a message from another agent"""
        self.inbox.append(message)

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "capabilities": self.capabilities,
            "tasks_completed": self.tasks_completed,
            "inbox_size": len(self.inbox),
            "outbox_size": len(self.outbox)
        }


class MultiAgentEnvironment(ABC):
    """
    Base class for multi-agent environments

    Manages:
    - Agent registration
    - Message routing
    - Task distribution
    - Coordination
    """

    def __init__(self, name: str):
        self.name = name
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[TaskAllocation] = []
        self.completed_tasks: List[TaskAllocation] = []
        self.message_log: List[Message] = []
        self.step_count = 0

    def register_agent(self, agent: BaseAgent):
        """Register an agent in the environment"""
        self.agents[agent.agent_id] = agent
        print(f"✓ Registered agent: {agent.agent_id} ({agent.role.value})")

    def add_task(self, task: TaskAllocation):
        """Add a task to the queue"""
        self.task_queue.append(task)

    def route_message(self, message: Message):
        """Route a message from one agent to another"""
        if message.recipient_id in self.agents:
            self.agents[message.recipient_id].receive_message(message)
            self.message_log.append(message)

    def broadcast_message(self, sender_id: str, content: str):
        """Send a message to all agents"""
        message = Message(
            sender_id=sender_id,
            recipient_id="all",
            message_type=MessageType.BROADCAST,
            content=content
        )

        for agent_id, agent in self.agents.items():
            if agent_id != sender_id:
                agent.receive_message(message)

        self.message_log.append(message)

    @abstractmethod
    def step(self):
        """Execute one step of the environment"""
        pass

    @abstractmethod
    def allocate_tasks(self):
        """Allocate tasks to agents"""
        pass

    def get_environment_status(self) -> Dict[str, Any]:
        """Get current environment status"""
        return {
            "name": self.name,
            "num_agents": len(self.agents),
            "agents": [a.get_status() for a in self.agents.values()],
            "pending_tasks": len([t for t in self.task_queue if t.status == "pending"]),
            "completed_tasks": len(self.completed_tasks),
            "total_messages": len(self.message_log),
            "steps_executed": self.step_count
        }

    def print_status(self):
        """Print environment status"""
        status = self.get_environment_status()
        print(f"\n{'='*60}")
        print(f"Environment: {status['name']}")
        print(f"{'='*60}")
        print(f"Agents: {status['num_agents']}")
        print(f"Pending tasks: {status['pending_tasks']}")
        print(f"Completed tasks: {status['completed_tasks']}")
        print(f"Messages exchanged: {status['total_messages']}")
        print(f"Steps executed: {status['steps_executed']}")

        print(f"\nAgent Status:")
        for agent_status in status['agents']:
            print(f"  - {agent_status['agent_id']} ({agent_status['role']})")
            print(f"    Capabilities: {', '.join(agent_status['capabilities'])}")
            print(f"    Tasks completed: {agent_status['tasks_completed']}")


class CoordinationProtocol(ABC):
    """
    Abstract coordination protocol for multi-agent systems

    Different frameworks implement different coordination strategies:
    - Dylan: Hierarchical with dynamic leader
    - AGentverse: Peer-to-peer coordination
    - MetaGPT: Role-based orchestration
    """

    @abstractmethod
    def coordinate(self, environment: MultiAgentEnvironment) -> bool:
        """Execute coordination logic. Returns True if coordination successful."""
        pass

    @abstractmethod
    def resolve_conflicts(self, environment: MultiAgentEnvironment):
        """Resolve conflicts between agents"""
        pass


# Utility functions

def find_agent_by_capability(agents: Dict[str, BaseAgent], capability: str) -> Optional[BaseAgent]:
    """Find an agent with a specific capability"""
    for agent in agents.values():
        if capability in agent.capabilities:
            return agent
    return None


def find_agents_by_role(agents: Dict[str, BaseAgent], role: AgentRole) -> List[BaseAgent]:
    """Find all agents with a specific role"""
    return [agent for agent in agents.values() if agent.role == role]


def get_capable_agents(agents: Dict[str, BaseAgent], required_capabilities: List[str]) -> List[BaseAgent]:
    """Get agents that have all required capabilities"""
    capable = []
    for agent in agents.values():
        if all(cap in agent.capabilities for cap in required_capabilities):
            capable.append(agent)
    return capable
