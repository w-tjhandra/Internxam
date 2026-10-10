"""Backward-compatible ASGI import for deployments using ``server:app``."""

from app.main import app

__all__ = ["app"]
