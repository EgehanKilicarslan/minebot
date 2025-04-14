"""
Model package for Minebot, providing core data structures and enumerations.

This package defines essential models and enumerations used throughout the
application, ensuring consistency and reusability of key components.
"""

from .config_keys import CommandsKeys, DatabaseKeys, SecretKeys, WebSocketKeys
from .message_keys import CommandKeys, MessageKeys
from .ready_keys import LogStyle
from .schemas import EmbedMessage, LocalizationSchema, MessageSchema, PlainMessage, SettingsSchema

__all__: list[str] = [
    "CommandsKeys",
    "DatabaseKeys",
    "SecretKeys",
    "WebSocketKeys",
    "CommandKeys",
    "MessageKeys",
    "LogStyle",
    "EmbedMessage",
    "LocalizationSchema",
    "MessageSchema",
    "PlainMessage",
    "SettingsSchema",
]
