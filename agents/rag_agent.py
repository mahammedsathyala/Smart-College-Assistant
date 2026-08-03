"""Smart College Assistant — RAG Agent
Uses the full RAG pipeline to answer document-grounded queries.
"""

from __future__ import annotations
from agents.base_agent import BaseAgent
from prompts.system_prompts import RAG_SYSTEM_PROMPT
from utils.logger import get_ai_logger

logger = get_ai_logger()


class RAGAgent(BaseAgent):
    """
    RAG-powered agent that retrieves context from uploaded documents
    before generating answers using the LLM.
    """

    name = "rag_agent"
    system_prompt = RAG_SYSTEM_PROMPT

    def handle(
        self,
        query: str,
        history: list[dict] | None = None,
        context: dict | None = None,
    ) -> dict:
        """Override to use RAG pipeline instead of direct LLM."""
        from rag.pipeline import get_rag_pipeline
        logger.info("[RAGAgent] Query: '%s'", query[:60])

        pipeline = get_rag_pipeline()
        result = pipeline.query(query, k=4, return_sources=True)

        return {
            "answer": result["answer"],
            "agent": self.name,
            "confidence": result["confidence"],
            "sources": result["sources"],
            "context_used": result.get("context_used", False),
        }
