# Advanced FastAPI Patterns

Building on the FastAPI introduction, this covers production patterns and best practices.

## Middleware

FastAPI supports several types of middleware for cross-cutting concerns:

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Error Handling

FastAPI provides exception handlers for custom error responses:

```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


@app.exception_handler(HTTPException)
async def custom_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "request_id": request.state.request_id},
    )
```

## Background Tasks

For operations that should run after the response:

```python
from fastapi import BackgroundTasks


@app.post("/send-email")
async def send_email(email: str, background: BackgroundTasks):
    background.add_task(send_email_task, email)
    return {"message": "Email queued"}
```

## Dependency Injection Patterns

### Factory Pattern with Lifespan
```python
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.db = Database()
    yield
    # Shutdown
    await app.state.db.close()
```

## WebSockets

FastAPI supports WebSocket connections for real-time communication:

```python
from fastapi import WebSocket


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")
```

## Testing FastAPI Applications

Using TestClient from Starlette:

```python
from fastapi.testclient import TestClient


def test_read_main():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

## Performance Optimization

- Use async endpoints for I/O-bound operations
- Leverage dependency caching
- Enable HTTP keep-alive
- Use Gunicorn + Uvicorn workers for production
- Implement response compression
- Use database connection pooling
