"""
Model package for Minebot, providing core data structures and enumerations.

This package defines essential models and enumerations used throughout the
application, ensuring consistency and reusability of key components.
"""

from .config import BotKeys, CommandsKeys, DatabaseKeys, EventsKeys, SecretKeys, WebSocketKeys
from .message import MenuKeys, MessageKeys, ModalKeys, TimeUnitKeys
from .ready import LogStyle, MessageType, PunishmentSource, PunishmentType
from .schemas import BotSettings, DiscordEmbed, DiscordMessage, LocalizationData, TextMessage

__all__: list[str] = [
    "BotKeys",
    "CommandsKeys",
    "DatabaseKeys",
    "EventsKeys",
    "SecretKeys",
    "WebSocketKeys",
    "MessageKeys",
    "ModalKeys",
    "TimeUnitKeys",
    "MenuKeys",
    "LogStyle",
    "MessageType",
    "PunishmentSource",
    "PunishmentType",
    "BotSettings",
    "DiscordEmbed",
    "DiscordMessage",
    "LocalizationData",
    "TextMessage",
]
