# FastAPI Framework

FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.

## Key Features

- **Fast**: Very high performance, on par with NodeJS and Go (thanks to Starlette and Pydantic)
- **Fast to code**: Increase development speed by 200% to 300%
- **Fewer bugs**: Reduce human-induced errors by about 40%
- **Intuitive**: Great editor support with auto-completion
- **Easy**: Designed to be easy to use and learn
- **Short**: Minimize code duplication
- **Robust**: Get production-ready code with automatic interactive documentation
- **Standards-based**: Based on OpenAPI and JSON Schema

## Automatic Documentation

FastAPI automatically generates two documentation interfaces:
1. Swagger UI at `/docs`
2. ReDoc at `/redoc`

## Dependency Injection

FastAPI has a powerful dependency injection system that allows you to declare dependencies as function parameters:

```python
from fastapi import Depends, FastAPI

app = FastAPI()


async def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()


@app.get("/items")
async def read_items(db=Depends(get_db)):
    return db.get_items()
```

## Type Hints

FastAPI leverages Python type hints for request validation, serialization, and documentation generation. Pydantic models define request and response schemas.
