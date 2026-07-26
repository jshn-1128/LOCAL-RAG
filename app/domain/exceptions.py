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


class ServiceNotAvailableError(DomainError):
    """Requested application service is not yet available.

    Raised when a dependency provider is accessed before the service
    has been initialized (e.g., during early startup or before the
    implementing milestone). Callers should handle this gracefully
    with an appropriate HTTP 503 response.
    """

    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        super().__init__(f"Service not available: {service_name}")
