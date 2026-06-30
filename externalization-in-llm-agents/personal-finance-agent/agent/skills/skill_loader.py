"""
FinAgent Skill Loader — loads SKILL.md files from S3 at runtime.

Skills are declarative markdown files that tell the agent HOW to handle
a specific task (progressive disclosure, paper §4.3). They are stored in
S3 rather than hardcoded so they can be updated without redeploying Lambda.

Usage:
    loader = SkillLoader(bucket_name=os.environ["SKILLS_S3_BUCKET"])
    skill_content = loader.load("trade_execution")   # reads trade_execution.md
"""

import os
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SkillLoader:
    def __init__(self, bucket_name: str):
        self.bucket = bucket_name
        self.s3 = boto3.client("s3")
        self._cache: dict[str, str] = {}   # in-memory cache per Lambda invocation

    def load(self, skill_name: str) -> str:
        """
        Load a skill by name. Reads <skill_name>.md from S3.
        Results are cached in memory for the lifetime of the Lambda invocation.

        Returns empty string if the skill file is not found — the agent
        falls back to general knowledge rather than crashing.
        """
        if skill_name in self._cache:
            return self._cache[skill_name]

        key = f"{skill_name}.md"
        try:
            resp    = self.s3.get_object(Bucket=self.bucket, Key=key)
            content = resp["Body"].read().decode("utf-8")
            self._cache[skill_name] = content
            logger.info(f"Loaded skill '{skill_name}' ({len(content)} chars) from s3://{self.bucket}/{key}")
            return content
        except ClientError as e:
            if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
                logger.warning(f"Skill not found in S3: s3://{self.bucket}/{key}")
            else:
                logger.error(f"S3 error loading skill '{skill_name}': {e}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error loading skill '{skill_name}': {e}")
            return ""

    def load_for_intent(self, user_message: str) -> tuple[str, str]:
        """
        Map a user message to the best matching skill and load it.
        Returns (skill_name, skill_content).

        The agent calls this after receiving the user message so it can
        inject the relevant skill instructions into the prompt.
        """
        # Keyword → skill file mapping (order matters — first match wins)
        intent_map = [
            (["buy", "sell", "trade", "order", "shares", "stock purchase"], "trade_execution"),
            (["portfolio", "holdings", "positions", "allocation", "rebalance"], "portfolio_analysis"),
            (["briefing", "market update", "market summary", "news", "movers"], "market_briefing"),
            (["credit score", "credit", "fico", "credit health"],              "credit_health"),
            (["budget", "spending", "expenses", "cash flow", "monthly"],       "budget_analysis"),
            (["research", "analyze", "fundamental", "earnings", "pe ratio"],   "stock_research"),
        ]

        msg_lower = user_message.lower()
        for keywords, skill_name in intent_map:
            if any(kw in msg_lower for kw in keywords):
                return skill_name, self.load(skill_name)

        # No skill matched — agent uses general knowledge
        logger.info(f"No skill matched for message: '{user_message[:60]}...'")
        return "", ""
