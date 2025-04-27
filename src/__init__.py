"""
Minebot Rewrite

This package serves as the core of the Minebot Rewrite project, providing
essential functionality and utilities for the bot's operation. It includes
modules for handling commands, managing events, and interacting with external
services.
"""

__version__ = "1.1.0"

from . import (
    data_types,
    database,
    debug,
    events,
    extensions,
    helper,
    model,
    settings,
    utils,
    websocket,
)

__all__: list[str] = [
    "database",
    "debug",
    "events",
    "extensions",
    "helper",
    "model",
    "settings",
    "data_types",
    "utils",
    "websocket",
]
