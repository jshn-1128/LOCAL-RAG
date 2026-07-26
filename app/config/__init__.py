"""
Configuration package.

Centralized settings management, logging configuration, and constants.
Only the composition root (app/app.py) instantiates Settings directly.
"""

from app.config.logging import setup_logging
from app.config.settings import Settings

__all__ = [
    "Settings",
    "setup_logging",
]
