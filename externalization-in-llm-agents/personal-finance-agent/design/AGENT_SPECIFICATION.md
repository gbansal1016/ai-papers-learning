# Personal Finance Agent — System Specification
## Grounded in Externalization Theory (Zhou et al., 2026)

---

## 1. Design Philosophy

This agent is designed using the **externalization framework** from *Externalization in LLM Agents* (Zhou et al., 2026). The paper's central thesis: reliable LLM agency comes not from larger models alone, but from systematically relocating cognitive burdens into persistent, inspectable, reusable external structures.

Three cognitive burdens map directly onto this agent's design:

| Burden | Problem | Externalization | AWS Implementation |
|--------|---------|-----------------|-------------------|
| **Continuity** | Agent forgets user's financial history, goals, risk profile across sessions | Memory | DynamoDB (4-tier) |
| **Procedural consistency** | Agent re-derives how to analyze a portfolio, execute a trade, or assess credit health each time | Skills | SKILL.md files loaded via S3 |
| **Interaction reliability** | Fragile ad-hoc API calls to brokerages, credit services, market data | Protocols | MCP tools (Alpaca, Plaid, Polygon.io, Alpha Vantage, Experian) |
| **Coordination** | No mechanism to sequence, gate, observe, or recover multi-step workflows | Harness | AWS Agent Core + Strands SDK |

The model (Claude 3.5 Sonnet via Bedrock) stays fixed. What changes is the external cognitive infrastructure around it.

---

## 2. Agent Identity and Scope

**Name:** FinAgent — Personal Finance AI

**Role:** A proactive, always-on personal finance companion that manages portfolio monitoring, executes trades on instruction, tracks credit health, and surfaces daily market intelligence — all within a governed harness that requires human approval for irreversible financial actions.

**Core capabilities:**
- Monitor and analyze the user's investment portfolio (Alpaca for trading; Plaid for read-only aggregation of external accounts)
- Execute stock trades on explicit user instruction (approval-gated)
- Pull and track credit score changes over time (Experian Connect API)
- Deliver a curated daily market briefing (Polygon.io for quotes/news; Alpha Vantage for sector data)
- Answer natural language financial questions using the user's actual data
- Learn the user's risk tolerance, goals, and preferences across sessions

---

## 3. Externalized Memory — DynamoDB Schema

Following the paper's four memory types (§3.1), FinAgent externalizes all state into DynamoDB. The model never reconstructs user history from weights — it retrieves it.

### 3.1 Memory Tier Architecture

```
DynamoDB Table: finagent-memory-{userId}
Partition Key: memory_type  (WORKING | EPISODIC | SEMANTIC | PERSONAL)
Sort Key:      memory_id    (timestamp-based ULID)

GSI-1: userId-createdAt-index (query all memories for a user by time)
GSI-2: memory_type-relevance_score-index (retrieve top-K by relevance)
```

### 3.2 Four Memory Types

**WORKING CONTEXT** — current session state, active tasks, in-progress decisions
```json
{
  "memory_type": "WORKING",
  "memory_id": "01JWXYZ...",
  "userId": "gaurav@...",
  "session_id": "sess_abc",
  "content": {
    "current_intent": "analyze tech exposure in portfolio",
    "active_tool_calls": ["alpaca_get_positions"],
    "pending_approval": null,
    "context_window_summary": "User asked about NVDA concentration..."
  },
  "ttl": 86400
}
```

**EPISODIC MEMORY** — what happened: past trades, decisions, outcomes, reflections
```json
{
  "memory_type": "EPISODIC",
  "memory_id": "01JWXYZ...",
  "userId": "gaurav@...",
  "event_type": "TRADE_EXECUTED | ANALYSIS_PERFORMED | CREDIT_CHECKED | MARKET_BRIEFING",
  "content": {
    "description": "User bought 10 shares NVDA at $875 on 2026-06-18",
    "tool_calls": ["alpaca_place_order"],
    "outcome": "success",
    "reflection": "User initiated after NVDA earnings beat. Part of AI infrastructure thesis."
  },
  "embedding_key": "s3://finagent-embeddings/episodic/01JWXYZ",
  "created_at": "2026-06-18T14:23:00Z"
}
```

**SEMANTIC KNOWLEDGE** — stable facts: domain knowledge, market concepts, how things work
```json
{
  "memory_type": "SEMANTIC",
  "memory_id": "01JWXYZ...",
  "userId": "gaurav@...",
  "topic": "options_greeks | pe_ratio | credit_utilization",
  "content": {
    "concept": "credit_utilization",
    "definition": "Ratio of credit used to total available credit. Below 30% is healthy.",
    "relevance": "User's current utilization is 42% — above threshold"
  }
}
```

**PERSONALIZED MEMORY** — who the user is: risk profile, goals, preferences, patterns
```json
{
  "memory_type": "PERSONAL",
  "memory_id": "01JWXYZ...",
  "userId": "gaurav@...",
  "content": {
    "risk_tolerance": "moderate-aggressive",
    "investment_horizon": "10+ years",
    "goals": ["retirement at 55", "passive income from dividends"],
    "sector_preferences": ["technology", "healthcare"],
    "sectors_to_avoid": ["tobacco", "weapons"],
    "preferred_briefing_time": "07:00 PST",
    "trade_approval_threshold_usd": 500,
    "credit_score_baseline": 742,
    "monthly_budget_targets": {"housing": 3000, "dining": 400}
  },
  "last_updated": "2026-06-18T00:00:00Z"
}
```

### 3.3 Memory Retrieval Strategy

On each agent invocation, the harness performs **selective retrieval** (not full context load):
1. Always inject PERSONAL memory (user profile) — it's small and always relevant
2. Inject WORKING context for active session
3. Retrieve top-3 EPISODIC memories by semantic similarity to current intent
4. Retrieve relevant SEMANTIC knowledge based on entities in the user's query

This converts "recall from weights" into "recognition from a curated retrieve" — the paper's core memory transformation.

---

## 4. Externalized Skills — Capability Packages

Following the paper's §4 framework, skills package procedural expertise into SKILL.md files stored in S3, loaded progressively by the harness.

### Skill Registry (S3: finagent-skills/)

| Skill | Trigger | Loads from |
|-------|---------|-----------|
| `portfolio_analysis` | "how is my portfolio doing", "analyze my holdings" | s3://finagent-skills/portfolio_analysis.md |
| `stock_research` | "tell me about AAPL", "should I buy NVDA" | s3://finagent-skills/stock_research.md |
| `trade_execution` | "buy X shares of Y", "sell my Z position" | s3://finagent-skills/trade_execution.md |
| `credit_health` | "what's my credit score", "how can I improve my credit" | s3://finagent-skills/credit_health.md |
| `market_briefing` | (background scheduler, 7am daily) | s3://finagent-skills/market_briefing.md |
| `budget_analysis` | "how am I doing on budget", "spending breakdown" | s3://finagent-skills/budget_analysis.md |

### Progressive Disclosure (from paper §4.3.3)

The harness loads skills in three stages to manage context budget:

```
Stage 1 (always in context):  Skill name + 1-line description
Stage 2 (on skill selection): Skill scope, preconditions, constraints
Stage 3 (on execution):       Full procedure, examples, tool bindings
```

### Example: trade_execution Skill (normative constraints component)
```
SKILL: trade_execution
PRECONDITIONS:
  - User has explicitly named a ticker and quantity
  - Alpaca account is connected and verified
  - Trade value does not exceed user's approval_threshold without explicit confirmation

OPERATIONAL PROCEDURE:
  1. Parse intent: extract ticker, quantity, direction (buy/sell), order type
  2. Fetch current price from market data MCP
  3. Calculate total value and compare to approval_threshold
  4. Present trade summary to user and request confirmation
  5. Only after EXPLICIT confirmation: call alpaca_place_order
  6. Write episodic memory: trade details, outcome, user rationale
  7. Update portfolio summary in SEMANTIC memory

NORMATIVE CONSTRAINTS:
  - NEVER execute a trade without step-4 confirmation, regardless of instruction phrasing
  - NEVER execute trades outside market hours without flagging this to the user
  - NEVER execute trades that would concentrate >30% of portfolio in one position without warning

DECISION HEURISTICS:
  - If trade value > 3x user's typical trade size, ask if this is intentional
  - If trade conflicts with user's sector_to_avoid list, flag before confirming
```

---

## 5. Externalized Protocols — MCP Tool Connectors

Following the paper's §5 framework, all external service interactions use **MCP (Model Context Protocol)** — explicit machine-readable contracts that replace brittle ad-hoc API calls.

### 5.1 MCP Tool Registry

#### Alpaca MCP (Stock Trading — Primary)
```
Provider: Alpaca Markets (api.alpaca.markets)
Auth: API Key + Secret via SSM Parameter Store
Mode: Paper trading for dev, live trading for prod

Tools exposed:
  alpaca_get_account       → account equity, buying power, status
  alpaca_get_positions     → all open positions with P&L
  alpaca_get_orders        → recent order history
  alpaca_place_order       → submit market/limit/stop order [APPROVAL GATED]
  alpaca_cancel_order      → cancel pending order [APPROVAL GATED]
  alpaca_get_portfolio_history → equity curve over time
```

#### Plaid MCP (Account Aggregation — Read-Only)
```
Provider: Plaid (plaid.com) — official, FCRA-compliant API
Auth: client_id + secret via SSM; per-user access tokens via Plaid Link OAuth flow
Note: Replaces any Robinhood direct integration. Robinhood has no official API
      (shut down 2019). Plaid's Investments product reads holdings from Robinhood
      and 10,000+ other institutions without violating any ToS.

Tools exposed:
  plaid_get_holdings       → investment holdings across all linked accounts (read-only)
  plaid_get_transactions   → transaction history across linked accounts
  plaid_get_account_balances → real-time balances for linked accounts

Constraint: Plaid is read-only. All order execution routes through Alpaca only.
```

#### Polygon.io MCP (Market Data — Primary)
```
Provider: Polygon.io (polygon.io) — official licensed market data API
Auth: API key via SSM Parameter Store
Tiers: Free (5 calls/min, previous-day data only) | Starter ($29/mo, real-time)
Note: Replaces yfinance, which is an unofficial Yahoo Finance scraper that violates
      Yahoo's ToS for commercial use and breaks unpredictably. Polygon.io is an
      officially licensed data provider with a stable, versioned REST API.

Tools exposed:
  polygon_get_quote        → real-time last trade price, volume, 52-week range
  polygon_get_news         → top N recent news articles for a ticker
  polygon_get_market_snapshot → current price + change for indices (SPY, QQQ, DIA, VIX)
  polygon_get_analyst_ratings → consensus buy/hold/sell + price targets (Starter+)
  polygon_get_earnings_calendar → upcoming earnings for user's holdings
```

#### Alpha Vantage MCP (Sector Data + Fundamentals)
```
Provider: Alpha Vantage (alphavantage.co)
Auth: API key via SSM Parameter Store

⚠️  FREE TIER LIMITATION: 25 API calls/day, 5 requests/minute.
    A daily briefing across 10 holdings exhausts the free tier in one run.
    Production use requires a premium plan (~$50/month) or switch sector data
    to Polygon.io (included in Starter tier).

Tools exposed:
  av_get_fundamentals       → P/E, EPS, revenue, debt-to-equity (free tier ok)
  av_get_sector_performance → sector rotation snapshot (1 call/day — use this sparingly)
  av_get_top_gainers_losers → daily movers
```

#### Experian MCP (Credit Score)
```
Provider: Experian Connect API (developer.experian.com)
Auth: OAuth2 client credentials via SSM
Note: Requires Experian developer account. NerdWallet/Credit Karma have no public APIs.
      Experian Connect is the most accessible programmatic credit score API.

Tools exposed:
  experian_get_credit_score     → VantageScore 3.0 + FICO
  experian_get_credit_report    → tradelines, accounts, inquiries
  experian_get_score_factors    → top factors helping/hurting score
  experian_get_score_history    → score trend over 12 months
```

### 5.2 Protocol Design Pattern

All MCP tools follow a **Structured Contract** pattern (paper §5.1):

```python
# Every MCP tool returns a typed, schema-validated response
{
  "tool": "alpaca_get_positions",
  "status": "success | error | rate_limited",
  "data": { ... },           # typed payload
  "metadata": {
    "timestamp": "...",
    "latency_ms": 142,
    "source": "alpaca_v2_api"
  },
  "error": null              # or structured error with retry guidance
}
```

---

## 6. Harness Engineering — AWS Agent Core + Strands

The harness is the unification layer (paper §6) — it does not add intelligence, it governs execution.

### 6.1 Harness Components

```
┌─────────────────────────────────────────────────────────────┐
│                    FINAGENT HARNESS                          │
│                  (AWS Agent Core + Strands)                  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   MEMORY     │  │   SKILLS     │  │    PROTOCOLS     │   │
│  │  (DynamoDB)  │  │   (S3 SKILL  │  │   (MCP Tools)    │   │
│  │              │  │    files)    │  │                  │   │
│  │ • Working    │  │ • Portfolio  │  │ • Alpaca MCP     │   │
│  │ • Episodic   │  │ • Trade Exec │  │ • Plaid MCP      │   │
│  │ • Semantic   │  │ • Research   │  │ • Polygon.io MCP │   │
│  │ • Personal   │  │ • Credit     │  │ • Alpha Vantage  │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘   │
│         │                 │                    │             │
│  ┌──────▼─────────────────▼────────────────────▼──────────┐  │
│  │              STRANDS AGENT LOOP                        │  │
│  │  1. Retrieve memory  →  2. Select skill  →  3. Plan    │  │
│  │  4. Execute MCP tools  →  5. Validate output           │  │
│  │  6. Approval gate (financial actions)                  │  │
│  │  7. Write episodic memory  →  8. Respond to user       │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  OBSERV-     │  │  APPROVAL    │  │  BACKGROUND      │   │
│  │  ABILITY     │  │  GATES       │  │  SCHEDULER       │   │
│  │ (CloudWatch) │  │ (SNS → User) │  │ (EventBridge)    │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Agent Loop (Strands Control Flow)

```python
# Strands agent loop — each invocation follows this sequence
async def finagent_loop(user_message, user_id, session_id):

    # Step 1: Memory retrieval (convert recall → recognition)
    memory = await retrieve_memory(user_id, user_message)
    # Injects: full PERSONAL profile + top-3 EPISODIC + relevant SEMANTIC

    # Step 2: Skill selection (progressive disclosure)
    skill = await select_skill(user_message, memory)
    skill_detail = await load_skill_stage(skill, stage=2)  # load constraints first

    # Step 3: Agent reasoning (Bedrock Claude 3.5 Sonnet)
    plan = await bedrock_reason(
        system=build_system_prompt(memory, skill_detail),
        user=user_message
    )

    # Step 4: Tool execution loop
    for tool_call in plan.tool_calls:
        if requires_approval(tool_call):            # trades, large actions
            await request_human_approval(tool_call, user_id)
            # Halts here — resumes only on user confirmation
        result = await execute_mcp_tool(tool_call)
        log_to_cloudwatch(tool_call, result)

    # Step 5: Write episodic memory
    await write_episodic_memory(user_id, {
        "intent": user_message,
        "skill_used": skill,
        "tools_called": plan.tool_calls,
        "outcome": plan.result,
        "reflection": plan.self_reflection
    })

    # Step 6: Respond
    return plan.response
```

### 6.3 Human Oversight & Approval Gates

The harness enforces **mandatory approval** before any irreversible financial action (paper §6.2.3):

```
Approval-required actions:
  • Any stock buy/sell order (regardless of size)
  • Portfolio rebalancing suggestions > $1,000 total
  • Canceling existing orders

Approval flow:
  Agent → SNS notification → user's phone/email
  User replies CONFIRM or CANCEL within 5 minutes
  Harness resumes or discards the pending action

Never approval-gated (read-only):
  • Fetching portfolio positions
  • Getting credit score
  • Market data queries
  • Memory reads
```

### 6.4 Background Scheduler — Daily Market Briefing

EventBridge Scheduler triggers daily at 7:00 AM PST:

```
EventBridge Rule → Lambda (market_briefing_job) →
  1. Fetch top 5 market news (Polygon.io MCP)
  2. Fetch S&P/NASDAQ/DOW snapshot (Polygon.io MCP)
  3. Fetch sector performance (Alpha Vantage MCP — 1 call/day, within free tier)
  4. Check earnings calendar for user's holdings (Polygon.io MCP)
  5. Run market_briefing skill to compose summary
  6. Write to EPISODIC memory
  7. Push to user via SNS/email
```

### 6.5 Context Budget Management

Following paper §6.2.6, the harness manages token budget explicitly:

```
Total context budget: 100,000 tokens (Claude 3.5 Sonnet)

Allocation:
  System prompt + skill:         ~3,000 tokens  (3%)
  PERSONAL memory:               ~1,000 tokens  (1%)
  Top-3 EPISODIC memories:       ~2,000 tokens  (2%)
  SEMANTIC knowledge:            ~1,500 tokens  (1.5%)
  Current conversation:          ~5,000 tokens  (5%)
  Tool call results:             ~8,000 tokens  (8%)
  Reserved for reasoning:       ~79,500 tokens  (79.5%)

If budget exceeded: compress older episodic memories via summarization
```

### 6.6 Observability (CloudWatch)

Every agent loop emits structured logs:
```json
{
  "event": "agent_loop_complete",
  "userId": "...",
  "sessionId": "...",
  "skill_selected": "portfolio_analysis",
  "tools_called": ["alpaca_get_positions", "polygon_get_market_snapshot"],
  "approval_required": false,
  "memory_retrieved_count": 4,
  "bedrock_input_tokens": 4821,
  "bedrock_output_tokens": 892,
  "total_latency_ms": 3241,
  "outcome": "success"
}
```

---

## 7. System Architecture Diagram

```
USER (web / mobile / voice)
       │
       ▼
API Gateway (HTTPS)
       │
       ▼
Cognito (auth) ──► Lambda: FinAgent Handler
                          │
              ┌───────────┼────────────────────────┐
              ▼           ▼                         ▼
        AWS Agent     DynamoDB                  S3
          Core /      (Memory)              (Skills SKILL.md)
          Strands     ├─ WORKING             ├─ portfolio_analysis.md
              │       ├─ EPISODIC            ├─ trade_execution.md
              │       ├─ SEMANTIC            ├─ credit_health.md
              │       └─ PERSONAL            └─ market_briefing.md
              │
              ├──── MCP: Alpaca ──────► Alpaca API (paper-api.alpaca.markets / live)
              ├──── MCP: Plaid ───────► Plaid API (read-only account aggregation)
              ├──── MCP: Polygon.io ──► polygon.io (licensed market data, real-time)
              ├──── MCP: Alpha Vantage ► alphavantage.co (sector data, 25 calls/day free)
              └──── MCP: Experian ────► Experian Connect API (OAuth2 credit scores)
                                              │
                    ┌─────────────────────────┤
                    ▼                         ▼
              Amazon Bedrock           CloudWatch
           (Claude 3.5 Sonnet)        (observability)
                    │
                    ▼
             SNS → User notification
             (trade approval gates)

BACKGROUND (EventBridge Scheduler, 7am PST daily):
  Lambda: market_briefing_job
    → Yahoo Finance MCP → Alpha Vantage MCP
    → market_briefing skill
    → write EPISODIC memory
    → SNS push to user
```

---

## 8. AWS Services Summary

| Service | Role | Tier |
|---------|------|------|
| Amazon Bedrock (Claude 3.5 Sonnet) | LLM reasoning core | On-demand |
| AWS Agent Core | Agent runtime + memory management | GA |
| AWS Strands SDK | Agent orchestration loop | Open source |
| DynamoDB | All 4 memory tiers (on-demand capacity) | Serverless |
| S3 | Skill file storage + embedding store | Standard |
| Lambda | Agent handler + background jobs | Serverless |
| API Gateway | User-facing REST API | Managed |
| Cognito | User authentication | Managed |
| EventBridge Scheduler | Daily market briefing trigger | Managed |
| SNS | Approval gate notifications + briefing delivery | Managed |
| CloudWatch | Structured logs + metrics + alarms | Managed |
| SSM Parameter Store | API keys (Alpaca, Plaid, Polygon.io, Alpha Vantage, Experian) | Standard (free) |
| SQS | Async approval queue (pending trade approvals) | Standard |

---

## 9. Build Sequence

| Phase | Weeks | Deliverable |
|-------|-------|-------------|
| 1 — Memory layer | 1–2 | DynamoDB schema + read/write helpers, PERSONAL memory seeded |
| 2 — Skill loading | 2–3 | S3 skill files, progressive disclosure loader |
| 3 — MCP tools | 3–5 | Alpaca + Yahoo Finance MCP wired and tested |
| 4 — Agent loop | 5–6 | Strands loop: retrieve memory → select skill → call tools → write memory |
| 5 — Harness controls | 6–7 | Approval gates, CloudWatch observability, context budget manager |
| 6 — Background job | 7–8 | EventBridge → daily market briefing → SNS push |
| 7 — Credit layer | 8–9 | Experian MCP + credit_health skill |
| 8 — Beta | 9–10 | End-to-end: ask questions, get briefings, execute paper trades |

---

## 10. Key Design Decisions & Trade-offs

**Why DynamoDB over a vector store for memory?**
DynamoDB handles structured memory (PERSONAL, WORKING) well and is serverless. For semantic similarity retrieval (EPISODIC lookup), store embeddings in S3 and use a Lambda + cosine similarity approach at MVP scale. At growth stage, add Amazon OpenSearch Serverless for vector search.

**Why Alpaca for trading + Plaid for account aggregation?**
Alpaca has an official REST API with paper trading mode — the only option for programmatic US equity trading with a clean developer experience. Robinhood shut down its official API in 2019; `robin_stocks` is an unofficial scraper that violates Robinhood's ToS and breaks without notice. Instead, use **Plaid's Investments product** to read holdings from Robinhood (and 10,000+ other institutions) in a ToS-compliant, FCRA-regulated way. All order execution goes through Alpaca only.

**Why Polygon.io over yfinance / Yahoo Finance?**
`yfinance` is an unofficial scraper of Yahoo Finance's private endpoints. It violates Yahoo's ToS for commercial use, has no SLA, and breaks unpredictably when Yahoo changes its API. **Polygon.io** is a licensed market data provider with a stable versioned REST API, proper attribution, and a free tier (5 req/min, previous-day data) plus a Starter plan at $29/month for real-time. Use Polygon.io for all stock quotes, news, and index snapshots.

**Why Experian over NerdWallet/Credit Karma?**
Neither NerdWallet nor Credit Karma exposes a programmatic credit score API. Experian's Connect API is the most accessible developer-facing credit data API. Alternatively, Plaid's Credit Report product can pull scores from the bureaus — evaluate both.

**Approval gate design philosophy**
The paper warns about harness systems that are either too permissive (agent acts without oversight) or too restrictive (approval gate kills usability). The design uses a tiered threshold: trades below $500 show a 10-second inline confirmation banner; trades above $500 require email/SMS confirmation. Read-only actions are never gated.
