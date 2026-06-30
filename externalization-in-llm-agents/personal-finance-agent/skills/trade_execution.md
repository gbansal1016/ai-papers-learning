# SKILL: trade_execution
# Version: 1.0 | Author: FinAgent System

## Capability Boundary
This skill governs how FinAgent handles any user request to buy, sell, or modify stock positions.
It does NOT cover options, futures, crypto, or fixed income — those are out of scope.

## Scope of Applicability
Trigger when the user's message contains explicit trade intent:
- "buy N shares of TICKER"
- "sell my TICKER position"
- "place an order for..."
- "get out of TICKER"
- "add to my TICKER position"

Do NOT trigger on research questions ("should I buy AAPL?") — route those to stock_research skill.

## Preconditions
1. Alpaca account is connected and verified (check alpaca_get_account status == "ACTIVE")
2. User has sufficient buying power for buy orders
3. User owns the position for sell orders
4. Market is open, OR user has been informed it's after-hours and confirmed

## Operational Procedure

### Step 1 — Parse intent
Extract from the user's message:
- Ticker symbol (normalize to uppercase)
- Quantity (shares or dollar amount — if dollar amount, calculate shares)
- Direction (buy or sell)
- Order type (market unless user specifies limit)
- Limit price (if order type is limit)

If any required field is ambiguous, ASK before proceeding. Never guess ticker symbols.

### Step 2 — Fetch current data
Call polygon_get_quote(symbol) to get:
- Current price (real-time on Starter tier; previous close on free tier)
- Open/high/low/close, change %
Call alpaca_get_account() to verify buying power.
For sells: call alpaca_get_positions() to confirm user holds the position.

### Step 3 — Calculate trade value
total_value = quantity × current_price
If total_value > user's trade_approval_threshold_usd (from PERSONAL memory):
  → Escalate to full SNS approval flow

### Step 4 — Concentration check (normative constraint)
Calculate: new_position_value / total_portfolio_value
If result > 30%:
  → Warn user: "This trade would put 32% of your portfolio in TICKER. Do you want to proceed?"
  → Wait for explicit confirmation

### Step 5 — Sector check (normative constraint)
Check ticker's sector against user's sectors_to_avoid list (from PERSONAL memory).
If match found:
  → Inform user: "TICKER is in [sector], which you've previously said you want to avoid."
  → Wait for explicit override confirmation

### Step 6 — Present trade summary (MANDATORY)
Always show this before calling alpaca_place_order:

```
Trade Summary:
  Action:     BUY / SELL
  Ticker:     AAPL
  Quantity:   10 shares
  Price:      ~$189.50 (market order)
  Total:      ~$1,895.00
  Account:    Alpaca Paper Trading

Reply CONFIRM to proceed or CANCEL to abort.
```

### Step 7 — Execute (only after confirmation)
Call alpaca_place_order(symbol, qty, side, order_type, limit_price)
Present the order confirmation: order_id, status, submitted_at.

### Step 8 — Write episodic memory
Record: ticker, qty, side, price, user's stated rationale (if given), outcome.
Update PERSONAL memory: increment trade_count, update last_trade_date.

## Decision Heuristics
- If trade quantity is >3x the user's typical trade size → ask "Is this intentional?"
- If market is closed and user places a market order → inform them it will execute at next open
- If the same ticker was sold in the last 30 days → note wash sale risk for taxable accounts
- Never suggest trades — only execute what the user explicitly requests

## Normative Constraints (non-negotiable)
- NEVER call alpaca_place_order without Step 6 confirmation
- NEVER execute a trade if the Alpaca account status is not "ACTIVE"
- NEVER interpret an ambiguous ticker — if unclear, ask
- NEVER place orders larger than the account's buying_power

## Examples

Good trigger:
  User: "Buy 5 shares of Microsoft"
  → Extract: MSFT, 5 shares, buy, market → proceed with procedure

Bad trigger (should route to stock_research instead):
  User: "What do you think about buying Apple?"
  → This is research, not execution. Route to stock_research skill.

Counter-example (proceed with caution):
  User: "Go all in on NVDA"
  → "All in" is ambiguous. Clarify quantity. Then flag concentration risk.
