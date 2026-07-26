"""
Ollama LLM adapter.

Purpose: Communicate with locally running Ollama models via HTTP API.
Implements: LLMPort
Dependencies: httpx, ollama Python client (optional)

Supports streaming, multiple models, and custom parameters.
Future milestone: Milestone 10 — LLM Integration.
"""

from app.domain.ports.llm import LLMPort


class OllamaLLM(LLMPort):
    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llama3.2",
        timeout: int = 120,
    ) -> None:
        self._host = host
        self._model = model
        self._timeout = timeout
        self._client = None
