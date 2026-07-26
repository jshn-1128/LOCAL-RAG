"""
Tests for app.config.settings.

Covers default values, environment variable overrides, immutability,
cross-field validation, and type guarantees.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.config.settings import Settings


class TestSettingsDefaults:
    def test_app_name_default(self) -> None:
        settings = Settings()
        assert settings.app_name == "Local RAG"

    def test_app_version_default(self) -> None:
        settings = Settings()
        assert settings.app_version == "0.1.0"

    def test_environment_default_development(self) -> None:
        settings = Settings()
        assert settings.environment == "development"

    def test_log_level_default_info(self) -> None:
        settings = Settings()
        assert settings.log_level == "INFO"

    def test_chunk_size_default(self) -> None:
        settings = Settings()
        assert settings.chunk_size == 512

    def test_chunk_overlap_default(self) -> None:
        settings = Settings()
        assert settings.chunk_overlap == 64

    def test_llm_host_default(self) -> None:
        settings = Settings()
        assert settings.llm_host == "http://localhost:11434"

    def test_llm_model_default(self) -> None:
        settings = Settings()
        assert settings.llm_model == "llama3.2"

    def test_top_k_default(self) -> None:
        settings = Settings()
        assert settings.top_k == 4

    def test_embedding_model_default(self) -> None:
        settings = Settings()
        assert settings.embedding_model == "all-MiniLM-L6-v2"

    def test_paths_are_path_objects(self) -> None:
        settings = Settings()
        assert isinstance(settings.data_dir, Path)
        assert isinstance(settings.log_dir, Path)
        assert isinstance(settings.vector_store_dir, Path)
        assert isinstance(settings.documents_dir, Path)
        assert isinstance(settings.memory_db_path, Path)


class TestSettingsEnvOverride:
    def test_env_overrides_app_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LOCAL_RAG_APP_NAME", "Test RAG")
        settings = Settings()
        assert settings.app_name == "Test RAG"

    def test_env_overrides_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LOCAL_RAG_ENVIRONMENT", "production")
        settings = Settings()
        assert settings.environment == "production"

    def test_env_overrides_log_level(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LOCAL_RAG_LOG_LEVEL", "DEBUG")
        settings = Settings()
        assert settings.log_level == "DEBUG"

    def test_env_overrides_chunk_size(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LOCAL_RAG_CHUNK_SIZE", "1024")
        settings = Settings()
        assert settings.chunk_size == 1024

    def test_env_overrides_llm_host(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LOCAL_RAG_LLM_HOST", "http://192.168.1.100:11434")
        settings = Settings()
        assert settings.llm_host == "http://192.168.1.100:11434"

    def test_env_overrides_top_k(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LOCAL_RAG_TOP_K", "10")
        settings = Settings()
        assert settings.top_k == 10

    def test_env_var_not_set_uses_default(self) -> None:
        settings = Settings()
        assert settings.llm_temperature == 0.7


class TestSettingsFrozen:
    def test_settings_is_immutable(self) -> None:
        settings = Settings()
        with pytest.raises((TypeError, ValidationError)):
            settings.app_name = "Cannot Change"


class TestSettingsValidation:
    def test_chunk_overlap_exceeding_chunk_size_raises(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Settings(chunk_size=100, chunk_overlap=200)
        assert "chunk_overlap" in str(exc_info.value).lower()

    def test_chunk_overlap_equal_to_chunk_size_is_valid(self) -> None:
        settings = Settings(chunk_size=100, chunk_overlap=100)
        assert settings.chunk_overlap == 100

    def test_chunk_overlap_less_than_chunk_size_is_valid(self) -> None:
        settings = Settings(chunk_size=500, chunk_overlap=50)
        assert settings.chunk_overlap == 50

    def test_invalid_log_level_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(log_level="TRACE")  # type: ignore[arg-type]

    def test_invalid_environment_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(environment="staging")  # type: ignore[arg-type]

    def test_negative_chunk_size_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(chunk_size=-1)

    def test_zero_top_k_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(top_k=0)

    def test_negative_temperature_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(llm_temperature=-0.1)

    def test_excessive_temperature_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(llm_temperature=3.0)

    def test_zero_max_tokens_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(llm_max_tokens=0)

    def test_invalid_embedding_dimensions_for_known_model_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(embedding_model="all-MiniLM-L6-v2", embedding_dimensions=768)


class TestSettingsEnvironmentSpecific:
    def test_production_environment_is_valid(self) -> None:
        settings = Settings(environment="production")
        assert settings.environment == "production"
