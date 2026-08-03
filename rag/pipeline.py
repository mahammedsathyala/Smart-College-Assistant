"""
Smart College Assistant — Complete RAG Pipeline
Orchestrates document loading → chunking → embedding → retrieval → generation.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from loaders.pdf_loader import DocumentLoader
from rag.chunker import TextChunker
from vectorstore.faiss_store import get_vector_store
from models.watsonx_llm import get_llm
from utils.logger import setup_logger

logger = setup_logger(__name__)


# ── RAG Prompt Template ───────────────────────────────────────
RAG_PROMPT_TEMPLATE = """You are the Smart College Assistant — a helpful AI for students and staff.

Use the following context from college documents to answer the question accurately and concisely.
If the context does not contain enough information, say so and provide general guidance.

Context:
{context}

Question: {question}

Instructions:
- Answer based on the context above.
- Be concise and friendly.
- If relevant, mention the source document.
- If unsure, suggest contacting the college helpdesk.

Answer:"""


class RAGPipeline:
    """
    Complete RAG (Retrieval-Augmented Generation) pipeline.

    Flow:
        Document → Load → Chunk → Embed → Store in FAISS
        Query → Embed → FAISS Search → Top-K Chunks → LLM → Answer
    """

    def __init__(self):
        self.chunker = TextChunker()
        self.vector_store = get_vector_store()
        self.llm = get_llm()
        logger.info("RAGPipeline initialized.")

    # ── Ingestion ─────────────────────────────────────────────

    def ingest_file(self, file_path: str, metadata: dict | None = None) -> int:
        """
        Ingest a document file into the vector store.

        Args:
            file_path: Path to document (PDF, DOCX, TXT, CSV).
            metadata: Optional extra metadata to attach to all chunks.

        Returns:
            Number of chunks added.
        """
        metadata = metadata or {}
        logger.info("Ingesting file: %s", file_path)

        pages = DocumentLoader.load(file_path)
        if not pages:
            logger.warning("No content extracted from %s.", file_path)
            return 0

        # Merge extra metadata
        for page in pages:
            page["metadata"].update(metadata)

        chunks = self.chunker.split_documents(pages)
        texts = [c["text"] for c in chunks]
        metas = [c["metadata"] for c in chunks]

        count = self.vector_store.add_texts(texts, metas)
        logger.info("Ingested %d chunks from %s.", count, file_path)
        return count

    def ingest_text(self, text: str, metadata: dict | None = None) -> int:
        """
        Ingest raw text directly into the vector store.

        Args:
            text: Text content to index.
            metadata: Optional metadata dict.
        """
        metadata = metadata or {}
        chunks = self.chunker.split_text(text)
        metas = [{**metadata, "chunk_index": i} for i in range(len(chunks))]
        return self.vector_store.add_texts(chunks, metas)

    # ── Retrieval + Generation ────────────────────────────────

    def query(
        self,
        question: str,
        k: int = 4,
        return_sources: bool = True,
    ) -> dict:
        """
        Answer a question using retrieved context.

        Args:
            question: User question string.
            k: Number of context chunks to retrieve.
            return_sources: Whether to include source citations.

        Returns:
            dict with keys: answer, sources, confidence
        """
        from config.settings import ActiveConfig
        k = k or ActiveConfig.RETRIEVER_K

        # Step 1: Retrieve relevant chunks
        results = self.vector_store.similarity_search(question, k=k)

        if not results:
            logger.info("No RAG context found for: '%s' — using direct LLM.", question)
            answer = self.llm.invoke(
                f"Answer this college-related question: {question}"
            )
            return {
                "answer": answer,
                "sources": [],
                "confidence": 0.5,
                "context_used": False,
            }

        # Step 2: Build context string
        context = "\n\n---\n\n".join(
            f"[Source: {r['metadata'].get('source', 'Document')}]\n{r['text']}"
            for r in results
        )

        # Step 3: Build prompt
        prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=question)

        # Step 4: Generate answer
        answer = self.llm.invoke(prompt)

        # Step 5: Build source citations
        sources = []
        seen = set()
        for r in results:
            src = r["metadata"].get("source", "")
            if src and src not in seen:
                sources.append({
                    "file": Path(src).name if src else "Unknown",
                    "page": r["metadata"].get("page"),
                    "score": round(r["score"], 4),
                })
                seen.add(src)

        avg_score = sum(r["score"] for r in results) / len(results)
        confidence = round(min(avg_score, 1.0), 4)

        logger.info(
            "RAG query answered | Chunks: %d | Confidence: %.3f | Question: '%s'",
            len(results), confidence, question[:50],
        )

        return {
            "answer": answer,
            "sources": sources if return_sources else [],
            "confidence": confidence,
            "context_used": True,
        }

    # ── Stats ─────────────────────────────────────────────────

    def get_stats(self) -> dict:
        return {
            "vector_store": self.vector_store.get_stats(),
            "llm_type": type(self.llm).__name__,
        }


# ── Singleton ─────────────────────────────────────────────────
_rag_pipeline: RAGPipeline | None = None


def get_rag_pipeline() -> RAGPipeline:
    """Return singleton RAGPipeline."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
