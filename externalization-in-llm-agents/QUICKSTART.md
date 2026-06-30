# Quickstart Guide

## 2-Minute Setup

```bash
# 1. Navigate to this folder
cd /Users/gaurav/Documents/Claude/workspace/externalization-in-llm-agents

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch Jupyter
jupyter lab
```

Then open `notebooks/fundamentals.ipynb` to begin.

---

## Learning Path

| Notebook | Time | What You'll Learn |
|----------|------|-------------------|
| `fundamentals.ipynb` | 30 min | Core concepts, no code |
| `memory_skill_concepts.ipynb` | 45 min | Memory tiers + skill progressive disclosure |
| `harness_algorithms.ipynb` | 60 min | Harness loop + approval gates |

---

## Key Files

- **Paper:** `2604.08224v1 - Externalization in LLM Agents.pdf`
- **Real implementation:** `personal-finance-agent/agent/agent_core.py`
- **Architecture spec:** `personal-finance-agent/design/AGENT_SPECIFICATION.md`

---

## Troubleshooting

**Jupyter not found:**
```bash
pip install jupyterlab
```

**Import errors in notebooks:**
```bash
pip install -r requirements.txt --upgrade
```
