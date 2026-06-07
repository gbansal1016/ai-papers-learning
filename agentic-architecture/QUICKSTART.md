# Quick Start Guide

## 2-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Navigate to the Folder
```bash
cd agentic-architecture
```

### 3. Run a Simple Agent
```bash
python code/react_agent.py
```

You should see the ReAct agent reasoning through a simple task with visible thought-action loops.

## Expected Learning Outcomes

After completing all phases, you'll be able to:

- [ ] Explain ReAct, RAISE, Reflexion, and LATS architectures
- [ ] Implement a basic ReAct agent from scratch
- [ ] Compare single-agent vs multi-agent approaches
- [ ] Build a simple Dylan or AGentverse system
- [ ] Know when to use each architecture
- [ ] Understand planning, execution, reflection cycles
- [ ] Implement basic tool calling patterns

## Run Individual Agents

Each agent is standalone and runnable:

```bash
# Single-Agent Architectures
python code/react_agent.py              # ReAct: Reason + Act
python code/reflexion_agent.py          # Reflexion: Learn from failures
python code/lats_agent.py               # LATS: Tree search reasoning

# Multi-Agent Frameworks  
python code/multi_agent_framework.py    # Base multi-agent classes
python code/dylan_framework.py          # Dylan: Dynamic hierarchical
python code/agenverse_framework.py      # AGentverse: Cooperative
python code/metagpt_framework.py        # MetaGPT: Role-based
```

## Troubleshooting

### `ModuleNotFoundError`
```bash
pip install -r requirements.txt
```

### `FileNotFoundError` when running code
Make sure you're in the `agentic-architecture/` directory:
```bash
cd agentic-architecture
python code/react_agent.py
```

### Want to Modify Code?
All code includes comments explaining each section. Feel free to:
- Change task descriptions
- Add new tools
- Modify agent behavior
- Experiment with parameters

## Architecture Overview

### Single-Agent Architectures
**ReAct**: Explicit reasoning loops
```
Think → Act → Observe → Think → Act → ...
```

**Reflexion**: Learn from mistakes
```
Attempt → Fail → Reflect → Improve → Retry
```

**LATS**: Explore multiple paths
```
State → Branch (try multiple actions) → Best path
```

### Multi-Agent Architectures
**Dylan**: Hierarchical task decomposition
```
Manager → Delegates to workers → Coordinates results
```

**AGentverse**: Peer collaboration
```
Agent A ←→ Agent B ←→ Agent C (discuss, decide)
```

**MetaGPT**: Role-based software engineering
```
Product Manager → Architect → Engineer → QA
```

## Key Files to Understand

| File | Purpose | Time |
|------|---------|------|
| `phase0_fundamentals.ipynb` | Concept overview
| `code/react_agent.py` | Simplest working agent
| `code/multi_agent_framework.py` | Multi-agent base classes

## Common Questions

**Q: Do I need an API key?**
A: By default, code uses the Anthropic API (requires `ANTHROPIC_API_KEY`). To run locally without API keys, use Ollama or another local LLM (see "Using Local Models" below).

**Q: Can I modify these agents?**
A: Absolutely! They're designed for learning and experimentation.

**Q: What's the difference between phases?**
A: Phase 0 = concepts, Phase 1 = implementation, Phase 2 = advanced, Phase 3 = integration

**Q: Should I run notebooks or Python files?**
A: Both! Notebooks for learning, Python files for quick demos.

**Q: Which agent should I use for my project?**
A: See README.md's "When to Use What" section

## Using Local Models (No API Keys Required)

### Option 1: Ollama (Easiest)

**Install Ollama:**
```bash
# macOS/Linux/Windows
# Download from https://ollama.ai
```

**Pull a model:**
```bash
ollama pull mistral  # Fast, capable model
# Or: ollama pull llama2, neural-chat, etc.
```

**Start Ollama server:**
```bash
ollama serve
# Runs on http://localhost:11434
```

**Update agent code to use Ollama:**
```python
from anthropic import Anthropic

client = Anthropic(
    api_key="not-needed",  # Ollama doesn't need this
    base_url="http://localhost:11434/v1",  # Ollama endpoint
)

response = client.messages.create(
    model="mistral",  # Use Ollama model name
    max_tokens=1024,
    messages=[{"role": "user", "content": "Think step by step..."}]
)
```

### Option 2: LM Studio (GUI-Based)

**Install LM Studio:**
```bash
# Download from https://lmstudio.ai
```

**Load a model in LM Studio UI:**
- Download your choice (Mistral, Neural Chat, etc.)
- Click "Load into context"

**Update code (same as Ollama):**
```python
client = Anthropic(
    api_key="not-needed",
    base_url="http://localhost:1234/v1",  # LM Studio endpoint
)
```

### Option 3: Other Local Runners

| Tool | Command | Endpoint |
|------|---------|----------|
| **Ollama** | `ollama serve` | `http://localhost:11434/v1` |
| **LM Studio** | GUI app | `http://localhost:1234/v1` |
| **vLLM** | `vllm serve mistral-7b` | `http://localhost:8000/v1` |
| **Text Generation WebUI** | `python server.py` | `http://localhost:5000/v1` |

### Option 4: Use Groq (Free API, No Claude)

If you want a free API alternative:
```python
from groq import Groq

client = Groq(api_key="your-groq-key")  # Free, fast inference

response = client.chat.completions.create(
    model="mixtral-8x7b-32768",
    messages=[...],
    max_tokens=1024,
)
```

## Quick Comparison

| Method | Speed | Cost | Setup | Quality |
|--------|-------|------|-------|---------|
| **Anthropic API** | Fast | $$ | 1 min | Excellent |
| **Ollama Local** | Medium | Free | 10 min | Good |
| **LM Studio** | Medium | Free | 15 min | Good |
| **Groq** | Very Fast | Free | 5 min | Good |

## Recommended for Learning

- **Start with**: Ollama + Mistral (free, fast, good quality)
- **For production**: Anthropic API or Groq
- **For experimentation**: LM Studio (easiest UI)

## Next Steps

1. Run `python code/react_agent.py` to see your first agent in action
2. Open `notebooks/phase0_fundamentals.ipynb` to understand concepts
3. Modify `code/react_agent.py` to solve a different task
4. Compare with other single-agent implementations
5. Explore multi-agent patterns in Phase 2

## Support

For each notebook and code file:
- ✅ Clear explanations of concepts
- ✅ Commented code showing exactly what happens
- ✅ Example outputs to understand behavior
- ✅ Exercises to test your understanding

---

**Total Learning Time**: ~2 hours (all phases)

**Start with**: Phase 0 fundamentals (15 minutes)

**Difficulty**: Beginner → Intermediate → Advanced

