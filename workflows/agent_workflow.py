"""
Smart College Assistant — Agent Workflow
Orchestrates the complete multi-agent processing workflow.
"""

from __future__ import annotations
from datetime import datetime
from agents.coordinator_agent import get_coordinator
from utils.logger import get_ai_logger

logger = get_ai_logger()


class AgentWorkflow:
    """
    Orchestrates multi-agent query processing with logging and metrics.

    This is the main entry point for all AI queries in the system.
    """

    def __init__(self):
        self.coordinator = get_coordinator()
        self.query_count = 0
        self.start_time = datetime.utcnow()

    def process(
        self,
        query: str,
        history: list[dict] | None = None,
        context: dict | None = None,
    ) -> dict:
        """
        Process a user query through the multi-agent workflow.

        Args:
            query: User question.
            history: Conversation history.
            context: Optional context (user_id, etc.)

        Returns:
            Structured response dict.
        """
        self.query_count += 1
        start = datetime.utcnow()

        logger.info(
            "Workflow processing query #%d: '%s'",
            self.query_count, query[:60]
        )

        result = self.coordinator.handle(query, history, context)

        elapsed_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
        result["processing_time_ms"] = elapsed_ms
        result["query_number"] = self.query_count

        logger.info(
            "Query #%d processed in %dms → agent=%s",
            self.query_count, elapsed_ms, result.get("routed_to", "unknown")
        )

        return result

    def get_stats(self) -> dict:
        """Return workflow statistics."""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        return {
            "total_queries": self.query_count,
            "uptime_seconds": round(uptime),
            "avg_qps": round(self.query_count / uptime, 3) if uptime > 0 else 0,
        }


# ── Singleton ─────────────────────────────────────────────────
_workflow: AgentWorkflow | None = None


def get_workflow() -> AgentWorkflow:
    """Return singleton AgentWorkflow."""
    global _workflow
    if _workflow is None:
        _workflow = AgentWorkflow()
    return _workflow
