"""
Domain exception hierarchy.

Centralized domain-level error types.
All custom exceptions inherit from DomainError for clean catch semantics.
"""


class DomainError(Exception):
    """Base exception for all domain errors."""


class DocumentNotFoundError(DomainError):
    """Requested document does not exist."""


class EmbeddingError(DomainError):
    """Embedding generation failed."""


class LLMError(DomainError):
    """LLM interaction failed."""


class RetrievalError(DomainError):
    """Vector retrieval failed."""


class ConfigurationError(DomainError):
    """Invalid or missing configuration."""
