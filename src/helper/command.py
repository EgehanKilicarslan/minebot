from logging import Logger
from typing import Literal, LiteralString, cast

import hikari
import lightbulb
from lightbulb import ExecutionHook
from lightbulb.prefab import cooldowns
from pydantic import PositiveInt

from debug import get_logger
from model import CommandsKeys
from model.schemas import BasicCommand, CommandCooldown, LoggedCommandConfig
from settings import Settings

# Get logger but with a reduced verbosity for debug messages
logger: Logger = get_logger(__name__)


class CommandHelper:
    def __init__(self, command: CommandsKeys) -> None:
        """
        Initialize a command helper.

        Args:
            command (CommandsKeys): The command key identifier.

        Attributes:
            command_name (LiteralString): The lowercase name of the command.
            command_enabled (bool): Whether the command is enabled.
            command_permissions (list[hikari.Permissions]): Permissions required to use the command.
            command_cooldown (Cooldown | None): The cooldown settings for the command.
            command_log_enabled (bool): Whether logging is enabled for the command.
            command_log_channel (PositiveInt): The channel ID for logging.
        """
        self.command_name: LiteralString = command.name.lower()
        self._cached_permission_value: int | None = None

        try:
            command_info: BasicCommand = Settings.get(command)

            # Check if command_info is None and handle it
            if command_info is None:
                self._set_defaults()
                return

            # Basic command properties
            self.command_enabled: bool = True
            self.command_cooldown: CommandCooldown | None = command_info.cooldown
            self.command_permissions = self._parse_permissions(command_info.permissions)

            # Log initialization
            self._log_initialization()

            # Handle logging configuration
            self._configure_logging(command_info)

        except Exception as e:
            # Provide a clear error message with the command name and error
            logger.error(f"[Command: {self.command_name}] Initialization FAILED: {str(e)}")
            raise ValueError(f"Failed to initialize command {command.name}: {str(e)}")

    def _set_defaults(self) -> None:
        """Set default values for command properties."""
        self.command_enabled = False
        self.command_permissions = [hikari.Permissions.NONE]
        self.command_cooldown = None
        self.command_log_enabled = False
        self.command_log_channel = None

        logger.debug(
            f"[Command: {self.command_name}] Initialized with defaults - Enabled: {self.command_enabled}, "
            f"Permissions: {[p.name for p in self.command_permissions]}"
        )

    def _parse_permissions(self, permission_strings: list[str]) -> list[hikari.Permissions]:
        """Parse string permissions into hikari.Permissions enum values."""
        return [
            hikari.Permissions.NONE if p == "NONE" else hikari.Permissions[p]
            for p in permission_strings
        ]

    def _log_initialization(self) -> None:
        """Log basic command initialization details."""
        logger.debug(
            f"[Command: {self.command_name}] Initialized - Enabled: {self.command_enabled}, "
            f"Permissions: {[p.name for p in self.command_permissions]}"
        )

    def _configure_logging(self, command_info: BasicCommand) -> None:
        """Configure logging properties if available."""
        # Default values
        self.command_log_enabled = False
        self.command_log_channel = None

        if isinstance(command_info, LoggedCommandConfig):
            self.command_log_enabled = bool(command_info.log)
            self.command_log_channel = command_info.log
            logger.debug(
                f"[Command: {self.command_name}] Logging configured - Enabled: {self.command_log_enabled}, "
                f"Channel: {self.command_log_channel}"
            )

    def get_loader(self) -> lightbulb.Loader:
        """
        Get the lightbulb command loader for the command helper.

        Returns:
            lightbulb.Loader: A loader instance that uses the command_enabled status as a condition.
        """
        logger.info(
            f"[Command: {self.command_name}] Creating command loader "
            f"(Status: {'ENABLED' if self.command_enabled else 'DISABLED'})"
        )
        return lightbulb.Loader(lambda: self.command_enabled)

    def get_permissions(self) -> int:
        """
        Get the permissions required for the command as a combined integer value.

        Returns:
            int: The combined permission value as expected by Discord's API.
        """
        # Return cached value if available
        if self._cached_permission_value is not None:
            return self._cached_permission_value

        # Special case: if NONE is in the permissions list, return 0
        if any(p == hikari.Permissions.NONE for p in self.command_permissions):
            logger.debug(f"[Command: {self.command_name}] Using NONE permission (value: 0)")
            self._cached_permission_value = 0
            return 0

        # Combine permissions
        combined_permissions = 0
        for permission in self.command_permissions:
            combined_permissions |= permission.value

        logger.debug(
            f"[Command: {self.command_name}] Permissions: {[p.name for p in self.command_permissions]} → {combined_permissions}"
        )

        # Cache the result
        self._cached_permission_value = combined_permissions
        return combined_permissions

    def generate_hooks(
        self,
        additional_hooks: ExecutionHook | list[ExecutionHook] | None = None,
    ) -> list[ExecutionHook]:
        """
        Generate a list of execution hooks for the command.

        Args:
            additional_hooks: Optional hook(s) to include with command hooks.

        Returns:
            list[lb.ExecutionHook]: A list of execution hooks, including cooldowns if configured.
        """
        logger.debug(f"[Command: {self.command_name}] Generating execution hooks")
        hooks = []

        # Add cooldown if configured
        if cooldown_hook := self._get_cooldown():
            hooks.append(cooldown_hook)

        # Add additional hooks if provided
        if additional_hooks:
            if isinstance(additional_hooks, list):
                hooks.extend(additional_hooks)
            else:
                hooks.append(additional_hooks)

        return hooks

    def has_logging_enabled(self) -> bool:
        """
        Check if logging is enabled for the command.

        Returns:
            bool: True if logging is enabled, False otherwise.
        """
        return self.command_log_enabled

    def get_log_channel_id(self) -> PositiveInt | None:
        """
        Get the ID of the channel where command logs should be sent.

        Returns:
            PositiveInt | None: The channel ID if logging is enabled, None otherwise.
        """
        return self.command_log_channel if self.command_log_enabled else None

    def _get_cooldown(self) -> ExecutionHook | None:
        """
        Get the configured cooldown as a lightbulb execution hook.

        Returns:
            lightbulb.ExecutionHook | None: The configured cooldown hook or None if no cooldown is set.
        """
        if not self.command_cooldown:
            logger.debug(f"[Command: {self.command_name}] No cooldown configured")
            return None

        try:
            window_length: PositiveInt = self.command_cooldown.window_length
            allowed_invocations: PositiveInt = self.command_cooldown.allowed_invocations
            bucket: str = self.command_cooldown.bucket
            algorithm: str = self.command_cooldown.algorithm

            # Validate bucket type with explicit error message
            valid_buckets = ["global", "user", "channel", "guild"]
            if bucket not in valid_buckets:
                raise ValueError(
                    f"Invalid bucket type: '{bucket}'. Must be one of: {valid_buckets}"
                )

            bucket_literal = cast(Literal["global", "user", "channel", "guild"], bucket)

            logger.debug(
                f"[Command: {self.command_name}] Configuring {algorithm} cooldown: "
                f"{allowed_invocations} invocations per {window_length}s ({bucket})"
            )

            # Dictionary-based cooldown creation
            cooldown_creators = {
                "fixed_window": lambda: cooldowns.fixed_window(
                    window_length=window_length,
                    allowed_invocations=allowed_invocations,
                    bucket=bucket_literal,
                ),
                "sliding_window": lambda: cooldowns.sliding_window(
                    window_length=window_length,
                    allowed_invocations=allowed_invocations,
                    bucket=bucket_literal,
                ),
            }

            if algorithm not in cooldown_creators:
                raise ValueError(f"Unknown cooldown algorithm: {algorithm}")

            return cooldown_creators[algorithm]()

        except (ValueError, KeyError, AttributeError) as e:
            # More specific exception handling
            logger.error(f"[Command: {self.command_name}] Failed to create cooldown: {str(e)}")
            raise ValueError(
                f"Failed to configure cooldown for {self.command_name}: {str(e)}"
            ) from e
