"""
FinAgent — Personal Finance AI Agent
Harness implementation using AWS Strands SDK + Amazon Bedrock

Externalization architecture (Zhou et al., 2026):
  Memory    → DynamoDB (4 tiers: WORKING, EPISODIC, SEMANTIC, PERSONAL)
  Skills    → S3 SKILL.md files (progressively disclosed)
  Protocols → MCP tools (Alpaca, Plaid, Polygon.io, Alpha Vantage)
  Harness   → This file — Strands agent loop + approval gates + observability

Market data: Polygon.io (polygon.io) — official licensed API.
  NOT yfinance — yfinance is an unofficial Yahoo Finance scraper that violates
  Yahoo's ToS for commercial use and breaks unpredictably.
"""

import json
import os
import time
import logging
import boto3
from datetime import datetime, timezone
from typing import Optional
from boto3.dynamodb.conditions import Attr

# AWS Strands SDK (aws-strands)
from strands import Agent, tool
from strands.models import BedrockModel

from memory.ddb_memory import MemoryStore
from skills.skill_loader import SkillLoader

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# -- AWS clients --------------------------------------------------------------
bedrock_client = boto3.client("bedrock-runtime", region_name=os.environ["AWS_REGION"])
sns            = boto3.client("sns")
ses            = boto3.client("ses", region_name=os.environ["AWS_REGION"])
sqs            = boto3.client("sqs")
cloudwatch     = boto3.client("cloudwatch")
ssm            = boto3.client("ssm")

BEDROCK_MODEL_ID   = "us.anthropic.claude-sonnet-4-6"
APPROVAL_TOPIC_ARN = os.environ["APPROVAL_SNS_TOPIC_ARN"]
SKILLS_BUCKET      = os.environ["SKILLS_S3_BUCKET"]
MEMORY_TABLE       = os.environ["MEMORY_DDB_TABLE"]

# -- MCP Tool definitions (bound at runtime by Strands) -----------------------

@tool
def alpaca_get_account() -> dict:
    """Get Alpaca brokerage account equity, buying power, and status."""
    api     = _alpaca_client()
    account = api.get_account()
    return {
        "equity":          float(account.equity),
        "buying_power":    float(account.buying_power),
        "cash":            float(account.cash),
        "portfolio_value": float(account.portfolio_value),
        "status":          account.status,
    }

@tool
def alpaca_get_quote(symbol: str) -> dict:
    """
    PREFERRED tool for live stock prices. Always call this first for any question about
    a stock's current price, bid/ask spread, or last trade. Uses Alpaca Market Data API
    which is free and reliable. Only fall back to polygon_get_quote if this fails.
    Args:
        symbol: Ticker symbol e.g. 'AAPL', 'TSLA', 'ADBE'
    """
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockLatestQuoteRequest, StockLatestTradeRequest

    key    = _get_secret("/finagent/alpaca_api_key")
    secret = _get_secret("/finagent/alpaca_secret_key")
    client = StockHistoricalDataClient(key, secret)

    symbol = symbol.upper()
    quote  = client.get_stock_latest_quote(StockLatestQuoteRequest(symbol_or_symbols=symbol))
    trade  = client.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols=symbol))

    q = quote[symbol]
    t = trade[symbol]
    return {
        "symbol":     symbol,
        "last_price": float(t.price),
        "last_size":  int(t.size),
        "bid":        float(q.bid_price),
        "ask":        float(q.ask_price),
        "bid_size":   int(q.bid_size),
        "ask_size":   int(q.ask_size),
        "timestamp":  str(t.timestamp),
    }

@tool
def alpaca_get_positions() -> list:
    """Get all open positions with current P&L."""
    api       = _alpaca_client()
    positions = api.get_all_positions()
    return [
        {
            "symbol":          p.symbol,
            "qty":             float(p.qty),
            "avg_entry_price": float(p.avg_entry_price),
            "current_price":   float(p.current_price),
            "market_value":    float(p.market_value),
            "unrealized_pl":   float(p.unrealized_pl),
            "unrealized_plpc": float(p.unrealized_plpc),
            "side":            p.side,
        }
        for p in positions
    ]

@tool
def alpaca_place_order(symbol: str, qty: float, side: str, user_id: str,
                       order_type: str = "market",
                       limit_price: Optional[float] = None) -> dict:
    """
    Request a stock order via Alpaca. ALWAYS requires human approval before execution.
    Sends an approval email to the user and returns a pending approval_id.
    The user must approve via email link before the order is placed.
    After approval, call execute_approved_trade(approval_id, user_id) to place it.
    Args:
        symbol:      Ticker symbol (e.g. 'AAPL')
        qty:         Number of shares
        side:        'buy' or 'sell'
        user_id:     User's email — get from user profile in system prompt
        order_type:  'market' or 'limit'
        limit_price: Required if order_type is 'limit'
    """
    trade_detail = {
        "symbol":      symbol.upper(),
        "qty":         qty,
        "side":        side.lower(),
        "order_type":  order_type,
        "limit_price": limit_price,
    }
    approval_id = request_human_approval("alpaca_place_order", trade_detail, user_id)
    return {
        "status":      "pending_approval",
        "approval_id": approval_id,
        "message":     f"Approval email sent to {user_id}. Click the link in your email to approve or cancel the {side.upper()} of {qty} {symbol.upper()}. Then say 'execute my approved trade {approval_id}'.",
    }

@tool
def execute_approved_trade(approval_id: str, user_id: str) -> dict:
    """
    Execute a trade that has been approved by the user via email.
    Only call this after the user confirms they have approved the trade.
    Args:
        approval_id: The approval ID returned by alpaca_place_order
        user_id:     User's email — get from user profile in system prompt
    """
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
    from alpaca.trading.enums   import OrderSide, TimeInForce

    # Load approval record from DynamoDB
    ddb   = boto3.resource("dynamodb")
    table = ddb.Table(os.environ["APPROVALS_TABLE"])
    resp  = table.get_item(Key={"approval_id": approval_id})
    item  = resp.get("Item")

    if not item:
        return {"error": f"Approval record {approval_id} not found."}
    if item.get("decision") == "cancel":
        return {"status": "cancelled", "message": "Trade was cancelled by the user."}
    if item.get("decision") != "approve":
        return {"status": "pending", "message": "Trade not yet approved. Ask the user to click the approval link in their email."}

    # Execute the approved trade
    detail = item.get("trade_detail", {})
    api    = _alpaca_client()
    _side  = OrderSide.BUY if detail["side"] == "buy" else OrderSide.SELL

    if detail.get("order_type") == "limit" and detail.get("limit_price"):
        req = LimitOrderRequest(
            symbol=detail["symbol"], qty=detail["qty"], side=_side,
            time_in_force=TimeInForce.DAY, limit_price=detail["limit_price"],
        )
    else:
        req = MarketOrderRequest(
            symbol=detail["symbol"], qty=detail["qty"], side=_side,
            time_in_force=TimeInForce.DAY,
        )

    order = api.submit_order(req)

    # Mark approval as executed
    table.update_item(
        Key={"approval_id": approval_id},
        UpdateExpression="SET decision = :d",
        ExpressionAttributeValues={":d": "executed"},
    )

    return {
        "status":       "executed",
        "order_id":     str(order.id),
        "symbol":       order.symbol,
        "qty":          float(order.qty),
        "side":         order.side.value,
        "order_type":   order.order_type.value,
        "order_status": order.status.value,
        "submitted_at": str(order.submitted_at),
    }

@tool
def polygon_get_quote(symbol: str) -> dict:
    """
    FALLBACK tool for stock prices — only use if alpaca_get_quote fails or is unavailable.
    Requires Polygon.io Starter plan for real-time data; free tier returns previous-day only.
    Prefer alpaca_get_quote for all live price lookups.
    """
    import requests
    api_key = _get_secret("/finagent/polygon_api_key")
    resp = requests.get(
        f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{symbol.upper()}",
        params={"apiKey": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    ticker = data.get("ticker", {})
    day = ticker.get("day", {})
    prev_day = ticker.get("prevDay", {})
    last_quote = ticker.get("lastQuote", {})
    return {
        "symbol": symbol.upper(),
        "current_price": ticker.get("lastTrade", {}).get("p") or day.get("c"),
        "open": day.get("o"),
        "high": day.get("h"),
        "low": day.get("l"),
        "close": day.get("c"),
        "volume": day.get("v"),
        "prev_close": prev_day.get("c"),
        "change_pct": round(ticker.get("todaysChangePerc", 0), 2),
        "market_cap": None,  # Use polygon_get_fundamentals for this
    }

@tool
def polygon_get_market_snapshot() -> dict:
    """
    Get a current snapshot of major US market indices via Polygon.io.
    Uses index tickers: I:SPX (S&P 500), I:NDX (NASDAQ-100), I:DJI (Dow), I:VIX.
    """
    import requests
    api_key = _get_secret("/finagent/polygon_api_key")
    index_map = {
        "S&P 500":    "I:SPX",
        "NASDAQ-100": "I:NDX",
        "DOW":        "I:DJI",
        "VIX":        "I:VIX",
    }
    snapshot = {}
    for name, ticker in index_map.items():
        resp = requests.get(
            f"https://api.polygon.io/v3/snapshot",
            params={"ticker.any_of": ticker, "apiKey": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if results:
            r = results[0]
            session = r.get("session", {})
            snapshot[name] = {
                "price": session.get("close"),
                "change_pct": round(r.get("todaysChangePerc", 0), 2),
                "open": session.get("open"),
            }
    return snapshot

@tool
def polygon_get_news(symbol: str, count: int = 5) -> list:
    """
    Fetch top N recent news articles for a ticker or market topic via Polygon.io.
    Uses GET /v2/reference/news — available on free tier (5 req/min).
    """
    import requests
    api_key = _get_secret("/finagent/polygon_api_key")
    params = {"apiKey": api_key, "limit": count, "order": "desc", "sort": "published_utc"}
    if symbol and symbol != "market":
        params["ticker"] = symbol.upper()
    resp = requests.get(
        "https://api.polygon.io/v2/reference/news",
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    articles = resp.json().get("results", [])
    return [
        {
            "title": a.get("title"),
            "publisher": a.get("publisher", {}).get("name"),
            "link": a.get("article_url"),
            "published": a.get("published_utc"),
            "tickers": a.get("tickers", []),
        }
        for a in articles
    ]

@tool
def av_get_fundamentals(symbol: str) -> dict:
    """
    Get company fundamentals for a stock: P/E ratio, market cap, EPS, 52-week high/low,
    dividend yield, beta, analyst target price, and description.
    Use for stock research, analysis, and 'should I buy' questions.
    Args:
        symbol: Ticker symbol e.g. 'AAPL', 'ADBE', 'TSLA'
    """
    import requests
    api_key = _get_secret("/finagent/alpha_vantage_key")
    resp = requests.get(
        "https://www.alphavantage.co/query",
        params={"function": "OVERVIEW", "symbol": symbol.upper(), "apikey": api_key},
        timeout=10,
    )
    data = resp.json()
    if not data or "Symbol" not in data:
        return {"error": f"No fundamental data found for {symbol}"}
    return {
        "symbol":           data.get("Symbol"),
        "name":             data.get("Name"),
        "description":      data.get("Description", "")[:400],
        "sector":           data.get("Sector"),
        "industry":         data.get("Industry"),
        "market_cap":       data.get("MarketCapitalization"),
        "pe_ratio":         data.get("PERatio"),
        "peg_ratio":        data.get("PEGRatio"),
        "eps":              data.get("EPS"),
        "revenue_ttm":      data.get("RevenueTTM"),
        "profit_margin":    data.get("ProfitMargin"),
        "dividend_yield":   data.get("DividendYield"),
        "beta":             data.get("Beta"),
        "52_week_high":     data.get("52WeekHigh"),
        "52_week_low":      data.get("52WeekLow"),
        "analyst_target":   data.get("AnalystTargetPrice"),
        "forward_pe":       data.get("ForwardPE"),
    }

@tool
def av_get_quote(symbol: str) -> dict:
    """
    Get current price, daily OHLC, volume and change % for a stock via Alpha Vantage.
    Use as a secondary price source if alpaca_get_quote is unavailable.
    Args:
        symbol: Ticker symbol e.g. 'AAPL', 'ADBE'
    """
    import requests
    api_key = _get_secret("/finagent/alpha_vantage_key")
    resp = requests.get(
        "https://www.alphavantage.co/query",
        params={"function": "GLOBAL_QUOTE", "symbol": symbol.upper(), "apikey": api_key},
        timeout=10,
    )
    q = resp.json().get("Global Quote", {})
    if not q:
        return {"error": f"No quote data found for {symbol}"}
    return {
        "symbol":        q.get("01. symbol"),
        "price":         float(q.get("05. price", 0)),
        "open":          float(q.get("02. open", 0)),
        "high":          float(q.get("03. high", 0)),
        "low":           float(q.get("04. low", 0)),
        "volume":        int(q.get("06. volume", 0)),
        "previous_close":float(q.get("08. previous close", 0)),
        "change":        float(q.get("09. change", 0)),
        "change_pct":    q.get("10. change percent"),
        "trading_day":   q.get("07. latest trading day"),
    }

@tool
def get_credit_score(user_id: str) -> dict:
    """
    Returns the user's self-reported credit score from PERSONAL memory.
    No third-party API — user updates their score manually via update_credit_score().
    Tracks score history in EPISODIC memory for trend analysis.
    """
    memory = MemoryStore(table_name=MEMORY_TABLE)
    profile = memory.get_personal_profile(user_id)
    score = profile.get("credit_score")
    last_updated = profile.get("credit_score_updated_at")
    history = profile.get("credit_score_history", [])
    if not score:
        return {
            "credit_score": None,
            "message": "No credit score on file. Ask the user to provide it with: 'Update my credit score to <number>'",
            "last_updated": None,
            "history": [],
        }
    return {
        "credit_score": score,
        "last_updated": last_updated,
        "score_range": {"min": 300, "max": 850},
        "rating": _score_rating(score),
        "history": history[-6:],  # last 6 entries
    }

@tool
def update_credit_score(user_id: str, score: int) -> dict:
    """
    Stores a user-reported credit score in PERSONAL memory.
    Use when user says things like 'my credit score is 748' or 'update my credit score to 720'.
    Args:
        user_id: the user's ID
        score:   credit score value (300–850)
    """
    if not (300 <= score <= 850):
        return {"error": f"Invalid score {score}. Must be between 300 and 850."}
    memory = MemoryStore(table_name=MEMORY_TABLE)
    profile = memory.get_personal_profile(user_id)
    history = profile.get("credit_score_history", [])
    # Append previous score to history before updating
    if profile.get("credit_score"):
        history.append({
            "score": profile["credit_score"],
            "recorded_at": profile.get("credit_score_updated_at"),
        })
    memory.update_personal_profile(user_id, {
        "credit_score": score,
        "credit_score_updated_at": datetime.now(timezone.utc).isoformat(),
        "credit_score_history": history,
    })
    prev = profile.get("credit_score")
    delta = f"{score - prev:+d} points" if prev else "first entry"
    return {
        "credit_score": score,
        "rating": _score_rating(score),
        "change": delta,
        "message": f"Credit score updated to {score} ({_score_rating(score)}). {delta}.",
    }


# -- Approval gate ------------------------------------------------------------

APPROVAL_REQUIRED_TOOLS = {"alpaca_place_order", "alpaca_cancel_order"}

def requires_approval(tool_name: str) -> bool:
    return tool_name in APPROVAL_REQUIRED_TOOLS

def _to_decimal(obj):
    """Recursively convert floats to Decimal for DynamoDB storage."""
    from decimal import Decimal
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_decimal(i) for i in obj]
    return obj

def request_human_approval(tool_name: str, tool_args: dict, user_id: str) -> str:
    """
    Send approval request via SNS and write initial audit record to DynamoDB.
    Returns approval_id. Harness halts until confirmation arrives via /approve endpoint.
    """
    approval_id = f"approval_{int(time.time())}_{user_id[:8]}"
    created_at  = datetime.now(timezone.utc).isoformat()
    expires_at  = datetime.fromtimestamp(time.time() + 300, tz=timezone.utc).isoformat()

    # Write initial audit record — decision fields filled in later by approval_handler
    # DynamoDB requires Decimal instead of float for numeric values
    ddb = boto3.resource("dynamodb")
    table = ddb.Table(os.environ["APPROVALS_TABLE"])
    table.put_item(Item=_to_decimal({
        "approval_id":  approval_id,
        "user_id":      user_id,
        "created_at":   created_at,
        "expires_at":   expires_at,
        "action":       tool_name,
        "trade_detail": tool_args,
        "decision":     "pending",
        "decided_at":   None,
        "decided_by":   None,
        "ip_address":   None,
    }))

    # Look up user's email from UsersTable
    ddb_resource  = boto3.resource("dynamodb")
    users_table   = ddb_resource.Table(os.environ["USERS_TABLE"])
    user_record   = users_table.get_item(Key={"user_id": user_id}).get("Item", {})
    user_email    = user_record.get("notifications", {}).get("email")

    if not user_email:
        logger.error(json.dumps({
            "event": "approval_email_skipped",
            "reason": "no_email_on_file",
            "user_id": user_id,
        }))
    else:
        # Send approval email via SES — dynamic recipient per user
        frontend_url = os.environ.get("FRONTEND_URL", "https://your-frontend.com")
        ses.send_email(
            Source=f"FinAgent <{os.environ.get('SES_FROM_EMAIL', 'noreply@finagent.app')}>",
            Destination={"ToAddresses": [user_email]},
            Message={
                "Subject": {
                    "Data": f"FinAgent Trade Approval — {tool_args.get('symbol', tool_name)}"
                },
                "Body": {
                    "Html": {
                        "Data": f"""
                        <h2>Trade Approval Required</h2>
                        <p><b>Action:</b> {tool_args.get('side', '').upper()}
                           {tool_args.get('qty')} shares of {tool_args.get('symbol')}</p>
                        <p><b>Estimated Value:</b> ${tool_args.get('estimated_value', 'N/A')}</p>
                        <p><b>Expires:</b> {expires_at}</p>
                        <br>
                        <a href="{frontend_url}/approve?approval_id={approval_id}"
                           style="background:green;color:white;padding:10px 20px;text-decoration:none">
                           ✅ Approve Trade
                        </a>
                        &nbsp;&nbsp;
                        <a href="{frontend_url}/approve?approval_id={approval_id}&action=cancel"
                           style="background:red;color:white;padding:10px 20px;text-decoration:none">
                           ❌ Cancel Trade
                        </a>
                        <br><br>
                        <p style="color:grey;font-size:12px">
                           You must be logged in to approve. Approval ID: {approval_id}
                        </p>
                        """
                    }
                }
            }
        )
    logger.info(json.dumps({
        "event": "approval_requested",
        "approval_id": approval_id,
        "tool": tool_name,
        "user_id": user_id,
        "created_at": created_at,
    }))
    return approval_id


# -- Main agent ---------------------------------------------------------------

class FinAgent:
    def __init__(self):
        self.memory    = MemoryStore(table_name=MEMORY_TABLE)
        self.skill_loader = SkillLoader(bucket_name=SKILLS_BUCKET)
        self.model     = BedrockModel(
            model_id=BEDROCK_MODEL_ID,
        )
        self.tools = [
            alpaca_get_account, alpaca_get_quote, alpaca_get_positions,
            alpaca_place_order, execute_approved_trade,
            polygon_get_quote, polygon_get_market_snapshot, polygon_get_news,
            av_get_fundamentals, av_get_quote,
            get_credit_score, update_credit_score,
        ]

    async def invoke(self, user_message: str, user_id: str, session_id: str) -> str:
        start_ms = int(time.time() * 1000)

        # ── Step 1: Memory retrieval (recall → recognition) ───────────────────
        # _decimal_to_native converts DynamoDB Decimal types to int/float for JSON serialization
        personal  = _decimal_to_native(self.memory.get_personal_profile(user_id))
        working   = _decimal_to_native(self.memory.get_working_context(user_id, session_id))
        episodic  = _decimal_to_native(self.memory.retrieve_episodic(user_id, query=user_message, top_k=3))
        semantic  = _decimal_to_native(self.memory.retrieve_semantic(user_id, query=user_message, top_k=2))

        # Conversation history lives in working memory — keeps turns within a session
        conv_history = working.get("conversation_history", [])

        # ── Step 2: Skill selection + progressive disclosure ──────────────────
        skill_name = self._select_skill(user_message)
        skill_body = self.skill_loader.load(skill_name)

        # ── Step 3: Build system prompt ───────────────────────────────────────
        system_prompt = self._build_system_prompt(
            personal, episodic, semantic, skill_body, conv_history
        )

        # ── Step 4: Strands agent execution ───────────────────────────────────
        agent = Agent(
            model=self.model,
            tools=self.tools,
            system_prompt=system_prompt,
        )

        # Strands executes the full agentic loop — tool calls, reasoning, and response.
        # Approval gate is enforced inside alpaca_place_order and alpaca_cancel_order tools.
        response = agent(user_message)
        response_text = str(response)

        # ── Step 5: Save turn to working memory (conversation continuity) ─────
        conv_history.append({"role": "user",      "content": user_message})
        conv_history.append({"role": "assistant",  "content": response_text[:600]})
        self.memory.update_working_context(user_id, session_id, {
            **working,
            "conversation_history": conv_history[-20:],  # keep last 10 turns
        })

        # ── Step 6: Write episodic memory ─────────────────────────────────────
        self.memory.write_episodic(user_id, {
            "intent": user_message,
            "skill_used": skill_name,
            "response_summary": response_text[:500],
            "session_id": session_id,
        })

        # ── Step 6: CloudWatch observability ──────────────────────────────────
        latency_ms = int(time.time() * 1000) - start_ms
        logger.info(json.dumps({
            "event": "agent_invocation_complete",
            "userId": user_id,
            "sessionId": session_id,
            "skill": skill_name,
            "approval_required": False,
            "latency_ms": latency_ms,
        }))

        return response_text

    def _select_skill(self, message: str) -> str:
        """Simple keyword-based skill routing. Replace with embedding similarity at scale."""
        msg = message.lower()
        if any(k in msg for k in ["buy", "sell", "trade", "order", "shares"]):
            return "trade_execution"
        if any(k in msg for k in ["portfolio", "holdings", "positions", "p&l"]):
            return "portfolio_analysis"
        if any(k in msg for k in ["credit", "score", "fico", "vantage"]):
            return "credit_health"
        if any(k in msg for k in ["news", "market", "briefing", "today"]):
            return "market_briefing"
        if any(k in msg for k in ["research", "analysis", "should i buy", "earnings"]):
            return "stock_research"
        return "general_finance"

    def _build_system_prompt(self, personal: dict, episodic: list,
                              semantic: list, skill: str,
                              conv_history: list = None) -> str:
        # Format conversation history so the agent remembers what was said this session
        history_section = ""
        if conv_history:
            lines = []
            for m in conv_history[-12:]:   # last 6 turns (12 messages)
                role = "User" if m["role"] == "user" else "Assistant"
                lines.append(f"{role}: {m['content']}")
            history_section = "\nCONVERSATION SO FAR (working memory):\n" + "\n".join(lines) + "\n"

        return f"""You are FinAgent, a personal finance AI for {personal.get('name', 'the user')}.

USER PROFILE:
{json.dumps(personal, indent=2)}

RECENT HISTORY (episodic memory):
{json.dumps(episodic, indent=2)}

RELEVANT KNOWLEDGE (semantic memory):
{json.dumps(semantic, indent=2)}

ACTIVE SKILL:
{skill}
{history_section}
CORE RULES (non-negotiable):
1. Never execute any trade without explicit user confirmation in this conversation.
2. Always show the user what action you are about to take BEFORE calling alpaca_place_order.
3. Flag any position that would exceed 30% portfolio concentration.
4. Respect the user's sector_to_avoid list at all times.
5. All monetary amounts should be in USD unless the user specifies otherwise.
6. When uncertain, ask — never guess at the user's intent for financial actions.
7. For stock prices ALWAYS use alpaca_get_quote first — never polygon_get_quote for prices.
"""


# -- Lambda entry points ------------------------------------------------------

agent_instance = FinAgent()

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
}

def handler(event, context):
    """API Gateway Lambda handler for synchronous user messages.

    Session lifecycle:
      - First request:     no session_id in body → Lambda generates one → returned in response
      - Subsequent requests: client sends session_id → Lambda reuses it → WORKING memory maintained
    """
    import asyncio
    try:
        body     = json.loads(event.get("body", "{}"))
        user_msg = body.get("message", "")
        claims   = event["requestContext"]["authorizer"]["claims"]
        user_id  = claims.get("email") or claims.get("sub") or claims.get("cognito:username")

        # Determine if this is a new session or continuation
        session_id     = body.get("session_id")
        is_new_session = session_id is None
        if is_new_session:
            session_id = f"sess_{int(time.time())}_{user_id[:8]}"

        response = asyncio.run(agent_instance.invoke(user_msg, user_id, session_id))
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "response":    response,
                "session_id":  session_id,
                "new_session": is_new_session,
            }),
        }
    except Exception as e:
        import traceback
        logger.error(json.dumps({"event": "handler_error", "error": str(e), "traceback": traceback.format_exc()}))
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)}),
        }

def market_briefing_handler(event, context):
    """EventBridge Scheduler handler — runs daily at 7am PST.
    Scans users table for active users with briefing enabled,
    generates a personalised briefing for each, and delivers
    via their notification email stored in the users table.
    """
    import asyncio
    ddb = boto3.resource("dynamodb")
    table = ddb.Table(os.environ["USERS_TABLE"])

    # Scan for users with both is_active and briefing_enabled set to true
    resp = table.scan(
        FilterExpression=(
            Attr("is_active").eq(True) &
            Attr("briefing_enabled").eq(True)
        )
    )

    for user in resp.get("Items", []):
        user_id    = user["user_id"]
        email      = user.get("notifications", {}).get("email")
        timezone_  = user.get("timezone", "America/Los_Angeles")

        if not email:
            logger.warning(json.dumps({
                "event": "briefing_skipped",
                "reason": "no_email",
                "user_id": user_id,
            }))
            continue

        try:
            # Generate briefing for this user
            briefing = asyncio.run(agent_instance.invoke(
                user_message="Generate my daily market briefing",
                user_id=user_id,
                session_id=f"briefing_{datetime.now(timezone.utc).strftime('%Y%m%d')}",
            ))

            # Send briefing email directly to user via SES
            date_str = datetime.now(timezone.utc).strftime("%B %d, %Y")
            ses.send_email(
                Source=f"FinAgent <{os.environ.get('SES_FROM_EMAIL', 'noreply@finagent.app')}>",
                Destination={"ToAddresses": [email]},
                Message={
                    "Subject": {
                        "Data": f"FinAgent Daily Briefing — {date_str}"
                    },
                    "Body": {
                        "Html": {
                            "Data": f"<pre style='font-family:sans-serif'>{briefing}</pre>"
                        },
                        "Text": {"Data": briefing},
                    }
                }
            )
            logger.info(json.dumps({
                "event": "briefing_sent",
                "user_id": user_id,
                "email": email,
                "timezone": timezone_,
            }))

        except Exception as e:
            # Send failed briefing to DLQ for investigation
            logger.error(json.dumps({
                "event": "briefing_failed",
                "user_id": user_id,
                "error": str(e),
            }))
            sqs.send_message(
                QueueUrl=os.environ["BRIEFING_DLQ_URL"],
                MessageBody=json.dumps({
                    "user_id":    user_id,
                    "email":      email,
                    "failed_at":  datetime.now(timezone.utc).isoformat(),
                    "error":      str(e),
                    "retry_hint": "Re-invoke BriefingFunction manually for this user",
                }),
            )

def _decimal_to_native(obj):
    """Recursively convert DynamoDB Decimal types back to int/float for JSON serialization."""
    from decimal import Decimal
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    if isinstance(obj, dict):
        return {k: _decimal_to_native(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_decimal_to_native(i) for i in obj]
    return obj

def approval_handler(event, context):
    """Handles trade approval GET (load details) and POST (confirm/cancel) from API Gateway.

    GET  /approval/{approvalId}      — frontend loads trade details to display
    POST /approve/{approvalId}       — user confirms the trade
    POST /cancel/{approvalId}        — user cancels the trade
    """
    try:
        http_method = event.get("httpMethod", "POST")
        approval_id = event["pathParameters"]["approvalId"]

        ddb   = boto3.resource("dynamodb")
        table = ddb.Table(os.environ["APPROVALS_TABLE"])

        # ── GET: return approval record so frontend can display trade details ──
        if http_method == "GET":
            resp = table.get_item(Key={"approval_id": approval_id})
            item = resp.get("Item")
            if not item:
                return {
                    "statusCode": 404,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({"error": "Approval not found"}),
                }
            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps(_decimal_to_native({
                    "approval_id":  item["approval_id"],
                    "trade_detail": item.get("trade_detail", {}),
                    "decision":     item.get("decision", "pending"),
                    "expires_at":   item.get("expires_at"),
                    "created_at":   item.get("created_at"),
                })),
            }

        # ── POST: record the user's decision ─────────────────────────────────
        path   = event.get("path", "")
        action = "approve" if "/approve/" in path else "cancel"

        claims     = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        decided_by = claims.get("email") or claims.get("cognito:username", "unknown")
        decided_at = datetime.now(timezone.utc).isoformat()

        table.update_item(
            Key={"approval_id": approval_id},
            UpdateExpression="SET decision = :decision, decided_at = :decided_at, decided_by = :decided_by, ip_address = :ip",
            ExpressionAttributeValues={
                ":decision":   action,
                ":decided_at": decided_at,
                ":decided_by": decided_by,
                ":ip":         event.get("requestContext", {}).get("identity", {}).get("sourceIp", "unknown"),
            },
        )
        logger.info(json.dumps({
            "event": "trade_approval_decision", "approval_id": approval_id,
            "decision": action, "decided_by": decided_by,
        }))
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"status": "recorded", "decision": action}),
        }
    except Exception as e:
        logger.error(json.dumps({"event": "approval_handler_error", "error": str(e)}))
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)}),
        }


def consolidation_handler(event, context):
    """Manually trigger episodic → semantic memory consolidation for all active users.

    Invoke via CLI:
        aws lambda invoke --function-name finagent-consolidation-dev \
          --payload '{}' --cli-binary-format raw-in-base64-out response.json

    Or for a specific user:
        aws lambda invoke --function-name finagent-consolidation-dev \
          --payload '{"user_id": "gtmrrental@gmail.com"}' \
          --cli-binary-format raw-in-base64-out response.json
    """
    try:
        body       = json.loads(event.get("body") or "{}") if "body" in event else event
        user_id    = body.get("user_id")
        memory     = MemoryStore(os.environ["MEMORY_DDB_TABLE"])
        users_ddb  = boto3.resource("dynamodb").Table(os.environ["USERS_TABLE"])

        if user_id:
            users = [user_id]
        else:
            # Scan all active users
            resp  = users_ddb.scan(FilterExpression=Attr("is_active").eq(True))
            users = [item["user_id"] for item in resp.get("Items", [])]

        results = {}
        for uid in users:
            result = memory.consolidate_episodic(uid)
            results[uid] = result
            logger.info(json.dumps({"event": "consolidation_complete", "user_id": uid, **result}))

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"status": "done", "results": results}),
        }
    except Exception as e:
        logger.error(json.dumps({"event": "consolidation_error", "error": str(e)}))
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)}),
        }


# -- Private helpers ----------------------------------------------------------

def _alpaca_client():
    from alpaca.trading.client import TradingClient
    key    = _get_secret("/finagent/alpaca_api_key")
    secret = _get_secret("/finagent/alpaca_secret_key")
    paper  = "paper-api" in os.environ.get("ALPACA_BASE_URL", "paper-api.alpaca.markets")
    return TradingClient(key, secret, paper=paper)

def _get_secret(name: str) -> str:
    resp = ssm.get_parameter(Name=name, WithDecryption=True)
    return resp["Parameter"]["Value"]

def _score_rating(score: int) -> str:
    """Convert numeric credit score to a human-readable rating."""
    if score >= 800: return "Exceptional"
    if score >= 740: return "Very Good"
    if score >= 670: return "Good"
    if score >= 580: return "Fair"
    return "Poor"
