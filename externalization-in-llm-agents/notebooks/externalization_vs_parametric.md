# Externalization vs. Parametric-Only Agents

## What is a Parametric Agent?

A **parametric agent** relies entirely on knowledge baked into the model's weights during training and on the current context window. There is no persistent external state — every session starts from zero.

```
PARAMETRIC AGENT:
  User message → [Context Window: history + knowledge + instructions] → LLM → Response
                  └── Everything lives here ──┘
                      Forgotten next session
```

## What is an Externalized Agent?

An **externalized agent** (Zhou et al., 2026) relocates cognitive burdens into persistent, inspectable, reusable external structures. The model handles reasoning only.

```
EXTERNALIZED AGENT:
  User message → Harness retrieves → [Memory + Skills + Protocols] → LLM (reasoning) → Response
                                      └──────── persists ─────────┘
                                           Survives next session
```

---

## Head-to-Head Comparison

| Dimension | Parametric Agent | Externalized Agent |
|-----------|------------------|--------------------|
| **User memory** | Re-explained every session | Persisted in DynamoDB PERSONAL tier |
| **Procedure consistency** | Re-derived from weights (varies) | Loaded from SKILL.md (always same) |
| **Error handling** | Unpredictable | Typed MCPResponse envelope |
| **Human oversight** | Ad-hoc, or none | Formal approval gates |
| **Debuggability** | "What did the model think?" | Inspect DynamoDB, CloudWatch logs |
| **Cost per session** | Full re-context every time | Selective retrieve — cheaper |
| **Learning over time** | Requires fine-tuning | Episodic → semantic promotion |
| **Procedure versioning** | Change the prompt | Update SKILL.md in S3 |
| **Scale** | Single model update | Each component scales independently |

---

## When Parametric is Fine

Externalization adds infrastructure overhead. It's overkill for:

- **Single-turn Q&A** — no memory needed, session is self-contained
- **Stateless tools** — code generation, text transformation, translation
- **Prototype / throw-away scripts** — cost of infrastructure exceeds benefit
- **Fully read-only tasks** — no approval gates needed, no state to persist

## When You Need Externalization

You need externalization when you have:

- **Session continuity** — user shouldn't re-explain their risk tolerance every time
- **Irreversible actions** — financial trades, medical orders, legal filings need approval gates
- **Procedural consistency** — the same task (trade execution, credit check) must follow the same exact steps every time
- **Multi-API orchestration** — brittle ad-hoc calls become a reliability problem at scale
- **Auditability** — regulated domains (finance, health) require inspectable logs

---

## The FinAgent Example

FinAgent is a concrete demonstration of why externalization matters for personal finance:

| Without externalization | With externalization (FinAgent) |
|------------------------|--------------------------------|
| "What's my risk tolerance?" → user must re-explain | Loaded from PERSONAL memory tier |
| Trade procedure re-derived each session → inconsistent | Loaded from `trade_execution.md` in S3 |
| `requests.get("https://api.alpaca.markets/...")` → brittle | `alpaca_get_positions()` → typed MCPResponse |
| Agent places order immediately | Approval gate: SNS → user confirms |
| No audit trail | CloudWatch structured logs + DynamoDB episodic memory |

---

## Key Insight from the Paper

> The model doesn't need to be smarter. The infrastructure around the model needs to be more reliable.

The four externalizations — memory, skills, protocols, harness — don't improve the model's reasoning capability. They make the *system* around the model reliable, consistent, observable, and correctable. That's the core contribution of Zhou et al. (2026).
