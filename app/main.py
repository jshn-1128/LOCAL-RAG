"""
Application entry point for uvicorn.

Usage:
    uvicorn app.main:app --reload
    uvicorn app.main:app --host 0.0.0.0 --port 8000

Settings are loaded at module level and passed to the factory.
This is the only place Settings() is instantiated for production.
"""

from app.app import create_app
from app.config.settings import Settings

app = create_app(settings=Settings())
