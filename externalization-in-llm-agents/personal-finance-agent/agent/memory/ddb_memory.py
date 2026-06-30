"""
FinAgent Memory Store — DynamoDB implementation
4-tier externalized memory (Zhou et al., 2026 §3):
  WORKING   → current session context        TTL: 24h
  EPISODIC  → past events, decisions         TTL: 90 days
  SEMANTIC  → domain knowledge, heuristics   TTL: permanent
  PERSONAL  → user profile, goals, prefs     TTL: permanent

Schema:
  HASH  → user_id   (e.g. "gaurav@example.com")
  RANGE → sort_key  (e.g. "EPISODIC#2026-06-18T14:30:00Z")

Sort key format per tier:
  PERSONAL  → "PERSONAL#profile"
  EPISODIC  → "EPISODIC#<iso_timestamp>"
  WORKING   → "WORKING#<session_id>"
  SEMANTIC  → "SEMANTIC#<topic_name>"

Queries:
  All EPISODIC for user → user_id=X, sort_key BEGINS_WITH "EPISODIC#"
  PERSONAL profile      → user_id=X, sort_key = "PERSONAL#profile"
  All SEMANTIC for user → user_id=X, sort_key BEGINS_WITH "SEMANTIC#"
  Current session       → user_id=X, sort_key = "WORKING#<session_id>"
"""

import json
import time
import boto3
from datetime import datetime, timezone, timedelta
from typing import Optional
from boto3.dynamodb.conditions import Key, Attr
from collections import Counter


class MemoryStore:
    def __init__(self, table_name: str):
        ddb = boto3.resource("dynamodb")
        self.table = ddb.Table(table_name)

    # ── PERSONAL MEMORY ───────────────────────────────────────────────────────

    def get_personal_profile(self, user_id: str) -> dict:
        """Load the user's persistent profile — risk tolerance, goals, preferences."""
        resp = self.table.get_item(
            Key={
                "user_id": user_id,
                "sort_key": "PERSONAL#profile",
            }
        )
        item = resp.get("Item")
        if not item:
            return self._default_personal_profile(user_id)
        return item.get("content", {})

    def update_personal_profile(self, user_id: str, updates: dict):
        """Merge updates into the user's personal profile."""
        profile = self.get_personal_profile(user_id)
        profile.update(updates)
        self.table.put_item(Item={
            "user_id": user_id,
            "sort_key": "PERSONAL#profile",
            "content": profile,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        })

    def _default_personal_profile(self, user_id: str) -> dict:
        return {
            "user_id": user_id,
            "risk_tolerance": "moderate",
            "investment_horizon": "unknown",
            "goals": [],
            "sector_preferences": [],
            "sectors_to_avoid": [],
            "preferred_briefing_time": "07:00",
            "trade_approval_threshold_usd": 500,
            "credit_score": None,
            "credit_score_updated_at": None,
            "credit_score_history": [],
            "monthly_budget_targets": {},
        }

    # ── WORKING MEMORY ────────────────────────────────────────────────────────

    def get_working_context(self, user_id: str, session_id: str) -> dict:
        """Get in-progress session state — active intent, pending approvals."""
        resp = self.table.get_item(
            Key={
                "user_id": user_id,
                "sort_key": f"WORKING#{session_id}",
            }
        )
        return resp.get("Item", {}).get("content", {})

    def update_working_context(self, user_id: str, session_id: str, updates: dict):
        """Update working context for active session. TTL: 24 hours."""
        self.table.put_item(Item={
            "user_id": user_id,
            "sort_key": f"WORKING#{session_id}",
            "session_id": session_id,
            "content": updates,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "ttl": int(time.time()) + 86400,  # 24h TTL
        })

    def clear_working_context(self, user_id: str, session_id: str):
        """Clear session state on conversation end."""
        self.table.delete_item(
            Key={
                "user_id": user_id,
                "sort_key": f"WORKING#{session_id}",
            }
        )

    # ── EPISODIC MEMORY ───────────────────────────────────────────────────────

    def write_episodic(self, user_id: str, event: dict):
        """
        Record what happened: intent, skill used, tools called, outcome.
        Converts experience into a retrievable artifact (paper §3.1).
        Sort key uses ISO timestamp so records sort chronologically.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        self.table.put_item(Item={
            "user_id": user_id,
            "sort_key": f"EPISODIC#{timestamp}",
            "created_at": timestamp,
            "event_type": event.get("skill_used", "GENERAL").upper(),
            "content": {
                "intent": event.get("intent"),
                "skill_used": event.get("skill_used"),
                "response_summary": event.get("response_summary"),
                "session_id": event.get("session_id"),
                "outcome": event.get("outcome", "success"),
                "reflection": event.get("reflection"),
            },
            "ttl": int(time.time()) + (90 * 86400),  # 90 day TTL
        })

    def retrieve_episodic(self, user_id: str, query: str, top_k: int = 3) -> list:
        """
        Retrieve top-K episodic memories relevant to current query.
        Queries using BEGINS_WITH on sort_key — no GSI needed.
        MVP: recency + keyword relevance. Production: replace with embeddings.
        """
        resp = self.table.query(
            KeyConditionExpression=(
                Key("user_id").eq(user_id) &
                Key("sort_key").begins_with("EPISODIC#")
            ),
            ScanIndexForward=False,  # newest first (descending sort_key)
            Limit=top_k * 3,        # over-fetch then re-rank by relevance
        )
        items = resp.get("Items", [])

        # Keyword relevance scoring (replace with embeddings at scale)
        query_words = set(query.lower().split())
        def relevance(item):
            text = str(item.get("content", {})).lower()
            return sum(1 for w in query_words if w in text)

        items.sort(key=relevance, reverse=True)
        return [i.get("content", {}) for i in items[:top_k]]

    # ── SEMANTIC MEMORY ───────────────────────────────────────────────────────

    def write_semantic(self, user_id: str, topic: str, content: dict):
        """
        Store stable knowledge: market facts, domain concepts, heuristics.
        Sort key uses topic name for direct lookup — no timestamp needed.
        """
        self.table.put_item(Item={
            "user_id": user_id,
            "sort_key": f"SEMANTIC#{topic}",
            "topic": topic,
            "content": content,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        })

    def retrieve_semantic(self, user_id: str, query: str, top_k: int = 2) -> list:
        """Retrieve relevant semantic knowledge items using BEGINS_WITH."""
        resp = self.table.query(
            KeyConditionExpression=(
                Key("user_id").eq(user_id) &
                Key("sort_key").begins_with("SEMANTIC#")
            ),
        )
        items = resp.get("Items", [])
        query_words = set(query.lower().split())
        def relevance(item):
            # Use str() instead of json.dumps() to avoid Decimal serialization issues
            text = (item.get("topic", "") + str(item.get("content", {}))).lower()
            return sum(1 for w in query_words if w in text)
        items.sort(key=relevance, reverse=True)
        return [{"topic": i["topic"], **i.get("content", {})} for i in items[:top_k]]

    # ── MEMORY LIFECYCLE ──────────────────────────────────────────────────────

    def consolidate_episodic(self, user_id: str, bedrock_model_id: str = "us.anthropic.claude-sonnet-4-6"):
        """
        Promote episodic patterns into semantic memory using LLM reflection.
        Implements episodic → semantic promotion (paper §3.1).

        Instead of hard-coded rules, passes all episodic entries to Claude which
        extracts nuanced user patterns, preferences, and behavioral insights.
        Run periodically via EventBridge weekly job.
        """
        import boto3 as _boto3

        # ── Load last 30 days of episodic memory ─────────────────────────────
        cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        resp = self.table.query(
            KeyConditionExpression=(
                Key("user_id").eq(user_id) &
                Key("sort_key").begins_with("EPISODIC#")
            ),
            FilterExpression=Attr("created_at").gte(cutoff),
        )
        episodes = resp.get("Items", [])

        if not episodes:
            return {"episodes_scanned": 0, "promoted": []}

        # ── Format episodes for LLM ───────────────────────────────────────────
        episode_lines = []
        for e in episodes:
            c = e.get("content", {})
            episode_lines.append(
                f"- [{e.get('created_at', '')[:10]}] skill={c.get('skill_used')} "
                f"intent=\"{c.get('intent')}\" outcome={c.get('outcome')}"
            )
        episodes_text = "\n".join(episode_lines)

        # ── Ask Claude to extract semantic knowledge ──────────────────────────
        prompt = f"""You are analyzing a user's financial agent interaction history to extract stable knowledge about them.

Here are their recent interactions (last 30 days):

{episodes_text}

Extract semantic knowledge about this user. Return a JSON object with these keys:

{{
  "trading_behavior": {{
    "description": "What stocks/assets does the user trade? How often? What order sizes?",
    "frequently_traded": ["list of tickers"],
    "preferred_order_type": "market or limit",
    "typical_trade_size": "small/medium/large"
  }},
  "information_seeking": {{
    "description": "What financial information does the user check regularly?",
    "frequent_topics": ["list of topics"],
    "preferred_data_sources": ["alpaca", "polygon", etc]
  }},
  "risk_profile": {{
    "description": "Inferred risk tolerance from trading patterns",
    "inferred_risk": "conservative/moderate/aggressive",
    "evidence": "what behavior suggests this"
  }},
  "portfolio_focus": {{
    "description": "What sectors/themes does the user focus on?",
    "sectors": ["list"],
    "themes": ["growth", "dividend", "tech", etc]
  }},
  "behavioral_patterns": {{
    "description": "Any notable patterns in how they use the agent",
    "patterns": ["list of observations"]
  }}
}}

Return ONLY valid JSON, no explanation."""

        bedrock = _boto3.client("bedrock-runtime", region_name="us-west-2")
        response = bedrock.converse(
            modelId=bedrock_model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 1024, "temperature": 0.1},
        )
        raw = response["output"]["message"]["content"][0]["text"].strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        insights = json.loads(raw)

        # ── Write each insight as a separate semantic memory entry ────────────
        promoted = []
        for topic, content in insights.items():
            if content:
                self.write_semantic(user_id, topic, {
                    **content,
                    "derived_from_episodes": len(episodes),
                    "consolidated_at": datetime.now(timezone.utc).isoformat(),
                })
                promoted.append(topic)

        return {
            "episodes_scanned": len(episodes),
            "promoted": promoted,
            "insights": insights,
        }
