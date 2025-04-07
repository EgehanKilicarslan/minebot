"""
Model package for Minebot, providing core data structures and enumerations.

This package defines essential models and enumerations used throughout the
application, ensuring consistency and reusability of key components.
"""

from .config_keys import SecretKeys
from .ready_keys import LogStyle

__all__: list[str] = ["SecretKeys", "LogStyle"]
