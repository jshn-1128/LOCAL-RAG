"""
Application constants.

Centralized constants used across configuration and runtime.
All magic numbers and repeated literal values live here.

Responsibilities:
  - Define default embedding model dimensions.
  - Define supported file extensions.
  - Define logging format strings and limits.
  - Define default chunking bounds.

Allowed dependencies: stdlib only.
Forbidden dependencies: app.domain, app.config, pydantic, any framework.

Constants are intentionally NOT in Settings because they are
not user-configurable — they are engineering constants.
"""

from __future__ import annotations

# ── Embeddings ──────────────────────────────────────────────────────────────
EMBEDDING_MODEL_DIMENSIONS: dict[str, int] = {
    "all-MiniLM-L6-v2": 384,
    "all-mpnet-base-v2": 768,
    "nomic-embed-text": 768,
    "snowflake-arctic-embed-l": 1024,
}

# ── Document Loading ────────────────────────────────────────────────────────
SUPPORTED_DOCUMENT_EXTENSIONS: set[str] = {
    ".txt",
    ".md",
    ".pdf",
    ".docx",
}

DOCX_MIME_TYPE: str = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)

TEXT_MIME_TYPES: dict[str, str] = {
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".pdf": "application/pdf",
    ".docx": DOCX_MIME_TYPE,
}

MAX_FILE_SIZE_MB_DEFAULT: int = 50
MAX_FILE_SIZE_BYTES_DEFAULT: int = MAX_FILE_SIZE_MB_DEFAULT * 1024 * 1024

# ── Document Processing / Chunking ──────────────────────────────────────
# Reserved for Milestone 7 (document ingestion):
# SUPPORTED_DOCUMENT_EXTENSIONS: set[str] = {
#     ".txt", ".md", ".pdf", ".html", ".htm", ".csv", ".json", ".xml", ".yaml", ".yml",
# }

CHUNK_SIZE_MIN: int = 1
CHUNK_SIZE_MAX: int = 8192
CHUNK_OVERLAP_MIN: int = 0

# ── API ─────────────────────────────────────────────────────────────────────
API_DEFAULT_HOST: str = "0.0.0.0"
API_DEFAULT_PORT: int = 8000

# ── HTTP Middleware ─────────────────────────────────────────────────────────
CORS_MAX_AGE_DEFAULT: int = 600
REQUEST_ID_HEADER_DEFAULT: str = "X-Request-ID"
PROCESS_TIME_HEADER_DEFAULT: str = "X-Process-Time"

# ── LLM ─────────────────────────────────────────────────────────────────────
LLM_TEMPERATURE_MIN: float = 0.0
LLM_TEMPERATURE_MAX: float = 2.0
LLM_MAX_TOKENS_MIN: int = 1
LLM_TOP_K_MIN: int = 1
LLM_TOP_K_MAX: int = 100
LLM_TIMEOUT_MIN: int = 1
LLM_DEFAULT_HOST: str = "http://localhost:11434"
LLM_DEFAULT_MODEL: str = "gemma3:1b"

# ── Logging ─────────────────────────────────────────────────────────────────
LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

LOG_CONSOLE_LEVEL_PROD: str = "INFO"
LOG_FILE_LEVEL: str = "INFO"

LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT: int = 5
LOG_FILENAME: str = "local-rag.log"

# ── Memory ──────────────────────────────────────────────────────────────────
MEMORY_MAX_HISTORY_DEFAULT: int = 20
MEMORY_MAX_HISTORY_MIN: int = 1

# ── Paths ───────────────────────────────────────────────────────────────────
DEFAULT_DATA_DIR: str = "data"
DEFAULT_LOG_DIR: str = "logs"
DEFAULT_VECTOR_STORE_DIR: str = "data/vector_store"
DEFAULT_DOCUMENTS_DIR: str = "data/documents"
DEFAULT_MEMORY_DB_PATH: str = "data/conversations.db"
