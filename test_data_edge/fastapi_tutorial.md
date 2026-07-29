# FastAPI Tutorial

FastAPI is a modern web framework for building APIs with Python.

## Installation
```bash
pip install fastapi uvicorn
```

## Basic Example
```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}
```

## Path Parameters
```python
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```
