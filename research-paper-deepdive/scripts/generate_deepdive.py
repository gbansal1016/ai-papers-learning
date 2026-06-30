#!/usr/bin/env python3
"""
Research Paper Deep Dive Generator

This script creates a complete phased learning structure for studying research papers.
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime


class ResearchPaperDeepDiveGenerator:
    """Generate comprehensive research paper study materials."""

    def __init__(self, paper_info: dict, output_dir: str, phases: int = 3):
        """Initialize the generator."""
        self.paper_info = paper_info
        self.output_dir = Path(output_dir)
        # Phases: 3 = fundamentals+basic+algorithms (phase 0-2)
        #         4 = above + LLM Integration (phase 0-3)
        #         5 = above + Complete Implementation (phase 0-4)
        self.phases = max(3, min(5, phases))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.paper_slug = paper_info.get('paper_title', 'research').lower()
        self.paper_slug = self.paper_slug.replace(' ', '-').replace('.', '')[:30]

    def generate_readme(self) -> str:
        """Generate readme.md with paper reference."""
        title = self.paper_info.get('paper_title', 'Research Paper')
        authors = self.paper_info.get('authors', 'Unknown Authors')
        year = self.paper_info.get('year', 'Unknown')
        abstract = self.paper_info.get('abstract', 'Abstract not provided.')
        url = self.paper_info.get('url', '')

        content = f"""# {title}
## Complete Study Guide

### Paper Reference

**Title:** {title}

**Authors:** {authors}

**Year:** {year}

**Abstract:**
{abstract}

"""
        if url:
            content += f"**URL:** {url}\n\n"

        content += f"""---

## Learning Structure

This guide is organized into **{self.phases} progressive phases**:

### Phase 0: Fundamentals
- Core concepts explained visually
- Paper motivation and innovation
- Key insights and takeaways
- When to use this approach
- **No code** - Pure conceptual understanding
- **Time:** ~30 minutes

### Phase 1: Basic Concepts
- Core data structures implementation
- Simple, runnable Python code
- Manual examples you can trace
- Learning through building
- **Time:** ~45 minutes

### Phase 2: Algorithms
- Key algorithm implementations
- Advanced techniques and optimizations
- Performance analysis and metrics
- Practical examples with output
- **Time:** ~60 minutes

"""
        if self.phases > 3:
            content += """### Phase 3: LLM Integration
- API setup and authentication
- Prompting templates
- Cost tracking
- Error handling
- Real-world examples with LLMs
- **Time:** ~60 minutes

"""

        content += f"""---

## Quick Start

1. Read this file for paper context
2. Open `phase0_fundamentals.ipynb` first
3. Follow through phases sequentially
4. Experiment and modify code as you learn

Total time commitment: **2-4 hours** depending on depth.

---

## Files in This Project

- `readme.md` - This file (paper reference)
- `quickstart.md` - 2-minute setup guide
- `phase0_fundamentals.ipynb` - Concepts and theory
- `phase1_basic_concepts.ipynb` - Core implementations
- `phase2_algorithms.ipynb` - Advanced techniques
"""
        if self.phases > 3:
            content += "- `phase3_llm_integration.ipynb` - LLM integration\n"
        if self.phases > 4:
            content += "- `phase4_complete_implementation.ipynb` - Complete implementation\n"

        content += f"""- `requirements.txt` - Python dependencies
- `.venv/` - Virtual environment

---

## About This Study Guide

This guide was generated using the Research Paper Deep Dive skill.
It provides structured, progressive learning for comprehensive paper understanding.

**Created:** {datetime.now().strftime('%Y-%m-%d')}

"""
        return content

    def generate_quickstart(self) -> str:
        """Generate quickstart.md."""
        title = self.paper_info.get('paper_title', 'Research Paper')
        dir_name = self.output_dir.name

        content = f"""# Quick Start - {title}

## Get Started in 2 Minutes

### 1. Install Dependencies
```bash
cd {dir_name}
pip install -r requirements.txt
```

### 2. Launch Jupyter
```bash
jupyter notebook
```

### 3. Open Notebooks in Order

1. **Start:** `readme.md` (5 min read)
2. **Learn:** `phase0_fundamentals.ipynb` (30 min)
3. **Code:** `phase1_basic_concepts.ipynb` (45 min)
4. **Build:** `phase2_algorithms.ipynb` (60 min)
"""
        if self.phases > 3:
            content += "5. **Integrate:** `phase3_llm_integration.ipynb` (60 min)\n"
        if self.phases > 4:
            content += "6. **Complete:** `phase4_complete_implementation.ipynb` (90+ min)\n"

        content += """
---

## Learning Objectives

After completing all phases, you'll be able to:

✅ Understand core concepts deeply
✅ Implement key algorithms
✅ Know when and how to use these techniques
✅ Apply to your own problems
✅ Understand trade-offs and limitations
✅ Extend the work further

---

## Expected Time

- **Quick path** (Phases 0-1): 1.5 hours
- **Standard path** (Phases 0-2): 2.5 hours
"""
        if self.phases > 3:
            content += "- **Deep path** (Phases 0-3): 4 hours\n"
        if self.phases > 4:
            content += "- **Complete path** (Phases 0-4): 5+ hours\n"

        content += """
---

## Tips

1. Don't skip Phase 0 - foundation matters
2. Code along, don't just read
3. Experiment and modify examples
4. Take notes of key insights
5. Return to these materials later as reference

---

## Troubleshooting

**Jupyter won't start:**
```bash
python3 -m jupyter notebook
```

**Module not found errors:**
```bash
pip install -r requirements.txt
```

**Restart kernel:** Kernel → Restart in Jupyter

---

Ready? Start with `readme.md`, then open `phase0_fundamentals.ipynb`
"""
        return content

    def generate_phase0_notebook(self) -> str:
        """Generate phase0_fundamentals.ipynb."""
        return json.dumps({
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"# Phase 0: Fundamentals - {self.paper_info.get('paper_title', 'Research Paper')}\n",
                        "\n",
                        "## Overview\n",
                        "\n",
                        "This notebook introduces the core concepts from the paper through conceptual understanding.\n",
                        "**No code yet** - we're focusing on understanding the \"why\" before the \"how\"."
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Paper Summary\n",
                        "\n",
                        f"**Title:** {self.paper_info.get('paper_title', 'Unknown')}\n",
                        f"**Authors:** {self.paper_info.get('authors', 'Unknown')}\n",
                        f"**Year:** {self.paper_info.get('year', 'Unknown')}\n",
                        "\n",
                        "### Abstract\n",
                        f"{self.paper_info.get('abstract', 'Abstract not provided.')}"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 1: The Problem\n",
                        "\n",
                        "What problem does this paper solve?\n",
                        "\n",
                        "*(Add your notes here as you read the paper)*"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 2: Core Innovation\n",
                        "\n",
                        "What is the main innovation or contribution?\n",
                        "\n",
                        "Key insights:\n",
                        "- Insight 1\n",
                        "- Insight 2\n",
                        "- Insight 3"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 3: Key Concepts\n",
                        "\n",
                        "List the main concepts you need to understand:\n",
                        "\n",
                        "1. Concept 1\n",
                        "2. Concept 2\n",
                        "3. Concept 3"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 4: How It Works (High Level)\n",
                        "\n",
                        "Explain the approach in simple terms.\n",
                        "\n",
                        "Step 1: ...\n",
                        "Step 2: ...\n",
                        "Step 3: ..."
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 5: When to Use This\n",
                        "\n",
                        "### Good Use Cases\n",
                        "- Case 1\n",
                        "- Case 2\n",
                        "\n",
                        "### Poor Use Cases\n",
                        "- Case 1\n",
                        "- Case 2"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Key Takeaways\n",
                        "\n",
                        "After Phase 0, you should understand:\n",
                        "\n",
                        "✅ What problem this paper addresses\n",
                        "✅ The core innovation\n",
                        "✅ Main concepts and how they fit together\n",
                        "✅ Strengths and limitations\n",
                        "✅ When and why to use this approach\n",
                        "\n",
                        "---\n",
                        "\n",
                        "**Ready for Phase 1?** Open `phase1_basic_concepts.ipynb` to start implementing!"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.10.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }, indent=2)

    def generate_phase1_notebook(self) -> str:
        """Generate phase1_basic_concepts.ipynb."""
        return json.dumps({
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"# Phase 1: Basic Concepts - {self.paper_info.get('paper_title', 'Research Paper')}\n",
                        "\n",
                        "## Goal\n",
                        "\n",
                        "Implement the **fundamental data structures** and concepts from the paper.\n",
                        "Learn by building core components from scratch."
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 1: Setup and Imports"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "from typing import List, Dict, Optional\n",
                        "from dataclasses import dataclass, field\n",
                        "import time\n",
                        "\n",
                        "print('✓ Imports successful')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 2: Core Data Structures"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "@dataclass\n",
                        "class CoreConcept:\n",
                        "    '''Core concept/structure from the paper.'''\n",
                        "    content: str\n",
                        "    value: float = 0.0\n",
                        "    metadata: Dict = field(default_factory=dict)\n",
                        "    \n",
                        "    def __repr__(self) -> str:\n",
                        "        return f'CoreConcept(value={self.value:.2f})'\n",
                        "\n",
                        "print('✓ Core data structures defined')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 3: Manual Example"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "example = CoreConcept(\n",
                        "    content='Example concept from the paper',\n",
                        "    value=0.8\n",
                        ")\n",
                        "\n",
                        "print(f'Created: {example}')\n",
                        "print(f'Value: {example.value}')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Key Insights\n",
                        "\n",
                        "✅ You now understand the core data structures\n",
                        "✅ You can create and manipulate them\n",
                        "✅ You're ready for Phase 2\n",
                        "\n",
                        "Ready for Phase 2? Open `phase2_algorithms.ipynb`"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.10.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }, indent=2)

    def generate_phase2_notebook(self) -> str:
        """Generate phase2_algorithms.ipynb."""
        return json.dumps({
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"# Phase 2: Algorithms - {self.paper_info.get('paper_title', 'Research Paper')}\n",
                        "\n",
                        "## Goal\n",
                        "\n",
                        "Implement the **key algorithms and techniques** from the paper."
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 1: Core Algorithm"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "from typing import List\n",
                        "\n",
                        "class CoreAlgorithm:\n",
                        "    '''Implementation of the core algorithm.'''\n",
                        "    \n",
                        "    def __init__(self):\n",
                        "        self.metrics = {}\n",
                        "    \n",
                        "    def solve(self, problem: str):\n",
                        "        '''Solve a problem using the approach from the paper.'''\n",
                        "        return {'status': 'implemented'}\n",
                        "    \n",
                        "    def get_metrics(self):\n",
                        "        '''Get performance metrics.'''\n",
                        "        return self.metrics\n",
                        "\n",
                        "print('✓ Algorithm class defined')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 2: Testing and Evaluation"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "algorithm = CoreAlgorithm()\n",
                        "result = algorithm.solve('test problem')\n",
                        "print(f'Result: {result}')\n",
                        "print(f'Metrics: {algorithm.get_metrics()}')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 3: Performance Analysis"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "import time\n",
                        "\n",
                        "start = time.time()\n",
                        "result = algorithm.solve('test')\n",
                        "duration = time.time() - start\n",
                        "\n",
                        "print(f'Duration: {duration:.4f}s')\n",
                        "print(f'Result: {result}')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Key Takeaways\n",
                        "\n",
                        "✅ Algorithm implementation\n",
                        "✅ Performance characteristics\n",
                        "✅ Trade-offs and optimizations\n",
                        "\n",
                        "---\n",
                        "\n",
                        "**Ready for Phase 3?** Open `phase3_llm_integration.ipynb` to integrate with real LLMs!"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.10.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }, indent=2)

    def generate_phase3_notebook(self) -> str:
        """Generate phase3_llm_integration.ipynb."""
        return json.dumps({
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"# Phase 3: LLM Integration - {self.paper_info.get('paper_title', 'Research Paper')}\n",
                        "\n",
                        "## Goal\n",
                        "\n",
                        "Integrate **real Language Models** (Claude, OpenAI GPT) with your implementation."
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 1: Setup and Authentication"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "import os\n",
                        "from typing import Optional\n",
                        "\n",
                        "# Option 1: Claude API (Anthropic)\n",
                        "CLAUDE_API_KEY = os.getenv('ANTHROPIC_API_KEY', 'your-key-here')\n",
                        "\n",
                        "# Option 2: OpenAI API\n",
                        "OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-key-here')\n",
                        "\n",
                        "print('✓ API keys configured')\n",
                        "print('Note: For production, use environment variables or secure vaults')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 2: LLM Prompting Templates"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "from dataclasses import dataclass\n",
                        "\n",
                        "@dataclass\n",
                        "class PromptTemplate:\n",
                        "    '''Template for LLM prompts.'''\n",
                        "    name: str\n",
                        "    system: str\n",
                        "    user: str\n",
                        "    \n",
                        "    def format(self, **kwargs) -> dict:\n",
                        "        '''Format prompt with variables.'''\n",
                        "        return {\n",
                        "            'system': self.system.format(**kwargs),\n",
                        "            'user': self.user.format(**kwargs)\n",
                        "        }\n",
                        "\n",
                        "# Example: Generation prompt\n",
                        "generation_prompt = PromptTemplate(\n",
                        "    name='generate',\n",
                        "    system='You are an expert in the field. Generate high-quality solutions.',\n",
                        "    user='Generate a solution for: {problem}'\n",
                        ")\n",
                        "\n",
                        "# Example: Evaluation prompt\n",
                        "evaluation_prompt = PromptTemplate(\n",
                        "    name='evaluate',\n",
                        "    system='You are an expert evaluator. Rate solutions objectively.',\n",
                        "    user='Evaluate the quality of this solution: {solution}'\n",
                        ")\n",
                        "\n",
                        "print('✓ Prompt templates defined')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 3: LLM API Wrapper"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "import time\n",
                        "from typing import Dict, List\n",
                        "\n",
                        "class LLMWrapper:\n",
                        "    '''Wrapper for LLM API calls with cost tracking.'''\n",
                        "    \n",
                        "    def __init__(self, model: str = 'claude-3-5-sonnet'):\n",
                        "        self.model = model\n",
                        "        self.calls = 0\n",
                        "        self.total_tokens = 0\n",
                        "        self.total_cost = 0.0\n",
                        "    \n",
                        "    def call(self, system: str, user: str) -> str:\n",
                        "        '''Make an LLM call (template - implement with actual API).'''\n",
                        "        self.calls += 1\n",
                        "        # In production: call actual API\n",
                        "        # import anthropic\n",
                        "        # client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)\n",
                        "        # response = client.messages.create(...)\n",
                        "        return 'LLM response here'\n",
                        "    \n",
                        "    def get_stats(self) -> dict:\n",
                        "        '''Get usage statistics.'''\n",
                        "        return {\n",
                        "            'calls': self.calls,\n",
                        "            'total_tokens': self.total_tokens,\n",
                        "            'total_cost': self.total_cost,\n",
                        "            'avg_tokens_per_call': self.total_tokens / max(1, self.calls)\n",
                        "        }\n",
                        "\n",
                        "llm = LLMWrapper()\n",
                        "print('✓ LLM wrapper initialized')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 4: Error Handling and Retries"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "import time\n",
                        "from functools import wraps\n",
                        "\n",
                        "def retry_with_backoff(max_retries: int = 3, backoff_ms: int = 1000):\n",
                        "    '''Decorator for API calls with exponential backoff.'''\n",
                        "    def decorator(func):\n",
                        "        @wraps(func)\n",
                        "        def wrapper(*args, **kwargs):\n",
                        "            for attempt in range(max_retries):\n",
                        "                try:\n",
                        "                    return func(*args, **kwargs)\n",
                        "                except Exception as e:\n",
                        "                    if attempt < max_retries - 1:\n",
                        "                        wait_ms = backoff_ms * (2 ** attempt)\n",
                        "                        print(f'Attempt {attempt + 1} failed, retrying in {wait_ms}ms...')\n",
                        "                        time.sleep(wait_ms / 1000)\n",
                        "                    else:\n",
                        "                        raise\n",
                        "        return wrapper\n",
                        "    return decorator\n",
                        "\n",
                        "@retry_with_backoff(max_retries=3)\n",
                        "def safe_llm_call(prompt: str) -> str:\n",
                        "    '''LLM call with automatic retry on failure.'''\n",
                        "    # Implementation would go here\n",
                        "    return 'Result'\n",
                        "\n",
                        "print('✓ Error handling configured')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Key Concepts\n",
                        "\n",
                        "✅ API authentication and setup\n",
                        "✅ Prompt engineering and templates\n",
                        "✅ Token counting and cost tracking\n",
                        "✅ Error handling and retries\n",
                        "✅ Integration with your algorithms\n",
                        "\n",
                        "---\n",
                        "\n",
                        "**Ready for Phase 4?** Open `phase4_complete_implementation.ipynb` for end-to-end examples!"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.10.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }, indent=2)

    def generate_phase4_notebook(self) -> str:
        """Generate phase4_complete_implementation.ipynb."""
        return json.dumps({
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"# Phase 4: Complete Implementation - {self.paper_info.get('paper_title', 'Research Paper')}\n",
                        "\n",
                        "## Goal\n",
                        "\n",
                        "Build a **complete end-to-end system** combining all previous phases with LLM integration."
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 1: Full System Architecture"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "from dataclasses import dataclass\n",
                        "from typing import List, Optional\n",
                        "from enum import Enum\n",
                        "\n",
                        "class SystemStatus(Enum):\n",
                        "    INITIALIZING = 'init'\n",
                        "    RUNNING = 'running'\n",
                        "    COMPLETED = 'completed'\n",
                        "    FAILED = 'failed'\n",
                        "\n",
                        "@dataclass\n",
                        "class SystemConfig:\n",
                        "    '''Configuration for the complete system.'''\n",
                        "    model: str = 'claude-3-5-sonnet'\n",
                        "    max_retries: int = 3\n",
                        "    timeout_seconds: int = 60\n",
                        "    temperature: float = 0.7\n",
                        "\n",
                        "class CompleteSystem:\n",
                        "    '''Integration of algorithms + LLM for end-to-end solving.'''\n",
                        "    \n",
                        "    def __init__(self, config: SystemConfig):\n",
                        "        self.config = config\n",
                        "        self.status = SystemStatus.INITIALIZING\n",
                        "        self.results = []\n",
                        "    \n",
                        "    def process(self, problem: str) -> dict:\n",
                        "        '''Process a problem end-to-end.'''\n",
                        "        self.status = SystemStatus.RUNNING\n",
                        "        try:\n",
                        "            # Step 1: Break down problem (Phase 1 concepts)\n",
                        "            # Step 2: Apply algorithm (Phase 2)\n",
                        "            # Step 3: Use LLM for enhancement (Phase 3)\n",
                        "            result = {'status': 'success', 'output': 'Solution here'}\n",
                        "            self.status = SystemStatus.COMPLETED\n",
                        "            return result\n",
                        "        except Exception as e:\n",
                        "            self.status = SystemStatus.FAILED\n",
                        "            return {'status': 'error', 'error': str(e)}\n",
                        "\n",
                        "config = SystemConfig()\n",
                        "system = CompleteSystem(config)\n",
                        "print('✓ Complete system initialized')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 2: Real Problem Examples"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Example problems to test your system\n",
                        "test_problems = [\n",
                        "    'Problem 1: Your first test case',\n",
                        "    'Problem 2: A more complex case',\n",
                        "    'Problem 3: Edge case handling',\n",
                        "]\n",
                        "\n",
                        "results = []\n",
                        "for problem in test_problems:\n",
                        "    result = system.process(problem)\n",
                        "    results.append({'problem': problem, 'result': result})\n",
                        "    print(f'✓ Processed: {problem[:30]}...')\n",
                        "\n",
                        "print(f'\\nCompleted {len(results)} test cases')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 3: Performance Benchmarking"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "import time\n",
                        "from statistics import mean, stdev\n",
                        "\n",
                        "def benchmark_system(system, test_cases: List[str], iterations: int = 3) -> dict:\n",
                        "    '''Benchmark system performance.'''\n",
                        "    timings = []\n",
                        "    \n",
                        "    for _ in range(iterations):\n",
                        "        for test_case in test_cases:\n",
                        "            start = time.time()\n",
                        "            system.process(test_case)\n",
                        "            duration = time.time() - start\n",
                        "            timings.append(duration)\n",
                        "    \n",
                        "    return {\n",
                        "        'mean_time_ms': mean(timings) * 1000,\n",
                        "        'std_dev_ms': stdev(timings) * 1000 if len(timings) > 1 else 0,\n",
                        "        'min_ms': min(timings) * 1000,\n",
                        "        'max_ms': max(timings) * 1000,\n",
                        "        'total_runs': len(timings)\n",
                        "    }\n",
                        "\n",
                        "benchmark = benchmark_system(system, test_problems[:2], iterations=2)\n",
                        "print('Performance Benchmark:')\n",
                        "for key, value in benchmark.items():\n",
                        "    print(f'  {key}: {value:.2f}')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Part 4: Production Deployment Checklist"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "deployment_checklist = {\n",
                        "    'Security': [\n",
                        "        '✓ API keys in environment variables (not hardcoded)',\n",
                        "        '✓ Input validation implemented',\n",
                        "        '✓ Error messages safe for users',\n",
                        "        '✓ Rate limiting configured'\n",
                        "    ],\n",
                        "    'Performance': [\n",
                        "        '✓ Caching strategy implemented',\n",
                        "        '✓ Timeouts configured',\n",
                        "        '✓ Batch processing for bulk operations'\n",
                        "    ],\n",
                        "    'Monitoring': [\n",
                        "        '✓ Logging setup',\n",
                        "        '✓ Error tracking',\n",
                        "        '✓ Performance metrics',\n",
                        "        '✓ Cost tracking'\n",
                        "    ],\n",
                        "    'Testing': [\n",
                        "        '✓ Unit tests passing',\n",
                        "        '✓ Integration tests passing',\n",
                        "        '✓ Load testing completed',\n",
                        "        '✓ Edge cases handled'\n",
                        "    ]\n",
                        "}\n",
                        "\n",
                        "print('Deployment Checklist:')\n",
                        "for category, items in deployment_checklist.items():\n",
                        "    print(f'\\n{category}:')\n",
                        "    for item in items:\n",
                        "        print(f'  {item}')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Summary\n",
                        "\n",
                        "You now have a complete system that:\n",
                        "\n",
                        "✅ Understands the paper conceptually (Phase 0)\n",
                        "✅ Implements core concepts (Phase 1)\n",
                        "✅ Applies advanced algorithms (Phase 2)\n",
                        "✅ Integrates with LLMs (Phase 3)\n",
                        "✅ Solves real problems end-to-end (Phase 4)\n",
                        "\n",
                        "## Next Steps\n",
                        "\n",
                        "1. **Customize prompts** for your specific use case\n",
                        "2. **Add domain-specific logic** based on paper insights\n",
                        "3. **Optimize for your metrics** (cost, speed, accuracy)\n",
                        "4. **Deploy to production** following the checklist\n",
                        "5. **Monitor and iterate** based on real usage"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.10.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }, indent=2)

    def generate_requirements(self) -> str:
        """Generate requirements.txt."""
        requirements = f"""# Research Paper Deep Dive: {self.paper_info.get('paper_title', 'Research Paper')}
# Install with: pip install -r requirements.txt

# Core
jupyter>=1.0.0
jupyterlab>=3.0.0

# Data science
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
scikit-learn>=1.3.0

# Utilities
tqdm>=4.66.0
python-dotenv>=1.0.0
"""

        # Add LLM packages if phases > 3
        if self.phases > 3:
            requirements += """
# LLM Integration (Phases 3-4)
anthropic>=0.18.0
openai>=1.0.0
"""

        requirements += """
# Paper-specific dependencies:
# Add as needed for this research paper
"""
        return requirements

    def generate_all(self) -> None:
        """Generate all files."""
        print(f"📚 Generating research paper deep dive for: {self.paper_info.get('paper_title')}")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Phases to generate: {self.phases}")
        print()

        # Generate files
        readme_path = self.output_dir / "readme.md"
        readme_path.write_text(self.generate_readme())
        print(f"✓ Created readme.md")

        quickstart_path = self.output_dir / "quickstart.md"
        quickstart_path.write_text(self.generate_quickstart())
        print(f"✓ Created quickstart.md")

        phase0_path = self.output_dir / "phase0_fundamentals.ipynb"
        phase0_path.write_text(self.generate_phase0_notebook())
        print(f"✓ Created phase0_fundamentals.ipynb")

        phase1_path = self.output_dir / "phase1_basic_concepts.ipynb"
        phase1_path.write_text(self.generate_phase1_notebook())
        print(f"✓ Created phase1_basic_concepts.ipynb")

        phase2_path = self.output_dir / "phase2_algorithms.ipynb"
        phase2_path.write_text(self.generate_phase2_notebook())
        print(f"✓ Created phase2_algorithms.ipynb")

        if self.phases > 3:
            phase3_path = self.output_dir / "phase3_llm_integration.ipynb"
            phase3_path.write_text(self.generate_phase3_notebook())
            print(f"✓ Created phase3_llm_integration.ipynb")

        if self.phases > 4:
            phase4_path = self.output_dir / "phase4_complete_implementation.ipynb"
            phase4_path.write_text(self.generate_phase4_notebook())
            print(f"✓ Created phase4_complete_implementation.ipynb")

        req_path = self.output_dir / "requirements.txt"
        req_path.write_text(self.generate_requirements())
        print(f"✓ Created requirements.txt")

        print()
        print(f"✅ Complete! Study materials ready in: {self.output_dir}")
        print(f"\n📚 Learning Path:")
        print(f"   Phase 0: Fundamentals (30 min)")
        print(f"   Phase 1: Basic Concepts (45 min)")
        print(f"   Phase 2: Algorithms (60 min)")
        if self.phases > 3:
            print(f"   Phase 3: LLM Integration (60 min)")
        if self.phases > 4:
            print(f"   Phase 4: Complete Implementation (90+ min)")
        print(f"\n🚀 Next steps:")
        print(f"   1. cd {self.output_dir.name}")
        print(f"   2. pip install -r requirements.txt")
        print(f"   3. jupyter notebook")
        print(f"   4. Open readme.md, then phase0_fundamentals.ipynb")


def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive research paper study materials"
    )

    parser.add_argument("--paper-title", required=True, help="Title of the paper")
    parser.add_argument("--authors", default="Unknown", help="Paper authors")
    parser.add_argument("--year", type=int, default=2024, help="Publication year")
    parser.add_argument("--abstract", default="", help="Paper abstract")
    parser.add_argument("--url", default="", help="Link to paper")
    parser.add_argument("--output-dir", default="./research-paper", help="Output directory")
    parser.add_argument("--phases", type=int, default=3, help="Number of phases (2-4)")

    args = parser.parse_args()

    paper_info = {
        "paper_title": args.paper_title,
        "authors": args.authors,
        "year": args.year,
        "abstract": args.abstract,
        "url": args.url,
    }

    generator = ResearchPaperDeepDiveGenerator(paper_info, args.output_dir, args.phases)
    generator.generate_all()


if __name__ == "__main__":
    main()
