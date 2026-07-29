"""
Ollama LLM adapter.

Purpose: Communicate with locally running Ollama models via HTTP API.
Implements: LLMPort
Dependencies: httpx

Supports streaming, multiple models, and custom parameters.
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

import httpx

from app.domain.exceptions import LLMError
from app.domain.ports.llm import LLMPort

logger = logging.getLogger(__name__)


class OllamaLLM(LLMPort):
    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llama3.2",
        timeout: int = 120,
    ) -> None:
        self._host = host.rstrip("/")
        self._model = model
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def generate(self, prompt: str, **kwargs: object) -> str:
        client = self._get_client()
        payload = self._build_payload(prompt, stream=False, **kwargs)

        try:
            response = await client.post(
                f"{self._host}/api/generate",
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()
            data: dict = response.json()
            return str(data.get("response", ""))
        except httpx.HTTPStatusError as exc:
            raise LLMError(
                f"Ollama returned status {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise LLMError(f"Ollama request failed: {exc}") from exc

    async def generate_stream(  # type: ignore[override,misc]
        self, prompt: str, **kwargs: object
    ) -> AsyncIterator[str]:
        client = self._get_client()
        payload = self._build_payload(prompt, stream=True, **kwargs)

        try:
            async with client.stream(
                "POST",
                f"{self._host}/api/generate",
                json=payload,
                timeout=self._timeout,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            token = data.get("response", "")
                            if token:
                                yield token
                            if data.get("done", False):
                                return
                        except json.JSONDecodeError:
                            continue
        except httpx.HTTPStatusError as exc:
            raise LLMError(
                f"Ollama stream returned status {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise LLMError(f"Ollama stream request failed: {exc}") from exc

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def generate_chat(
        self, messages: list[dict[str, str]], **kwargs: object
    ) -> str:
        client = self._get_client()
        payload = self._build_chat_payload(messages, stream=False, **kwargs)

        try:
            response = await client.post(
                f"{self._host}/api/chat",
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()
            data: dict = response.json()
            msg = data.get("message", {})
            return str(msg.get("content", ""))
        except httpx.HTTPStatusError as exc:
            raise LLMError(
                f"Ollama returned status {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise LLMError(f"Ollama request failed: {exc}") from exc

    async def generate_chat_stream(  # type: ignore[override,misc]
        self, messages: list[dict[str, str]], **kwargs: object
    ) -> AsyncIterator[str]:
        client = self._get_client()
        payload = self._build_chat_payload(messages, stream=True, **kwargs)

        try:
            async with client.stream(
                "POST",
                f"{self._host}/api/chat",
                json=payload,
                timeout=self._timeout,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            delta = data.get("message", {}).get("content", "")
                            if delta:
                                yield delta
                            if data.get("done", False):
                                return
                        except json.JSONDecodeError:
                            continue
        except httpx.HTTPStatusError as exc:
            raise LLMError(
                f"Ollama stream returned status {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise LLMError(f"Ollama stream request failed: {exc}") from exc

    def _build_payload(self, prompt: str, stream: bool, **kwargs: object) -> dict:
        payload: dict = {
            "model": self._model,
            "prompt": prompt,
            "stream": stream,
        }
        if "temperature" in kwargs:
            payload["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            payload["max_tokens"] = kwargs["max_tokens"]
        if "top_k" in kwargs:
            payload["top_k"] = kwargs["top_k"]
        return payload

    def _build_chat_payload(
        self, messages: list[dict[str, str]], stream: bool, **kwargs: object
    ) -> dict:
        payload: dict = {
            "model": self._model,
            "messages": messages,
            "stream": stream,
        }
        if "temperature" in kwargs:
            payload["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            payload["max_tokens"] = kwargs["max_tokens"]
        if "top_k" in kwargs:
            payload["top_k"] = kwargs["top_k"]
        return payload
