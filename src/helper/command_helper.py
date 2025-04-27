from logging import Logger
from typing import Literal, LiteralString, cast

import hikari
import lightbulb
import lightbulb.prefab.cooldowns
from pydantic import PositiveInt

from debug import get_logger
from model import CommandsKeys, SettingsSchema
from settings import Settings

# Get logger but with a reduced verbosity for debug messages
logger: Logger = get_logger(__name__)

SimpleCommand = SettingsSchema.Commands.SimpleCommand
LoggedCommand = SettingsSchema.Commands.LoggedCommand
Cooldown = SettingsSchema.Commands.SimpleCommand.Cooldown


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

        try:
            command_info: SimpleCommand = Settings.get(command)

            # Basic command properties
            self.command_enabled: bool = command_info.enabled

            # Convert string permissions to hikari.Permissions enum values using a list comprehension
            self.command_permissions: list[hikari.Permissions] = [
                hikari.Permissions.NONE if p == "NONE" else hikari.Permissions[p]
                for p in command_info.permissions
            ]

            # Cooldown properties
            self.command_cooldown: Cooldown | None = command_info.cooldown

            # Log command initialization with basic details
            logger.debug(
                f"[Command: {self.command_name}] Initialized - Enabled: {self.command_enabled}, "
                f"Permissions: {[p.name for p in self.command_permissions]}"
            )

            # Optional logging properties - only log if it's a LoggedCommand
            if isinstance(command_info, LoggedCommand):
                self.command_log_enabled: bool = command_info.log.enabled
                self.command_log_channel: PositiveInt | None = command_info.log.channel
                logger.debug(
                    f"[Command: {self.command_name}] Logging configured - Enabled: {self.command_log_enabled}, "
                    f"Channel: {self.command_log_channel}"
                )

        except Exception as e:
            # Provide a clear error message with the command name and error
            logger.error(f"[Command: {self.command_name}] Initialization FAILED: {str(e)}")
            raise ValueError(f"Failed to initialize command {command.name}: {str(e)}")

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
        # Special case: if NONE is in the permissions list, return 0
        if any(p == hikari.Permissions.NONE for p in self.command_permissions):
            logger.debug(f"[Command: {self.command_name}] Using NONE permission (value: 0)")
            return 0

        # Combine permissions
        combined_permissions = 0
        for permission in self.command_permissions:
            combined_permissions |= permission.value

        logger.debug(
            f"[Command: {self.command_name}] Permissions: {[p.name for p in self.command_permissions]} → {combined_permissions}"
        )
        return combined_permissions

    def get_cooldown(self) -> lightbulb.ExecutionHook | None:
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

            # Validate bucket type
            assert bucket in ["global", "user", "channel", "guild"]
            bucket_literal = cast(Literal["global", "user", "channel", "guild"], bucket)

            logger.debug(
                f"[Command: {self.command_name}] Configuring {algorithm} cooldown: "
                f"{allowed_invocations} invocations per {window_length}s ({bucket})"
            )

            match algorithm:
                case "fixed_window":
                    return lightbulb.prefab.cooldowns.fixed_window(
                        window_length=window_length,
                        allowed_invocations=allowed_invocations,
                        bucket=bucket_literal,
                    )

                case "sliding_window":
                    return lightbulb.prefab.cooldowns.sliding_window(
                        window_length=window_length,
                        allowed_invocations=allowed_invocations,
                        bucket=bucket_literal,
                    )

                case _:
                    logger.error(
                        f"[Command: {self.command_name}] Unknown cooldown algorithm: {algorithm}"
                    )
                    raise ValueError(
                        f"Unknown cooldown algorithm for {self.command_name}: {algorithm}"
                    )

        except Exception as e:
            logger.error(f"[Command: {self.command_name}] Failed to create cooldown: {str(e)}")
            # Re-raise with context for better error handling upstream
            raise ValueError(
                f"Failed to configure cooldown for {self.command_name}: {str(e)}"
            ) from e

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
        return self.command_log_channel
