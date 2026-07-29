# FastAPI Tutorial (Subfolder Copy)

This is a different document with the same filename as the one in the parent directory.

## Content
FastAPI uses Pydantic models for data validation.

```python
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float
```
