"""
Application settings.

Central configuration management via Pydantic Settings.
Reads from environment variables (LOCAL_RAG_* prefix) and .env file.

Purpose:
  - Single source of truth for all runtime configuration.
  - Allows override via environment variables for containerized deployments.
  - Type-safe configuration with validation.

Future milestone: Milestone 5 — Configuration & Logging.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {
        "env_prefix": "LOCAL_RAG_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    app_name: str = "Local RAG"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    data_dir: Path = Path("data")
    vector_store_dir: Path = Path("data/vector_store")
    log_dir: Path = Path("logs")

    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "llama3.2"
    llm_host: str = "http://localhost:11434"
    llm_request_timeout: int = 120

    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 4
    temperature: float = 0.7
    max_tokens: int = 2048
