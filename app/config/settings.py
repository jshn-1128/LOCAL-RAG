"""
Application settings.

Central configuration management via Pydantic Settings v2.

Design:
  - Every configuration value has a single source of truth.
  - All fields are organized into logical groups with comments.
  - Cross-field validation ensures consistency.
  - Settings are immutable after creation (frozen=True).
  - Environment variables (LOCAL_RAG_* prefix) override .env values.
  - .env file overrides defaults.

Dependency injection:
  Settings is instantiated EXACTLY ONCE in the composition root (app/app.py:lifespan).
  All consumers receive Settings through constructor injection.
  No module imports Settings() directly — it must be passed in.

Future milestone: Milestone 5 — Configuration & Logging.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.constants import (
    API_DEFAULT_HOST,
    API_DEFAULT_PORT,
    CHUNK_OVERLAP_MIN,
    CHUNK_SIZE_MAX,
    CHUNK_SIZE_MIN,
    DEFAULT_DATA_DIR,
    DEFAULT_DOCUMENTS_DIR,
    DEFAULT_LOG_DIR,
    DEFAULT_MEMORY_DB_PATH,
    DEFAULT_VECTOR_STORE_DIR,
    EMBEDDING_MODEL_DIMENSIONS,
    LLM_DEFAULT_HOST,
    LLM_DEFAULT_MODEL,
    LLM_MAX_TOKENS_MIN,
    LLM_TEMPERATURE_MAX,
    LLM_TEMPERATURE_MIN,
    LLM_TIMEOUT_MIN,
    LLM_TOP_K_MAX,
    LLM_TOP_K_MIN,
    MEMORY_MAX_HISTORY_DEFAULT,
    MEMORY_MAX_HISTORY_MIN,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LOCAL_RAG_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        frozen=True,
    )

    # ── Application Metadata ────────────────────────────────────────────────
    app_name: str = "Local RAG"
    app_version: str = "0.1.0"
    environment: Literal["development", "production"] = "development"

    # ── Logging ─────────────────────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # ── Paths ───────────────────────────────────────────────────────────────
    data_dir: Path = Path(DEFAULT_DATA_DIR)
    log_dir: Path = Path(DEFAULT_LOG_DIR)
    vector_store_dir: Path = Path(DEFAULT_VECTOR_STORE_DIR)
    documents_dir: Path = Path(DEFAULT_DOCUMENTS_DIR)
    memory_db_path: Path = Path(DEFAULT_MEMORY_DB_PATH)

    # ── API Server ──────────────────────────────────────────────────────────
    api_host: str = API_DEFAULT_HOST
    api_port: int = Field(default=API_DEFAULT_PORT, ge=1, le=65535)

    # ── Document Processing / Chunking ──────────────────────────────────────
    chunk_size: int = Field(default=512, ge=CHUNK_SIZE_MIN, le=CHUNK_SIZE_MAX)
    chunk_overlap: int = Field(default=64, ge=CHUNK_OVERLAP_MIN)

    # ── Embeddings ──────────────────────────────────────────────────────────
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimensions: int = Field(default=384, ge=1)
    embedding_device: str = "auto"

    # ── Vector Store ────────────────────────────────────────────────────────
    vector_store_type: Literal["chroma"] = "chroma"
    vector_store_collection: str = "documents"

    # ── LLM / Ollama ────────────────────────────────────────────────────────
    llm_model: str = LLM_DEFAULT_MODEL
    llm_host: str = LLM_DEFAULT_HOST
    llm_request_timeout: int = Field(default=120, ge=LLM_TIMEOUT_MIN)
    llm_temperature: float = Field(
        default=0.7, ge=LLM_TEMPERATURE_MIN, le=LLM_TEMPERATURE_MAX
    )
    llm_max_tokens: int = Field(default=2048, ge=LLM_MAX_TOKENS_MIN)

    # ── Retrieval ───────────────────────────────────────────────────────────
    top_k: int = Field(default=4, ge=LLM_TOP_K_MIN, le=LLM_TOP_K_MAX)

    # ── Conversation Memory ─────────────────────────────────────────────────
    memory_max_history: int = Field(
        default=MEMORY_MAX_HISTORY_DEFAULT, ge=MEMORY_MAX_HISTORY_MIN
    )

    # ── Cross-field Validation ──────────────────────────────────────────────

    @model_validator(mode="after")
    def _validate_chunk_overlap_not_exceeding_chunk_size(self) -> Settings:
        if self.chunk_overlap > self.chunk_size:
            raise ValueError(
                f"chunk_overlap ({self.chunk_overlap}) must not exceed "
                f"chunk_size ({self.chunk_size})"
            )
        return self

    @model_validator(mode="after")
    def _validate_embedding_dimensions_match_model(self) -> Settings:
        expected = EMBEDDING_MODEL_DIMENSIONS.get(self.embedding_model)
        if expected is not None and self.embedding_dimensions != expected:
            raise ValueError(
                f"embedding_dimensions ({self.embedding_dimensions}) does not match "
                f"expected dimensions for model '{self.embedding_model}' ({expected}). "
                f"Set LOCAL_RAG_EMBEDDING_DIMENSIONS={expected} or use a different model."
            )
        return self
