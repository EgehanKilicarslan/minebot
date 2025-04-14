from datetime import datetime
from typing import Any

import hikari
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    PositiveInt,
    ValidationInfo,
    field_validator,
    model_validator,
)
from pydantic_extra_types.color import Color


class SettingsSchema(BaseModel):
    """Settings model with validation."""

    class Secret(BaseModel):
        token: str = Field(..., title="Bot Token", description="Discord bot token")
        default_guild: PositiveInt = Field(
            ..., title="Default Guild ID", description="Default guild ID for the bot"
        )

        @field_validator("token")
        @classmethod
        def validate_token(cls, v: str) -> str:
            if not v.strip():
                raise ValueError("Token cannot be empty or whitespace")
            return v

    class Database(BaseModel):
        url: str = Field(..., title="Database URL", description="Database connection URL")

        @field_validator("url")
        @classmethod
        def validate_url(cls, v: str) -> str:
            import re

            if not v.strip():
                raise ValueError("Database URL cannot be empty or whitespace")

            patterns: dict[str, str] = {
                "sqlite+aiosqlite://": r"sqlite\+aiosqlite:///.*",
                "mysql+aiomysql://": r"mysql\+aiomysql://[^:]+:.*@[^:]+:[0-9]+/[^/]+",
                "postgresql+asyncpg://": r"postgresql\+asyncpg://[^:]+:.*@[^:]+:[0-9]+/[^/]+",
            }

            for prefix, pattern in patterns.items():
                if v.startswith(prefix):
                    if not re.match(pattern, v):
                        raise ValueError(f"{prefix} URL must follow the correct format.")
                    return v

            raise ValueError(
                "Invalid database URL format. Supported formats are: "
                "sqlite+aiosqlite:///, mysql+aiomysql://, postgresql+asyncpg://"
            )

    class WebSocket(BaseModel):
        class Server(BaseModel):
            host: str = Field(
                default="localhost", title="Host", description="WebSocket server host"
            )
            port: PositiveInt = Field(
                default=8080, title="Port", description="WebSocket server port", ge=1, le=65535
            )

        server: Server

    class Commands(BaseModel):
        class SimpleCommand(BaseModel):
            enabled: bool = Field(..., title="Enabled", description="Is the command enabled")
            permissions: list[str] = Field(
                default=["NONE"],
                title="Permissions",
                description="Command permissions",
            )

            class Cooldown(BaseModel):
                algorithm: str = Field(
                    ...,
                    title="Algorithm",
                    description="Cooldown algorithm",
                    pattern=r"^(fixed_window|sliding_window)$",
                )
                bucket: str = Field(
                    ...,
                    title="Bucket",
                    description="Cooldown bucket",
                    pattern=r"^(global|user|channel|guild)$",
                )
                window_length: PositiveInt = Field(
                    ..., title="Window Length", description="Cooldown window length"
                )
                allowed_invocations: PositiveInt = Field(
                    ..., title="Allowed Invocations", description="Allowed invocations"
                )

            cooldown: Cooldown | None = Field(
                default=None, title="Cooldown", description="Command cooldown"
            )

            @model_validator(mode="before")
            @classmethod
            def validate_permissions(cls, data: Any) -> Any:
                if isinstance(data, dict):
                    enabled: bool = data.get("enabled", False)
                    permissions = data.get("permissions", ["NONE"])

                    if enabled and isinstance(permissions, list):
                        # Validate string permissions
                        valid_permissions = hikari.Permissions.__members__
                        for permission in permissions:
                            if permission not in valid_permissions and permission != "NONE":
                                raise ValueError(
                                    f"Invalid permission: {permission}. Valid permissions are: {', '.join(valid_permissions)}"
                                )

                return data

        class LoggedCommand(SimpleCommand):
            class Log(BaseModel):
                enabled: bool = Field(..., title="Enabled", description="Is logging enabled")
                channel: PositiveInt | None = Field(
                    ..., title="Channel ID", description="Log channel ID"
                )

                @model_validator(mode="before")
                @classmethod
                def validate_channel(cls, data: Any) -> Any:
                    if isinstance(data, dict):
                        enabled: bool = data.get("enabled", False)
                        channel: PositiveInt | None = data.get("channel")

                        if enabled and channel is None:
                            raise ValueError("Channel ID must be provided when logging is enabled.")

                    return data

            log: Log

        ban: LoggedCommand

    secret: Secret
    database: Database
    websocket: WebSocket
    commands: Commands


class PlainMessage(BaseModel):
    """Plain message model with validation."""

    text: str = Field(
        ..., title="Text", description="Plain text message", min_length=1, max_length=2000
    )


class EmbedMessage(BaseModel):
    """Embed message model with validation."""

    title: str | None = Field(
        default=None, title="Title", description="Embed title", max_length=256
    )
    description: str | None = Field(
        default=None, title="Description", description="Embed description", max_length=4096
    )
    url: HttpUrl | None = Field(default=None, title="URL", description="Embed URL")
    color: Color | None = Field(default=None, title="Color", description="Embed color")
    timestamp: datetime | None = Field(
        default=None, title="Timestamp", description="Embed timestamp"
    )

    class EmbedField(BaseModel):
        """Model for individual fields in an embed."""

        name: str = Field(..., title="Name", description="Field name", max_length=256)
        value: str = Field(..., title="Value", description="Field value", max_length=1024)
        inline: bool = Field(default=False, title="Inline", description="Inline field")

    fields: list[EmbedField] | None = Field(
        default=None, title="Fields", description="Embed fields"
    )

    class EmbedFooter(BaseModel):
        """Model for the footer of an embed."""

        text: str = Field(..., title="Text", description="Footer text", max_length=2048)
        icon: HttpUrl | None = Field(default=None, title="Icon URL", description="Footer icon URL")

    footer: EmbedFooter | None = Field(default=None, title="Footer", description="Embed footer")

    image: HttpUrl | None = Field(default=None, title="Image", description="Embed image URL")

    thumbnail: HttpUrl | None = Field(
        default=None, title="Thumbnail", description="Embed thumbnail URL"
    )

    class EmbedAuthor(BaseModel):
        """Model for the author section of an embed."""

        name: str | None = Field(
            default=None, title="Name", description="Author name", max_length=256
        )
        url: HttpUrl | None = Field(default=None, title="URL", description="Author URL")
        icon: HttpUrl | None = Field(default=None, title="Icon URL", description="Author icon URL")

    author: EmbedAuthor | None = Field(default=None, title="Author", description="Embed author")

    @field_validator("fields", mode="before")
    @classmethod
    def ensure_fields_are_list(cls, v: list[EmbedField] | EmbedField) -> list[EmbedField]:
        """Ensure that fields are always a list."""
        if isinstance(v, EmbedMessage.EmbedField):
            return [v]
        return v

    @model_validator(mode="before")
    @classmethod
    def validate_title_or_description(cls, data: Any) -> dict[str, Any]:
        """Ensure that either title or description is provided."""
        if isinstance(data, dict):
            title = data.get("title")
            description = data.get("description")

            if not title and not description:
                raise ValueError("Either title or description must be provided.")

        return data


class MessageSchema(BaseModel):
    """Message schema with validation."""

    message_type: str = Field(
        ..., title="Message Type", description="Type of the message", pattern=r"^(plain|embed)$"
    )
    content: PlainMessage | EmbedMessage = Field(...)

    @field_validator("content")
    @classmethod
    def validate_content_by_type(
        cls, v: PlainMessage | EmbedMessage, info: ValidationInfo
    ) -> PlainMessage | EmbedMessage:
        """Validate content based on the message_type."""
        message_type = info.data.get("message_type")
        if message_type == "plain" and not isinstance(v, PlainMessage):
            raise ValueError("Content must be of type PlainMessage when message_type is 'plain'.")
        if message_type == "embed" and not isinstance(v, EmbedMessage):
            raise ValueError("Content must be of type EmbedMessage when message_type is 'embed'.")
        return v


class LocalizationSchema(BaseModel):
    """Localization model with validation."""

    locale: str = Field(..., title="Locale", description="Language locale")

    class Ban(BaseModel):
        class Command(BaseModel):
            label: str = Field(..., title="Label", description="Command label")
            description: str = Field(..., title="Description", description="Command description")

            class Options(BaseModel):
                class User(BaseModel):
                    label: str = Field(..., title="Label", description="User label")
                    description: str = Field(
                        ..., title="Description", description="User description"
                    )

                class Duration(BaseModel):
                    label: str = Field(..., title="Label", description="Duration label")
                    description: str = Field(
                        ..., title="Description", description="Duration description"
                    )

                class Reason(BaseModel):
                    label: str = Field(..., title="Label", description="Reason label")
                    description: str = Field(
                        ..., title="Description", description="Reason description"
                    )

                user: User
                duration: Duration
                reason: Reason

            options: Options

        class Messages(BaseModel):
            class User(BaseModel):
                success: MessageSchema = Field(..., title="Success", description="Success message")

            user: User

        command: Command
        messages: Messages

    class Error(BaseModel):
        title: str = Field(..., title="Title", description="Error title")
        unknown: str = Field(..., title="Unknown", description="Unknown error message")

    ban: Ban
    error: Error
