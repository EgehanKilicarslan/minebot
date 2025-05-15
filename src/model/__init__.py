"""
Model package for Minebot, providing core data structures and enumerations.

This package defines essential models and enumerations used throughout the
application, ensuring consistency and reusability of key components.
"""

from .config import BotKeys, CommandsKeys, DatabaseKeys, SecretKeys, WebSocketKeys
from .message import CommandKeys, MenuKeys, MessageKeys, ModalKeys
from .ready import LogStyle, MessageType
from .schemas import BotSettings, DiscordEmbed, DiscordMessage, LocalizationData, TextMessage

__all__: list[str] = [
    "BotKeys",
    "CommandsKeys",
    "DatabaseKeys",
    "SecretKeys",
    "WebSocketKeys",
    "CommandKeys",
    "MessageKeys",
    "ModalKeys",
    "MenuKeys",
    "LogStyle",
    "MessageType",
    "BotSettings",
    "DiscordEmbed",
    "DiscordMessage",
    "LocalizationData",
    "TextMessage",
]
