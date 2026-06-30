# SKILL: market_briefing
# Version: 1.0 | Author: FinAgent System

## Capability Boundary
Generates a structured daily market briefing personalized to the user's portfolio and interests.
Triggered automatically at 7am PST by EventBridge Scheduler, OR on-demand by the user.

## Scope of Applicability
- Scheduled trigger: EventBridge daily job
- On-demand: "give me today's market update", "what's the market doing", "morning briefing"

## Preconditions
- Polygon.io and Alpha Vantage MCPs are available
- User's PERSONAL memory is loaded (to personalize news filtering)
- User's positions are accessible (to highlight relevant earnings/news)

## Operational Procedure

### Step 1 — Fetch market snapshot
Call polygon_get_market_snapshot() → S&P 500, NASDAQ-100, DOW, VIX current levels + % change

### Step 2 — Fetch top 5 market headlines
Call polygon_get_news("market", count=5) → broad market news
Filter by relevance to user's sector_preferences (from PERSONAL memory)

### Step 3 — Fetch sector rotation
Call av_get_sector_performance() → which sectors are up/down today

### Step 4 — Portfolio-specific highlights
For each position in the user's portfolio (from last alpaca_get_positions cache or fresh call):
  - Check if earnings announcement today or this week
  - Flag any position with single-day move > 3%
  - Note analyst rating changes if available

### Step 5 — Compose briefing

Format the output as:

```
Good morning! Here's your FinAgent market briefing for [DATE].

MARKETS:
  S&P 500:  4,892.10  (+0.42%)
  NASDAQ:   17,241.30 (+0.71%)
  DOW:      39,112.50 (-0.08%)
  VIX:      14.2 (low volatility)

TOP 5 HEADLINES:
  1. [Title] — [Publisher]
  2. ...

SECTORS TODAY:
  Leading:  Technology (+1.2%), Healthcare (+0.8%)
  Lagging:  Energy (-0.9%), Utilities (-0.5%)

YOUR PORTFOLIO HIGHLIGHTS:
  • NVDA earnings report tomorrow — consensus EPS $5.12
  • AAPL up 2.3% today after analyst upgrade at Goldman Sachs
  • No other notable events for your holdings

Questions? Ask me anything about the market or your portfolio.
```

### Step 6 — Write to episodic memory
Store briefing summary as EPISODIC event (type: MARKET_BRIEFING)
Include: date, market levels, key headlines, user's portfolio alerts

### Step 7 — Deliver
For scheduled runs: push via SNS to user's registered email/phone
For on-demand: return as agent response

## Decision Heuristics
- If VIX > 25: prepend a volatility warning
- If user's portfolio is down > 2% on the day: lead with portfolio impact, not general news
- If a holding has earnings this week: always include it in highlights regardless of relevance score
- If a headline touches user's sectors_to_avoid: exclude from the briefing

## Normative Constraints
- Never present more than 5 headlines — brevity is core to the skill
- Never include speculative price predictions as facts
- Always timestamp the briefing with the data freshness time
- If market data fetch fails: clearly state data unavailability rather than presenting stale data

## Examples

Scheduled trigger example (EventBridge):
  Input: system event, user_id: "gaurav@..."
  Action: fetch all data, compose briefing, push via SNS

On-demand example:
  User: "What happened in the market today?"
  → Run steps 1–5, return briefing inline in conversation
