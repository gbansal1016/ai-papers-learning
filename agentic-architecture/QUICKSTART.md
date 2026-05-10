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

## Which Notebook Should I Read First?

**Recommended Path:**

1. **START HERE**: `notebooks/phase0_fundamentals.ipynb`
   - Read this first
   - Understand core concepts
   - No code, just concepts

2. **THEN**: `notebooks/phase1_single_agents.ipynb`
   - See working code
   - Run and modify examples
   - Understand each agent type

3. **NEXT**: `notebooks/phase2_multi_agents.ipynb`
   - Learn multi-agent patterns 
   - See collaboration in action
   - Understand tradeoffs

4. **ADVANCED**: `notebooks/phase3_integrated.ipynb`
   - Combine approaches
   - Real-world examples
   - Performance insights

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
A: No! All code runs locally with simulated environments.

**Q: Can I modify these agents?**
A: Absolutely! They're designed for learning and experimentation.

**Q: What's the difference between phases?**
A: Phase 0 = concepts, Phase 1 = implementation, Phase 2 = advanced, Phase 3 = integration

**Q: Should I run notebooks or Python files?**
A: Both! Notebooks for learning, Python files for quick demos.

**Q: Which agent should I use for my project?**
A: See README.md's "When to Use What" section

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

