"""
Smart College Assistant — Base Agent
All specialized agents inherit from this base class.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from models.watsonx_llm import get_llm
from utils.logger import get_ai_logger

logger = get_ai_logger()


class BaseAgent:
    """
    Abstract base class for all Smart College Agents.

    Each agent has:
    - A unique name
    - A system prompt defining its domain and persona
    - A reference to the LLM
    - A handle() method that generates a response
    """

    name: str = "base_agent"
    system_prompt: str = ""

    def __init__(self, llm=None):
        self.llm = llm or get_llm()

    def _build_prompt(self, query: str, history: list[dict] | None = None) -> str:
        """
        Construct the full prompt with system context and conversation history.

        Args:
            query: Current user query.
            history: List of {"role": "user"|"assistant", "content": str} dicts.

        Returns:
            Full formatted prompt string.
        """
        today = date.today().strftime("%d %B %Y")
        system = self.system_prompt.replace("{date}", today)

        parts = [f"System: {system}"]

        if history:
            for turn in history[-6:]:  # Last 3 exchanges
                role = "Student" if turn["role"] == "user" else "Assistant"
                parts.append(f"{role}: {turn['content']}")

        parts.append(f"Student: {query}")
        parts.append("Assistant:")
        return "\n\n".join(parts)

    def handle(
        self,
        query: str,
        history: list[dict] | None = None,
        context: dict | None = None,
    ) -> dict:
        """
        Process a query and return a structured response.

        Args:
            query: User's question.
            history: Conversation history.
            context: Additional context (e.g., student data).

        Returns:
            dict with keys: answer, agent, confidence, sources
        """
        logger.info("[%s] Handling query: '%s'", self.name, query[:60])
        try:
            prompt = self._build_prompt(query, history)
            answer = self.llm.invoke(prompt)
            return {
                "answer": answer,
                "agent": self.name,
                "confidence": 0.9,
                "sources": [],
            }
        except Exception as e:
            logger.error("[%s] Error: %s", self.name, e)
            return {
                "answer": "I apologize, I encountered an issue. Please try again or contact the helpdesk.",
                "agent": self.name,
                "confidence": 0.0,
                "sources": [],
            }
