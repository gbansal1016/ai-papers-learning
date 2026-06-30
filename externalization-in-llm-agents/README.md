# Externalization in LLM Agents

## Paper Reference

**Title:** Externalization in LLM Agents  
**Authors:** Zhou et al.  
**Year:** 2026  
**ArXiv:** 2604.08224v1  
**PDF:** `2604.08224v1 - Externalization in LLM Agents.pdf` (in this folder)

---

## Core Thesis

> Reliable LLM agency comes not from larger models alone, but from systematically relocating cognitive burdens into persistent, inspectable, reusable **external** structures.

The paper argues that the fundamental bottleneck in LLM agents is not model capability — it is the lack of externalized infrastructure. When an agent tries to hold conversation history, procedural knowledge, interaction contracts, and coordination logic all inside the context window, it fails predictably. The solution is to move each of these burdens outside the model.

---

## The Four Externalizations

```
┌──────────────────────────────────────────────────────────────────┐
│                    EXTERNALIZATION FRAMEWORK                      │
│                                                                  │
│   COGNITIVE BURDEN        EXTERNALIZATION       IMPLEMENTATION   │
│   ─────────────────       ─────────────────     ─────────────── │
│   State & history    →    Memory               DynamoDB (4-tier) │
│   Procedural know.   →    Skills               SKILL.md (S3)     │
│   Service contracts  →    Protocols            MCP tools         │
│   Coordination       →    Harness              Agent Core/Strands │
└──────────────────────────────────────────────────────────────────┘
```

### §3 — Memory Externalization
Converts model recall (from weights) into **recognition** (from a curated retrieve).

| Tier | Purpose | Lifetime | FinAgent Example |
|------|---------|---------|-----------------|
| WORKING | Active session intent, pending actions | 24 hours | Current trade request in flight |
| EPISODIC | Past events, decisions, outcomes | 90 days | "Bought 10 NVDA at $950 on Jun 18" |
| SEMANTIC | Stable domain knowledge, heuristics | Permanent | "User's sectors to avoid: tobacco" |
| PERSONAL | User profile, goals, preferences | Permanent | Risk tolerance, approval threshold |

### §4 — Skill Externalization
Packages procedural expertise into **SKILL.md** files stored in S3, loaded progressively:
- **Stage 1:** Name + 1-line description (always in context)
- **Stage 2:** Scope, preconditions, constraints (on skill selection)
- **Stage 3:** Full procedure, examples, tool bindings (on execution)

FinAgent skills: `trade_execution.md`, `market_briefing.md` → see `personal-finance-agent/skills/`

### §5 — Protocol Externalization
Replaces brittle ad-hoc API calls with **MCP (Model Context Protocol)** — typed, schema-validated contracts:
```json
{
  "tool": "alpaca_get_positions",
  "status": "success | error | rate_limited",
  "data": { "...": "typed payload" },
  "metadata": { "timestamp": "...", "latency_ms": 142 }
}
```

FinAgent MCPs: Alpaca (trading), Polygon.io (market data), Plaid (account aggregation), Experian (credit)

### §6 — Harness Engineering
The unification layer — does not add intelligence, it **governs execution**:
1. Retrieve memory (DynamoDB — all 4 tiers)
2. Select and load skill (progressive disclosure from S3)
3. Reason with Bedrock (Claude 3.5 Sonnet)
4. Execute MCP tools
5. Approval gate for irreversible actions (SNS → user confirms)
6. Write episodic memory
7. Respond

---

## Sample Implementation: FinAgent (Personal Finance Agent)

This folder contains a complete, deployable implementation of the paper's framework applied to personal finance. Every concept from the paper maps directly to production code.

| Paper Concept | FinAgent Implementation |
|--------------|------------------------|
| Memory (§3) | `personal-finance-agent/memory/ddb_memory.py` — DynamoDB 4-tier store |
| Skills (§4) | `personal-finance-agent/skills/*.md` — trade execution, market briefing |
| Protocols (§5) | `personal-finance-agent/agent/agent_core.py` — Polygon.io, Alpaca, Plaid MCPs |
| Harness (§6) | `personal-finance-agent/agent/agent_core.py` — 7-step loop with SNS approval gates |
| Infrastructure | `personal-finance-agent/infrastructure/template.yaml` — AWS SAM deployment |

---

## Folder Structure

```
externalization-in-llm-agents/
├── README.md                                  ← You are here
├── QUICKSTART.md                              ← Setup and notebooks guide
├── requirements.txt                           ← Python dependencies
├── 2604.08224v1 - Externalization in LLM Agents.pdf
├── notebooks/
│   ├── fundamentals.ipynb                     ← Paper concepts, no code (start here)
│   ├── memory_skill_concepts.ipynb            ← Memory tiers + skill progressive disclosure
│   ├── harness_algorithms.ipynb               ← Harness loop + approval gates
│   └── externalization_vs_parametric.md       ← Parametric vs. externalized comparison
└── personal-finance-agent/                    ← Full working implementation
    ├── agent/
    │   └── agent_core.py                      ← Lambda handler + all MCP tools
    ├── design/
    │   ├── AGENT_SPECIFICATION.md             ← Complete architecture spec
    │   └── AWS_RESOURCES.md                   ← AWS resource reference
    ├── memory/
    │   └── ddb_memory.py                      ← Production DynamoDB memory
    ├── skills/
    │   ├── trade_execution.md                 ← Trade skill (SKILL.md format)
    │   └── market_briefing.md                 ← Briefing skill (SKILL.md format)
    └── infrastructure/
        └── template.yaml                      ← AWS SAM template (deploy-ready)
```

---

## Recommended Reading Order

1. **This README** — framework overview (5 min)
2. **`notebooks/fundamentals.ipynb`** — concepts before code (30 min)
3. **`notebooks/externalization_vs_parametric.md`** — why this matters (15 min)
4. **`personal-finance-agent/design/AGENT_SPECIFICATION.md`** — full design (30 min)
5. **`notebooks/memory_skill_concepts.ipynb`** — memory + skills in code (45 min)
6. **`notebooks/harness_algorithms.ipynb`** — harness loop + approval gates (60 min)
7. **`personal-finance-agent/agent/agent_core.py`** — production implementation (30 min)
