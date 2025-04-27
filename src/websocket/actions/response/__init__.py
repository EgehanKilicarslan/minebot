"""
WebSocket response actions package for the minebot system.

This package contains handlers for outgoing WebSocket response actions,
providing structured replies to client requests. Response handlers format
data and ensure proper message delivery back to clients after their
requests have been processed, completing the request-response cycle of
the WebSocket communication protocol.
"""

from .test import test

__all__: list[str] = ["test"]
