"""
Smart College Assistant — Text Chunker
Splits documents into overlapping chunks for better RAG retrieval.
"""

from __future__ import annotations
from typing import List

from utils.logger import setup_logger

logger = setup_logger(__name__)


class TextChunker:
    """
    Splits long texts into overlapping chunks.

    Uses a sliding window approach: each chunk is CHUNK_SIZE characters
    long with CHUNK_OVERLAP characters of overlap with the previous chunk.
    This preserves context across chunk boundaries.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        from config.settings import ActiveConfig
        self.chunk_size = chunk_size or ActiveConfig.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or ActiveConfig.CHUNK_OVERLAP

    def split_text(self, text: str) -> List[str]:
        """
        Split a single text into overlapping chunks.

        Args:
            text: Input text string.

        Returns:
            List of chunk strings.
        """
        if len(text) <= self.chunk_size:
            return [text.strip()] if text.strip() else []

        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap

        logger.debug("Split text (%d chars) into %d chunks.", len(text), len(chunks))
        return chunks

    def split_documents(self, documents: List[dict]) -> List[dict]:
        """
        Split a list of document pages into chunks with metadata preserved.

        Args:
            documents: List of {"text": str, "metadata": dict} dicts.

        Returns:
            List of {"text": str, "metadata": dict} chunk dicts.
        """
        all_chunks = []
        for doc in documents:
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            chunks = self.split_text(text)
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    "text": chunk,
                    "metadata": {**metadata, "chunk_index": i},
                })

        logger.info(
            "Chunked %d documents → %d chunks.", len(documents), len(all_chunks)
        )
        return all_chunks
