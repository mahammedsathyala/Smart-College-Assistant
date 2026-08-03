"""
Smart College Assistant — FAISS Vector Store
Manages document embeddings storage, retrieval, and persistence.
"""

from __future__ import annotations

import os
import json
import pickle
from pathlib import Path
from typing import List, Tuple

import numpy as np

from embeddings.sentence_transformer_embeddings import get_embeddings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FAISSStore:
    """
    FAISS-based vector store for semantic document retrieval.

    Stores document chunks with their embeddings and metadata,
    persists to disk, and supports similarity search.
    """

    def __init__(self, index_path: str | None = None):
        from config.settings import ActiveConfig
        self.index_path = Path(index_path or ActiveConfig.FAISS_INDEX_PATH)
        self.index_path.mkdir(parents=True, exist_ok=True)

        self.embeddings = get_embeddings()
        self._index = None        # faiss.IndexFlatIP
        self._documents: list[dict] = []  # [{text, metadata}]

        self._load_if_exists()

    # ── Index management ─────────────────────────────────────

    def _load_if_exists(self) -> None:
        """Load existing FAISS index and documents from disk."""
        index_file = self.index_path / "faiss.index"
        docs_file = self.index_path / "documents.pkl"

        if index_file.exists() and docs_file.exists():
            try:
                import faiss
                self._index = faiss.read_index(str(index_file))
                with open(docs_file, "rb") as f:
                    self._documents = pickle.load(f)
                logger.info(
                    "✅ Loaded FAISS index with %d vectors.", self._index.ntotal
                )
            except Exception as e:
                logger.error("Failed to load FAISS index: %s", e)
                self._index = None
                self._documents = []
        else:
            logger.info("No existing FAISS index found — starting fresh.")

    def save(self) -> None:
        """Persist FAISS index and document store to disk."""
        if self._index is None:
            return
        try:
            import faiss
            faiss.write_index(self._index, str(self.index_path / "faiss.index"))
            with open(self.index_path / "documents.pkl", "wb") as f:
                pickle.dump(self._documents, f)
            logger.info("💾 FAISS index saved (%d vectors).", self._index.ntotal)
        except Exception as e:
            logger.error("Failed to save FAISS index: %s", e)

    # ── Adding documents ─────────────────────────────────────

    def add_texts(
        self,
        texts: List[str],
        metadatas: List[dict] | None = None,
    ) -> int:
        """
        Add text chunks to the vector store.

        Args:
            texts: List of text chunks.
            metadatas: Optional list of metadata dicts.

        Returns:
            Number of vectors added.
        """
        import faiss

        if not texts:
            return 0

        metadatas = metadatas or [{} for _ in texts]
        vectors = np.array(self.embeddings.embed_documents(texts), dtype="float32")

        if self._index is None:
            dim = vectors.shape[1]
            self._index = faiss.IndexFlatIP(dim)   # Inner product = cosine (normalized)
            logger.info("Created new FAISS index (dim=%d).", dim)

        self._index.add(vectors)

        for text, meta in zip(texts, metadatas):
            self._documents.append({"text": text, "metadata": meta})

        self.save()
        logger.info("Added %d vectors. Total: %d.", len(texts), self._index.ntotal)
        return len(texts)

    # ── Similarity search ────────────────────────────────────

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        score_threshold: float = 0.0,
    ) -> List[dict]:
        """
        Find k most similar documents to query.

        Args:
            query: Search query string.
            k: Number of results.
            score_threshold: Minimum similarity score.

        Returns:
            List of {text, metadata, score} dicts.
        """
        if self._index is None or self._index.ntotal == 0:
            logger.warning("FAISS index is empty — no results.")
            return []

        query_vec = np.array(
            [self.embeddings.embed_query(query)], dtype="float32"
        )
        k = min(k, self._index.ntotal)
        scores, indices = self._index.search(query_vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or float(score) < score_threshold:
                continue
            doc = self._documents[idx]
            results.append({
                "text": doc["text"],
                "metadata": doc["metadata"],
                "score": float(score),
            })

        logger.debug("Similarity search returned %d results for: '%s'", len(results), query[:50])
        return results

    def similarity_search_with_score(
        self, query: str, k: int = 4
    ) -> List[Tuple[dict, float]]:
        """Return (document, score) pairs."""
        results = self.similarity_search(query, k)
        return [(r, r["score"]) for r in results]

    # ── Index stats ──────────────────────────────────────────

    @property
    def total_vectors(self) -> int:
        """Total number of stored vectors."""
        return self._index.ntotal if self._index else 0

    def clear(self) -> None:
        """Clear all vectors and documents."""
        self._index = None
        self._documents = []
        for f in self.index_path.glob("*"):
            f.unlink()
        logger.info("FAISS index cleared.")

    def get_stats(self) -> dict:
        return {
            "total_vectors": self.total_vectors,
            "total_documents": len(self._documents),
            "index_path": str(self.index_path),
        }


# ── Singleton accessor ───────────────────────────────────────
_store: FAISSStore | None = None


def get_vector_store() -> FAISSStore:
    """Return singleton FAISSStore instance."""
    global _store
    if _store is None:
        _store = FAISSStore()
    return _store
