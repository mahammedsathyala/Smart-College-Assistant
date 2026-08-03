"""
Smart College Assistant — Configuration Module
Settings, environment loading, and application configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env file ──────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base configuration class."""

    # ── Flask Core ───────────────────────────────────────────
    SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-in-prod")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    PORT: int = int(os.getenv("FLASK_PORT", 5000))
    HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))

    # ── IBM watsonx.ai ───────────────────────────────────────
    IBM_API_KEY: str = os.getenv("IBM_API_KEY", "")
    IBM_PROJECT_ID: str = os.getenv("IBM_PROJECT_ID", "")
    IBM_URL: str = os.getenv("IBM_URL", "https://us-south.ml.cloud.ibm.com")
    IBM_MODEL_ID: str = os.getenv("IBM_MODEL_ID", "ibm/granite-13b-chat-v2")

    # ── Database ─────────────────────────────────────────────
    DATABASE_PATH: str = str(BASE_DIR / "database" / "college.db")
    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"

    # ── Vector Store ─────────────────────────────────────────
    FAISS_INDEX_PATH: str = str(BASE_DIR / "vectorstore" / "index")

    # ── Embeddings ───────────────────────────────────────────
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # ── Session ──────────────────────────────────────────────
    SESSION_TYPE: str = os.getenv("SESSION_TYPE", "filesystem")
    SESSION_LIFETIME_MINUTES: int = int(os.getenv("SESSION_LIFETIME_MINUTES", 60))
    SESSION_FILE_DIR: str = str(BASE_DIR / "logs" / "sessions")

    # ── Logging ──────────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = str(BASE_DIR / "logs" / "app.log")
    ERROR_LOG_FILE: str = str(BASE_DIR / "logs" / "error.log")
    AI_LOG_FILE: str = str(BASE_DIR / "logs" / "ai.log")
    AUDIT_LOG_FILE: str = str(BASE_DIR / "logs" / "audit.log")

    # ── Security ─────────────────────────────────────────────
    WTF_CSRF_ENABLED: bool = os.getenv("WTF_CSRF_ENABLED", "True").lower() == "true"
    BCRYPT_ROUNDS: int = 12

    # ── File Upload ──────────────────────────────────────────
    UPLOAD_FOLDER: str = str(BASE_DIR / "assets" / "uploads")
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".txt", ".csv"}

    # ── AI Generation ────────────────────────────────────────
    MAX_NEW_TOKENS: int = 1024
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    TOP_K: int = 50

    # ── RAG ──────────────────────────────────────────────────
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RETRIEVER_K: int = 4

    # ── Pagination ───────────────────────────────────────────
    PAGE_SIZE: int = 10

    @classmethod
    def is_watsonx_configured(cls) -> bool:
        """Check if IBM watsonx.ai credentials are present."""
        return bool(cls.IBM_API_KEY and cls.IBM_PROJECT_ID)

    @classmethod
    def ensure_directories(cls) -> None:
        """Create required directories if they don't exist."""
        dirs = [
            BASE_DIR / "database",
            BASE_DIR / "vectorstore" / "index",
            BASE_DIR / "logs" / "sessions",
            BASE_DIR / "assets" / "uploads",
            BASE_DIR / "assets" / "sample_docs",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    WTF_CSRF_ENABLED = True


# ── Active config ────────────────────────────────────────────
env = os.getenv("FLASK_ENV", "development")
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
ActiveConfig = config_map.get(env, DevelopmentConfig)
