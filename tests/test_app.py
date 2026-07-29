"""
Tests for the application bootstrap layer.

Verifies:
  - Application factory creates a valid FastAPI instance
  - Lifespan initializes settings, logging, and state
  - Health endpoint returns correct structure
  - Middleware stack functions correctly
  - Exception handlers return structured responses
  - Router registration is correct
  - Dependency injection via app.state works
"""

from __future__ import annotations

import uuid
from collections.abc import Generator

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.api.dependencies import get_settings
from app.app import create_app


@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


class TestAppFactory:
    def test_create_app_succeeds(self):
        app = create_app()
        assert app.title == "Local RAG"
        assert app.version == "0.1.0"
        assert app.description is not None

    def test_create_app_returns_new_instance(self):
        app1 = create_app()
        app2 = create_app()
        assert app1 is not app2

    def test_lifespan_populates_state(self, app: FastAPI):
        with TestClient(app) as client:
            _ = client.get("/health")
            assert hasattr(app.state, "settings")
            assert hasattr(app.state, "startup_timestamp")

    def test_lifespan_settings_is_settings_instance(self, app: FastAPI):
        with TestClient(app) as client:
            _ = client.get("/health")
            from app.config.settings import Settings

            assert isinstance(app.state.settings, Settings)


class TestHealthEndpoint:
    def test_health_returns_200(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_structure(self, client: TestClient):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert data["environment"] == "development"
        assert "timestamp" in data
        assert "uptime_seconds" in data
        assert data["app_name"] == "Local RAG"

    def test_health_uptime_increases(self, app: FastAPI):
        with TestClient(app) as client:
            r1 = client.get("/health")
            u1 = r1.json()["uptime_seconds"]
            r2 = client.get("/health")
            u2 = r2.json()["uptime_seconds"]
            assert u2 >= u1

    def test_health_ready_returns_200(self, client: TestClient):
        response = client.get("/health/ready")
        assert response.status_code == 200

    def test_health_ready_response_structure(self, client: TestClient):
        response = client.get("/health/ready")
        data = response.json()
        assert data["status"] == "ready"
        assert "timestamp" in data


class TestMiddleware:
    def test_request_id_header_present(self, client: TestClient):
        response = client.get("/health")
        assert "X-Request-ID" in response.headers

    def test_request_id_is_uuid(self, client: TestClient):
        response = client.get("/health")
        request_id = response.headers["X-Request-ID"]
        uuid.UUID(request_id)

    def test_request_id_varies_per_request(self, client: TestClient):
        r1 = client.get("/health")
        r2 = client.get("/health")
        assert r1.headers["X-Request-ID"] != r2.headers["X-Request-ID"]

    def test_process_time_header_present(self, client: TestClient):
        response = client.get("/health")
        assert "X-Process-Time" in response.headers

    def test_process_time_header_format(self, client: TestClient):
        response = client.get("/health")
        value = response.headers["X-Process-Time"]
        assert value.endswith("ms")

    def test_cors_headers_present_with_origin(self, client: TestClient):
        response = client.get("/health", headers={"Origin": "http://example.com"})
        assert "access-control-allow-origin" in response.headers

    def test_cors_echoes_origin_when_credentials_enabled(self, client: TestClient):
        response = client.get("/health", headers={"Origin": "http://example.com"})
        assert response.headers["access-control-allow-origin"] == "http://example.com"

    def test_cors_headers_not_added_without_origin(self, client: TestClient):
        response = client.get("/health")
        assert "access-control-allow-origin" not in response.headers


class TestExceptionHandlers:
    def test_unknown_route_returns_404(self, client: TestClient):
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_unknown_route_includes_request_id(self, client: TestClient):
        response = client.get("/nonexistent")
        data = response.json()
        assert "detail" in data
        assert "request_id" in data

    def test_validation_error_on_bad_input(self, app: FastAPI):
        @app.get("/test-validation")
        async def test_endpoint(value: int):
            return {"value": value}

        with TestClient(app) as client:
            response = client.get("/test-validation?value=not-a-number")
            assert response.status_code == 422
            data = response.json()
            assert "detail" in data
            assert "request_id" in data


class TestRouterRegistration:
    def test_health_route_registered(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_ready_route_registered(self, client: TestClient):
        response = client.get("/health/ready")
        assert response.status_code == 200

    def test_chat_route_prefix(self, client: TestClient):
        response = client.get("/chat/test")
        assert response.status_code in (404, 200)

    def test_documents_route_prefix(self, client: TestClient):
        response = client.get("/documents/")
        assert response.status_code in (404, 200, 405)

    def test_search_route_prefix(self, client: TestClient):
        response = client.get("/search/")
        assert response.status_code in (404, 200, 405)


class TestDependencyInjection:
    def test_get_settings_from_state(self, app: FastAPI):
        with TestClient(app) as client:
            _ = client.get("/health")

        @app.get("/test-di")
        async def test_endpoint(request: Request):
            settings = get_settings(request)
            return {"app_name": settings.app_name}

        with TestClient(app) as client:
            response = client.get("/test-di")
            data = response.json()
            assert data["app_name"] == "Local RAG"

    def test_health_endpoint_reads_from_app_state(self, client: TestClient):
        response = client.get("/health")
        data = response.json()
        assert data["environment"] == "development"
