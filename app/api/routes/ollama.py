from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ollama"])


@router.get("/ollama/models")
async def list_ollama_models(request: Request) -> dict:
    settings = request.app.state.settings
    host = settings.llm_host

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(f"{host}/api/tags")
            resp.raise_for_status()
            data = resp.json()
        except httpx.RequestError as exc:
            logger.warning("Ollama unreachable at %s: %s", host, exc)
            return {"models": [], "error": f"Ollama unreachable at {host}"}
        except httpx.HTTPStatusError as exc:
            logger.warning("Ollama returned %s at %s", exc.response.status_code, host)
            return {
                "models": [],
                "error": f"Ollama returned {exc.response.status_code}",
            }

    models = [m["name"] for m in data.get("models", [])]
    return {"models": models, "current": settings.llm_model}
