"""
WebSocket package for providing real-time communication capabilities.

This package provides a WebSocket server implementation that allows
for bidirectional communication between the bot and external services.
It includes an action-based system for handling different message types
and a manager for the server lifecycle.
"""

from .action_registry import action_handlers, websocket_action
from .listener import handle_connection
from .server import initialize_websocket_server, shutdown_websocket_server

__all__: list[str] = [
    "action_handlers",
    "websocket_action",
    "handle_connection",
    "initialize_websocket_server",
    "shutdown_websocket_server",
]
