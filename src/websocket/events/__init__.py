"""
WebSocket events handling package for the minebot system.

This package provides event handlers and processors for the WebSocket server,
enabling real-time communication capabilities between the bot and external services.
Events are registered and dispatched through this system, allowing for modular
and extensible message handling.
"""

from .test import test

__all__: list[str] = ["test"]
