"""
Smart College Assistant — Sentence Transformer Embeddings
Provides a LangChain-compatible embeddings class using sentence-transformers.
"""

from __future__ import annotations

import numpy as np
from typing import List

from utils.logger import setup_logger

logger = setup_logger(__name__)

# ── Singleton cache ───────────────────────────────────────────
_embedding_model = None


def _get_model():
    """Load and cache the SentenceTransformer model."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        from config.settings import ActiveConfig
        model_name = ActiveConfig.EMBEDDING_MODEL
        logger.info("Loading SentenceTransformer: %s", model_name)
        _embedding_model = SentenceTransformer(model_name)
        logger.info("✅ Embedding model loaded.")
    return _embedding_model


class CollegeEmbeddings:
    """
    LangChain-compatible embeddings using sentence-transformers.

    Implements embed_documents() and embed_query() required by
    LangChain's Embeddings interface.
    """

    def __init__(self, model_name: str | None = None):
        from config.settings import ActiveConfig
        self.model_name = model_name or ActiveConfig.EMBEDDING_MODEL
        self._model = None

    def _load(self):
        if self._model is None:
            self._model = _get_model()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of document strings.

        Returns:
            List of embedding vectors.
        """
        self._load()
        logger.debug("Embedding %d documents.", len(texts))
        embeddings = self._model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.

        Args:
            text: Query string.

        Returns:
            Embedding vector as a list of floats.
        """
        self._load()
        embedding = self._model.encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embedding[0].tolist()


def get_embeddings() -> CollegeEmbeddings:
    """Factory function returning a CollegeEmbeddings instance."""
    return CollegeEmbeddings()
