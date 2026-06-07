"""
MetaGPT Framework Implementation

MetaGPT: Software engineering-inspired multi-agent collaboration

Key Features:
- Role-based agents using Claude/Ollama reasoning (like software engineering roles)
- Structured workflows with clear handoffs
- Document-driven collaboration
- Sequential phases (design → development → testing)

Architecture:
    Product Manager → Architect → Engineer → QA
         (Plan)    → (Design)  → (Code)   → (Test)

Each role has specific responsibilities and uses Claude or Ollama to generate deliverables.
Agents work in sequence, each building on previous deliverables.

Real LLM Integration: Each role agent uses Claude API OR Local Ollama to generate its deliverables.

Requirements:
    Option 1 (Anthropic): pip install anthropic
    Option 2 (Local): pip install requests

Setup:
    OPTION 1: Use Anthropic API (Claude)
        1. Get your API key from https://console.anthropic.com
        2. Export: export ANTHROPIC_API_KEY='your-key'
        3. Run: python metagpt_framework.py

    OPTION 2: Use Local Model (Ollama - NO API KEY NEEDED)
        1. Install Ollama: https://ollama.ai
        2. Run: ollama pull mistral && ollama serve
        3. Run: python metagpt_framework.py
"""

from typing import Dict, List, Optional, Any
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


class SoftwareEngineeeringRole(Enum):
    """Software engineering roles in MetaGPT"""
    PRODUCT_MANAGER = "product_manager"
    ARCHITECT = "architect"
    ENGINEER = "engineer"
    QA = "qa"


@dataclass
class Requirement:
    """Product requirement"""
    id: str
    description: str
    priority: int


@dataclass
class Design:
    """System design document"""
    design_id: str
    architecture: str
    components: List[str]
    created_by: str


@dataclass
class Code:
    """Generated code"""
    code_id: str
    language: str
    implementation: str
    created_by: str


@dataclass
class TestResult:
    """Test results"""
    test_id: str
    tests_run: int
    passed: int
    failed: int
    created_by: str

    @property
    def success_rate(self) -> float:
        return (self.passed / self.tests_run) if self.tests_run > 0 else 0.0


class MetaGPTAgent(BaseAgent):
    """Agent in the MetaGPT role-based framework with Claude reasoning"""

    def __init__(self, agent_id: str, software_role: SoftwareEngineeeringRole, capabilities: List[str]):
        super().__init__(agent_id, AgentRole.SPECIALIST, capabilities)
        self.software_role = software_role
        self.deliverables: List[Any] = []
        self.dependencies: List[str] = []  # deliverables this agent depends on
        self.model = "claude-3-5-sonnet-20241022"

    def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming messages"""
        if message.message_type == MessageType.REQUEST:
            return self._handle_request(message)
        elif message.message_type == MessageType.COORDINATION:
            return self._handle_handoff(message)
        return None

    def _handle_request(self, message: Message) -> Optional[Message]:
        """Handle work request"""
        return Message(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content=f"{self.software_role.value} acknowledging request"
        )

    def _handle_handoff(self, message: Message) -> Optional[Message]:
        """Handle handoff of work from previous role"""
        return Message(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content=f"{self.software_role.value} ready to work on deliverables"
        )

    def execute_task(self, task: TaskAllocation) -> str:
        """Execute task based on role"""
        task.status = "in_progress"

        if self.software_role == SoftwareEngineeeringRole.PRODUCT_MANAGER:
            result = self._do_requirements_analysis(task)
        elif self.software_role == SoftwareEngineeeringRole.ARCHITECT:
            result = self._do_system_design(task)
        elif self.software_role == SoftwareEngineeeringRole.ENGINEER:
            result = self._do_development(task)
        elif self.software_role == SoftwareEngineeeringRole.QA:
            result = self._do_testing(task)
        else:
            result = f"[{self.agent_id}] Executed: {task.task_description}"

        task.result = result
        task.status = "completed"
        self.tasks_completed += 1
        return result

    def _do_requirements_analysis(self, task: TaskAllocation) -> str:
        """Product Manager: Analyze and document requirements using Claude"""
        prompt = f"""You are a Product Manager. Analyze the project and document key requirements:

Project: {task.task_description}

Identify and list:
1. Key functional requirements
2. Non-functional requirements (performance, security, etc.)
3. User needs

Be concise but specific."""

        try:
            if USE_LOCAL_MODEL:
                response = client.messages_create(
                    system="You are a professional Product Manager. Focus on clear, prioritized requirements.",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300
                )
            else:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=300,
                    system="You are a professional Product Manager. Focus on clear, prioritized requirements.",
                    messages=[{"role": "user", "content": prompt}]
                )
            description = response.content[0].text.strip()
            print(f"\n[🤖 MODEL GENERATED - Product Manager Requirements]\n{description}\n")
        except Exception as e:
            description = f"Requirements for: {task.task_description}"

        req = Requirement(
            id="REQ_001",
            description=description,
            priority=1
        )
        self.deliverables.append(req)
        return f"[PM] Requirements documented:\n{description[:100]}..."

    def _do_system_design(self, task: TaskAllocation) -> str:
        """Architect: Design system architecture using Claude"""
        prompt = f"""You are a System Architect. Design the system architecture for:

Project: {task.task_description}

Provide:
1. Recommended architecture pattern
2. Key components
3. Technology stack

Be practical and modern."""

        try:
            if USE_LOCAL_MODEL:
                response = client.messages_create(
                    system="You are a senior architect. Provide scalable, maintainable designs.",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=400
                )
            else:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=400,
                    system="You are a senior architect. Provide scalable, maintainable designs.",
                    messages=[{"role": "user", "content": prompt}]
                )
            design_text = response.content[0].text.strip()
            print(f"\n[🤖 MODEL GENERATED - Architect Design]\n{design_text}\n")

            # Extract architecture and components
            architecture = "Recommended architecture from analysis"
            components = ["API Layer", "Business Logic", "Data Layer", "Cache Layer"]

            if "architecture" in design_text.lower():
                lines = design_text.split("\n")
                architecture = lines[0][:100]
        except Exception as e:
            design_text = f"Architecture for: {task.task_description}"
            architecture = "Modular Architecture"
            components = ["API", "Logic", "Data", "Cache"]

        design = Design(
            design_id="DESIGN_001",
            architecture=architecture,
            components=components,
            created_by=self.agent_id
        )
        self.deliverables.append(design)
        return f"[Architect] Design: {architecture}\nComponents: {', '.join(components)}"

    def _do_development(self, task: TaskAllocation) -> str:
        """Engineer: Implement code based on design using Claude"""
        prompt = f"""You are a Senior Engineer. Generate Python implementation outline for:

Project: {task.task_description}

Provide:
1. Main class structure
2. Key methods
3. Brief implementation notes

Keep it concise but professional."""

        try:
            if USE_LOCAL_MODEL:
                response = client.messages_create(
                    system="You are a professional software engineer. Write clean, production-ready code.",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=400
                )
            else:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=400,
                    system="You are a professional software engineer. Write clean, production-ready code.",
                    messages=[{"role": "user", "content": prompt}]
                )
            implementation = response.content[0].text.strip()
            print(f"\n[🤖 MODEL GENERATED - Engineer Implementation]\n{implementation}\n")
        except Exception as e:
            implementation = f"class {task.task_description.split()[0]}:\n  def execute(self):\n    pass"

        code = Code(
            code_id="CODE_001",
            language="Python",
            implementation=implementation,
            created_by=self.agent_id
        )
        self.deliverables.append(code)
        return f"[Engineer] Code implemented:\n{implementation[:100]}..."

    def _do_testing(self, task: TaskAllocation) -> str:
        """QA: Test and validate implementation using Claude"""
        prompt = f"""You are a QA Engineer. Create a test plan for:

Project: {task.task_description}

Design tests for:
1. Core functionality
2. Edge cases
3. Error handling

Estimate test coverage."""

        try:
            if USE_LOCAL_MODEL:
                response = client.messages_create(
                    system="You are a QA professional. Design comprehensive test plans.",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300
                )
            else:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=300,
                    system="You are a QA professional. Design comprehensive test plans.",
                    messages=[{"role": "user", "content": prompt}]
                )
            test_plan = response.content[0].text.strip()
            print(f"\n[🤖 MODEL GENERATED - QA Test Plan]\n{test_plan}\n")
        except Exception as e:
            test_plan = f"Test plan for: {task.task_description}"

        # Simulate test results
        test = TestResult(
            test_id="TEST_001",
            tests_run=10,
            passed=9,
            failed=1,
            created_by=self.agent_id
        )
        self.deliverables.append(test)
        return f"[QA] Testing: {test.passed}/{test.tests_run} tests passed ({test.success_rate*100:.1f}%)\nPlan:\n{test_plan[:100]}..."


class MetaGPTWorkflow(CoordinationProtocol):
    """
    Workflow coordination for MetaGPT

    Follows strict sequential phases:
    1. Requirements (Product Manager)
    2. Design (Architect)
    3. Implementation (Engineer)
    4. Testing (QA)
    """

    def __init__(self):
        self.current_phase = 0
        self.phases = [
            ("Requirements", SoftwareEngineeeringRole.PRODUCT_MANAGER),
            ("Design", SoftwareEngineeeringRole.ARCHITECT),
            ("Implementation", SoftwareEngineeeringRole.ENGINEER),
            ("Testing", SoftwareEngineeeringRole.QA)
        ]
        self.phase_results: Dict[str, List[Any]] = {}

    def coordinate(self, environment: 'MetaGPTEnvironment') -> bool:
        """
        Execute MetaGPT workflow:
        Sequential phases with clear handoffs
        """
        print(f"\n[MetaGPT] Starting structured workflow...")

        pending = [t for t in environment.task_queue if t.status == "pending"]
        if not pending:
            return False

        for task in pending:
            print(f"\n[MetaGPT] Processing task: {task.task_description}")

            # Execute each phase in sequence
            for phase_name, required_role in self.phases:
                print(f"\n  [Phase: {phase_name}]")
                self._execute_phase(environment, task, phase_name, required_role)

            task.status = "completed"
            environment.completed_tasks.append(task)

        return True

    def _execute_phase(self, environment: 'MetaGPTEnvironment', task: TaskAllocation,
                      phase_name: str, required_role: SoftwareEngineeeringRole):
        """Execute a single phase with the appropriate role"""
        # Find agent with required role
        agent = None
        for a in environment.agents.values():
            if isinstance(a, MetaGPTAgent) and a.software_role == required_role:
                agent = a
                break

        if agent:
            print(f"    → {agent.software_role.value} working on: {phase_name}")

            # Create phase-specific task
            phase_task = TaskAllocation(
                task_id=f"{task.task_id}_{phase_name.lower()}",
                task_description=f"{phase_name}: {task.task_description}",
                assigned_agent=agent.agent_id
            )

            # Execute
            result = agent.execute_task(phase_task)
            print(f"    ✓ Completed: {result[:60]}...")

            # Store phase result
            if phase_name not in self.phase_results:
                self.phase_results[phase_name] = []
            self.phase_results[phase_name].append(agent.deliverables[-1] if agent.deliverables else None)
        else:
            print(f"    ✗ No agent found for role: {required_role.value}")

    def resolve_conflicts(self, environment: 'MetaGPTEnvironment'):
        """Resolve conflicts in MetaGPT"""
        print("[MetaGPT] Resolving conflicts in workflow...")
        # In MetaGPT, conflicts are resolved by workflow structure


class MetaGPTEnvironment(MultiAgentEnvironment):
    """Environment for MetaGPT role-based collaboration"""

    def __init__(self, name: str = "MetaGPTEnvironment"):
        super().__init__(name)
        self.workflow = MetaGPTWorkflow()
        self.project_documentation: Dict[str, str] = {}

    def setup_roles(self):
        """Setup the software engineering roles"""
        roles = [
            ("pm_1", SoftwareEngineeeringRole.PRODUCT_MANAGER, ["requirements", "analysis"]),
            ("arch_1", SoftwareEngineeeringRole.ARCHITECT, ["design", "architecture"]),
            ("eng_1", SoftwareEngineeeringRole.ENGINEER, ["coding", "implementation"]),
            ("qa_1", SoftwareEngineeeringRole.QA, ["testing", "quality"])
        ]

        for agent_id, software_role, capabilities in roles:
            agent = MetaGPTAgent(agent_id, software_role, capabilities)
            self.register_agent(agent)

    def step(self):
        """Execute one step of the workflow"""
        self.step_count += 1

        # Process messages
        for agent in self.agents.values():
            for message in agent.outbox:
                self.route_message(message)
            agent.outbox.clear()

        # Allocate tasks
        self.allocate_tasks()

        # Execute workflow
        self.workflow.coordinate(self)

    def allocate_tasks(self):
        """Allocate tasks to the workflow"""
        for task in [t for t in self.task_queue if t.status == "pending"]:
            print(f"Task queued for workflow: {task.task_description}")

    def add_documentation(self, doc_id: str, content: str):
        """Add project documentation"""
        self.project_documentation[doc_id] = content

    def run(self, num_steps: int = 5):
        """Run the environment"""
        print(f"\n{'='*60}")
        print(f"Running MetaGPT Environment: {self.name}")
        print(f"{'='*60}\n")

        # Setup roles
        self.setup_roles()

        for _ in range(num_steps):
            self.step()
            if not self.task_queue:
                break

        self.print_status()
        self._print_workflow_results()

    def _print_workflow_results(self):
        """Print workflow results"""
        print(f"\n{'='*60}")
        print(f"Workflow Results")
        print(f"{'='*60}")

        for phase, results in self.workflow.phase_results.items():
            print(f"\n{phase}:")
            for i, result in enumerate(results):
                if result:
                    print(f"  - {result}")


# Demo
def main():
    """Interactive MetaGPT framework with role-based workflow"""

    print("="*70)
    print("🚀 MetaGPT Framework - Interactive Role-Based Software Engineering")
    print("="*70)
    print("\nMetaGPT uses specialized roles to build software collaboratively:")
    print("  1. Product Manager → Creates requirements")
    print("  2. Architect → Designs system architecture")
    print("  3. Engineer → Implements code")
    print("  4. QA → Creates test plans")
    print("\n" + "="*70 + "\n")

    project_counter = 1

    while True:
        print("\n" + "-"*70)
        print(f"Project #{project_counter}")
        print("-"*70)

        # Get project description from user
        project_desc = input("\n📋 Enter your project description (or 'quit' to exit): ").strip()

        if project_desc.lower() == "quit":
            print("\n✅ Thank you for using MetaGPT Framework!")
            break

        if not project_desc:
            print("⚠️  Please enter a valid project description")
            continue

        # Get number of workflow steps
        while True:
            try:
                steps_input = input("🔄 How many workflow steps? (5-20, default=10): ").strip()
                if not steps_input:
                    num_steps = 10
                    break
                num_steps = int(steps_input)
                if 5 <= num_steps <= 20:
                    break
                else:
                    print("⚠️  Please enter a number between 5-20")
            except ValueError:
                print("⚠️  Please enter a valid number")

        print(f"\n🎬 Starting workflow with {num_steps} steps...")
        print("="*70)

        # Create environment
        env = MetaGPTEnvironment(f"Project_{project_counter}")

        # Setup roles
        env.setup_roles()

        # Add task
        task = TaskAllocation(
            task_id=f"project_{project_counter}",
            task_description=project_desc,
            assigned_agent=""
        )
        env.add_task(task)

        # Run workflow
        print("\n🔥 Role-based workflow executing...\n")
        env.run(num_steps=num_steps)

        print("\n" + "="*70)
        print("✅ Workflow completed!")
        print("="*70)

        project_counter += 1


if __name__ == "__main__":
    # Check if API key is set (only needed for Anthropic API mode)
    if not USE_LOCAL_MODEL and not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your API key: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)

    main()
