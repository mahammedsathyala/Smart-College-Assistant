"""
Smart College Assistant — Document Loaders
Supports PDF, DOCX, TXT, and CSV loading for RAG pipeline.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import List

from utils.logger import setup_logger

logger = setup_logger(__name__)


class DocumentLoader:
    """
    Multi-format document loader.

    Supports: .pdf, .docx, .txt, .csv
    Returns a list of page/chunk dicts: {text, metadata}
    """

    @staticmethod
    def load(file_path: str) -> List[dict]:
        """
        Load a document and return a list of text pages with metadata.

        Args:
            file_path: Absolute path to the document.

        Returns:
            List of {"text": str, "metadata": dict} dicts.
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        loaders = {
            ".pdf": DocumentLoader._load_pdf,
            ".docx": DocumentLoader._load_docx,
            ".txt": DocumentLoader._load_txt,
            ".csv": DocumentLoader._load_csv,
        }
        if ext not in loaders:
            raise ValueError(f"Unsupported file type: {ext}")

        logger.info("Loading document: %s (%s)", path.name, ext)
        pages = loaders[ext](str(path))
        logger.info("Loaded %d pages/chunks from %s.", len(pages), path.name)
        return pages

    @staticmethod
    def _load_pdf(file_path: str) -> List[dict]:
        """Load PDF using pypdf."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            pages = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages.append({
                        "text": text,
                        "metadata": {
                            "source": file_path,
                            "page": i + 1,
                            "type": "pdf",
                        },
                    })
            return pages
        except Exception as e:
            logger.error("PDF load error: %s", e)
            return []

    @staticmethod
    def _load_docx(file_path: str) -> List[dict]:
        """Load DOCX using python-docx."""
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            return [{
                "text": text,
                "metadata": {"source": file_path, "type": "docx"},
            }]
        except Exception as e:
            logger.error("DOCX load error: %s", e)
            return []

    @staticmethod
    def _load_txt(file_path: str) -> List[dict]:
        """Load plain text file."""
        try:
            text = Path(file_path).read_text(encoding="utf-8", errors="replace")
            return [{
                "text": text,
                "metadata": {"source": file_path, "type": "txt"},
            }]
        except Exception as e:
            logger.error("TXT load error: %s", e)
            return []

    @staticmethod
    def _load_csv(file_path: str) -> List[dict]:
        """Load CSV file — each row becomes a text chunk."""
        try:
            pages = []
            with open(file_path, newline="", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    text = " | ".join(f"{k}: {v}" for k, v in row.items() if v)
                    pages.append({
                        "text": text,
                        "metadata": {"source": file_path, "row": i + 1, "type": "csv"},
                    })
            return pages
        except Exception as e:
            logger.error("CSV load error: %s", e)
            return []

    @staticmethod
    def load_bytes(content: bytes, filename: str) -> List[dict]:
        """
        Load a document from bytes (useful for in-memory uploads).

        Args:
            content: File bytes.
            filename: Original filename (used to determine type).
        """
        import tempfile
        ext = Path(filename).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            return DocumentLoader.load(tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)
