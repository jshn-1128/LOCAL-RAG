"""
Tests for app.config.logging.

Covers handler setup, log levels, directory creation,
idempotency, and logger hierarchy.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from app.config.logging import setup_logging
from app.config.settings import Settings


@pytest.fixture
def temp_log_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for log files."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


@pytest.fixture
def dev_settings(temp_log_dir: Path) -> Settings:
    """Provide development settings with a temporary log directory."""
    return Settings(
        environment="development",
        log_level="DEBUG",
        log_dir=temp_log_dir,
    )


@pytest.fixture
def prod_settings(temp_log_dir: Path) -> Settings:
    """Provide production settings with a temporary log directory."""
    return Settings(
        environment="production",
        log_level="INFO",
        log_dir=temp_log_dir,
    )


def _clear_root_handlers() -> None:
    """Remove all handlers from the root logger for test isolation."""
    logging.getLogger().handlers.clear()


class TestSetupLogging:
    def test_adds_console_handler(self, dev_settings: Settings) -> None:
        _clear_root_handlers()
        setup_logging(dev_settings)
        root = logging.getLogger()
        handler_types = [type(h).__name__ for h in root.handlers]
        assert "StreamHandler" in handler_types

    def test_adds_rotating_file_handler(self, dev_settings: Settings) -> None:
        _clear_root_handlers()
        setup_logging(dev_settings)
        root = logging.getLogger()
        handler_types = [type(h).__name__ for h in root.handlers]
        assert "RotatingFileHandler" in handler_types

    def test_console_handler_respects_environment_level(
        self, dev_settings: Settings
    ) -> None:
        _clear_root_handlers()
        setup_logging(dev_settings)
        root = logging.getLogger()
        console = next(h for h in root.handlers if isinstance(h, logging.StreamHandler))
        assert console.level == logging.DEBUG

    def test_production_console_level_is_info(self, prod_settings: Settings) -> None:
        _clear_root_handlers()
        setup_logging(prod_settings)
        root = logging.getLogger()
        console = next(h for h in root.handlers if isinstance(h, logging.StreamHandler))
        assert console.level == logging.INFO

    def test_file_handler_level_is_info(self, dev_settings: Settings) -> None:
        _clear_root_handlers()
        setup_logging(dev_settings)
        root = logging.getLogger()
        file_handler = next(
            h
            for h in root.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        )
        assert file_handler.level == logging.INFO

    def test_root_logger_level_is_debug(self, dev_settings: Settings) -> None:
        _clear_root_handlers()
        setup_logging(dev_settings)
        root = logging.getLogger()
        assert root.level == logging.DEBUG

    def test_creates_log_directory(self, temp_log_dir: Path) -> None:
        _clear_root_handlers()
        settings = Settings(
            environment="development",
            log_dir=temp_log_dir / "auto_created",
        )
        expected_dir = Path(settings.log_dir)
        assert not expected_dir.exists()
        setup_logging(settings)
        assert expected_dir.exists()

    def test_idempotent_does_not_duplicate_handlers(
        self, dev_settings: Settings
    ) -> None:
        _clear_root_handlers()
        setup_logging(dev_settings)
        first_count = len(logging.getLogger().handlers)
        setup_logging(dev_settings)
        second_count = len(logging.getLogger().handlers)
        assert second_count == first_count

    def test_handler_has_utf8_encoding(self, dev_settings: Settings) -> None:
        _clear_root_handlers()
        setup_logging(dev_settings)
        root = logging.getLogger()
        file_handler = next(
            h
            for h in root.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        )
        assert file_handler.encoding == "utf-8"

    def test_logger_propagates_to_root(self, dev_settings: Settings) -> None:
        _clear_root_handlers()
        setup_logging(dev_settings)
        child = logging.getLogger("test.child")
        assert child.propagate is True

    def test_third_party_loggers_at_warning(self, dev_settings: Settings) -> None:
        _clear_root_handlers()
        setup_logging(dev_settings)
        assert logging.getLogger("httpx").level == logging.WARNING
        assert logging.getLogger("urllib3").level == logging.WARNING
        assert logging.getLogger("chromadb").level == logging.WARNING
