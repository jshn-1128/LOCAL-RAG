"""
Logging configuration.

Enterprise logging system with centralized configuration.

Design:
  - Single entry point: setup_logging(settings) — called once from the composition root.
  - Console handler at configured level (DEBUG dev, INFO prod).
  - Rotating file handler at INFO level with 10 MB max, 5 backups, UTF-8 encoding.
  - Structured log format with timestamp, level, logger name, and message.
  - Logger hierarchy mirrors package structure:
      local_rag
      local_rag.api
      local_rag.application
      local_rag.config
      local_rag.domain
      local_rag.infrastructure
      local_rag.pipeline

Usage in feature modules:
  import logging
  logger = logging.getLogger(__name__)

  This automatically places loggers in the correct hierarchy
  (e.g., app.api.routes.health → local_rag.api.routes.health).

Future: JSON logging for production, OpenTelemetry integration.
"""

from __future__ import annotations

import logging
import logging.config
import logging.handlers
import sys
from pathlib import Path
from typing import cast

from app.config.constants import (
    LOG_BACKUP_COUNT,
    LOG_CONSOLE_LEVEL_PROD,
    LOG_DATE_FORMAT,
    LOG_FILE_LEVEL,
    LOG_FILENAME,
    LOG_FORMAT,
    LOG_MAX_BYTES,
)
from app.config.settings import Settings


def _create_formatter() -> logging.Formatter:
    """Create a structured log formatter."""
    return logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT, validate=True)


def _console_level(settings: Settings) -> int:
    """Determine console log level based on environment."""
    if settings.environment == "production":
        return cast(int, getattr(logging, LOG_CONSOLE_LEVEL_PROD))
    return cast(int, getattr(logging, settings.log_level))


def _resolve_log_path(settings: Settings) -> Path:
    """Resolve and ensure the log directory exists."""
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / LOG_FILENAME


def setup_logging(settings: Settings) -> None:
    """Configure the root logger with console and rotating file handlers.

    Must be called exactly once at application startup, before any
    module-level loggers are created. Idempotent — subsequent calls
    clear existing handlers and reconfigure.

    Args:
        settings: Application settings with logging configuration.
    """
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG)

    formatter = _create_formatter()

    # ── Console Handler ────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(_console_level(settings))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # ── Rotating File Handler ──────────────────────────────
    log_file = _resolve_log_path(settings)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(log_file),
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(getattr(logging, LOG_FILE_LEVEL))
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # ── Third-party library noise reduction ────────────────
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
