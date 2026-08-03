"""
Smart College Assistant — Coordinator Agent
Routes user queries to the most appropriate specialized agent.
"""

from __future__ import annotations

import re
from utils.logger import get_ai_logger

logger = get_ai_logger()


# ── Keyword-based routing rules (fast path) ──────────────────
ROUTING_RULES: dict[str, list[str]] = {
    "ADMISSION": [
        "admission", "apply", "application", "eligibility", "documents",
        "fee", "scholarship", "hostel", "seat", "counseling", "merit",
        "entrance exam", "cutoff", "join", "enroll",
    ],
    "EXAM": [
        "exam", "examination", "hall ticket", "result", "cgpa", "gpa",
        "grade", "marks", "revaluation", "supplementary", "credits",
        "pass", "fail", "backlog", "semester", "internal", "external",
    ],
    "PLACEMENT": [
        "placement", "company", "recruit", "job", "package", "lpa",
        "interview", "resume", "cv", "drive", "tcs", "infosys", "wipro",
        "amazon", "google", "offer letter", "campus",
    ],
    "POLICY": [
        "attendance", "absent", "leave", "rule", "policy", "dress code",
        "uniform", "library", "fine", "ragging", "conduct", "discipline",
        "hostel rules", "anti-ragging",
    ],
    "TIMETABLE": [
        "timetable", "schedule", "class", "period", "timing", "room",
        "faculty", "professor", "teacher", "lab session", "slot",
    ],
    "FAQ": [
        "help", "how to", "what is", "where", "when", "who", "contact",
        "helpdesk", "phone number", "address", "office",
    ],
}


def _keyword_route(query: str) -> str | None:
    """Fast keyword-based routing. Returns agent name or None."""
    lower = query.lower()
    scores: dict[str, int] = {}
    for agent, keywords in ROUTING_RULES.items():
        score = sum(1 for kw in keywords if kw in lower)
        if score > 0:
            scores[agent] = score
    if scores:
        return max(scores, key=scores.get)
    return None


def route_query(query: str, llm=None) -> str:
    """
    Determine which agent should handle a query.

    Uses fast keyword matching first; falls back to LLM classification.

    Args:
        query: User's question.
        llm: Optional LLM instance for classification.

    Returns:
        Agent name string (e.g., "ADMISSION", "EXAM", ...).
    """
    # Fast path
    agent = _keyword_route(query)
    if agent:
        logger.info("Coordinator → %s (keyword match)", agent)
        return agent

    # LLM-based classification
    if llm is not None:
        from prompts.system_prompts import COORDINATOR_SYSTEM_PROMPT
        prompt = COORDINATOR_SYSTEM_PROMPT.format(query=query)
        try:
            result = llm.invoke(prompt).strip().upper()
            # Extract agent name from result
            valid = {"ADMISSION", "EXAM", "PLACEMENT", "POLICY", "TIMETABLE", "FAQ", "RAG"}
            for word in result.split():
                if word in valid:
                    logger.info("Coordinator → %s (LLM classification)", word)
                    return word
        except Exception as e:
            logger.warning("LLM routing failed: %s — defaulting to FAQ", e)

    logger.info("Coordinator → FAQ (default fallback)")
    return "FAQ"


class CoordinatorAgent:
    """
    Orchestrates the multi-agent system.

    Instantiates all specialized agents and routes queries
    to the appropriate one based on query content.
    """

    def __init__(self):
        from models.watsonx_llm import get_llm
        from agents.admission_agent import AdmissionAgent
        from agents.exam_agent import ExamAgent
        from agents.placement_agent import PlacementAgent
        from agents.policy_agent import PolicyAgent
        from agents.timetable_agent import TimetableAgent
        from agents.faq_agent import FAQAgent
        from agents.rag_agent import RAGAgent

        self.llm = get_llm()
        self.agents = {
            "ADMISSION": AdmissionAgent(self.llm),
            "EXAM": ExamAgent(self.llm),
            "PLACEMENT": PlacementAgent(self.llm),
            "POLICY": PolicyAgent(self.llm),
            "TIMETABLE": TimetableAgent(self.llm),
            "FAQ": FAQAgent(self.llm),
            "RAG": RAGAgent(self.llm),
        }
        logger.info("CoordinatorAgent initialized with %d agents.", len(self.agents))

    def handle(
        self,
        query: str,
        history: list[dict] | None = None,
        context: dict | None = None,
    ) -> dict:
        """
        Route query to appropriate agent and return response.

        Args:
            query: User question.
            history: Conversation history.
            context: Additional context.

        Returns:
            Structured response dict.
        """
        agent_name = route_query(query, self.llm)
        agent = self.agents.get(agent_name, self.agents["FAQ"])
        result = agent.handle(query, history, context)
        result["routed_to"] = agent_name
        return result


# ── Singleton ─────────────────────────────────────────────────
_coordinator: CoordinatorAgent | None = None


def get_coordinator() -> CoordinatorAgent:
    """Return singleton CoordinatorAgent."""
    global _coordinator
    if _coordinator is None:
        _coordinator = CoordinatorAgent()
    return _coordinator
