from datetime import datetime

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


# ==== Shared Base Models ====
class LabeledItem(BaseModel):
    """Base model for labeled items."""

    label: str
    description: str


# ==== Message Schemas ====
class PlainMessage(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class EmbedField(BaseModel):
    name: str = Field(..., max_length=256)
    value: str = Field(..., max_length=1024)
    inline: bool = Field(default=False)


class EmbedFooter(BaseModel):
    text: str = Field(..., max_length=2048)
    icon: HttpUrl | None = None


class EmbedAuthor(BaseModel):
    name: str | None = Field(default=None, max_length=256)
    url: HttpUrl | None = None
    icon: HttpUrl | None = None


class EmbedMessage(BaseModel):
    title: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=4096)
    url: HttpUrl | None = None
    color: Color | None = None
    timestamp: datetime | None = None
    fields: list[EmbedField] | None = None
    footer: EmbedFooter | None = None
    image: HttpUrl | None = None
    thumbnail: HttpUrl | None = None
    author: EmbedAuthor | None = None

    @field_validator("fields", mode="before")
    @classmethod
    def ensure_fields_are_list(cls, v: list[EmbedField] | EmbedField) -> list[EmbedField]:
        return [v] if isinstance(v, EmbedField) else v

    @model_validator(mode="after")
    def validate_title_or_description(self) -> "EmbedMessage":
        if not self.title and not self.description:
            raise ValueError("Either title or description must be provided.")
        return self


class MessageSchema(BaseModel):
    message_type: str = Field(..., pattern=r"^(plain|embed)$")
    content: PlainMessage | EmbedMessage

    @field_validator("content")
    @classmethod
    def validate_content_by_type(
        cls, v: PlainMessage | EmbedMessage, info: ValidationInfo
    ) -> PlainMessage | EmbedMessage:
        expected = PlainMessage if info.data.get("message_type") == "plain" else EmbedMessage
        if not isinstance(v, expected):
            raise ValueError(
                f"Content must be of type {expected.__name__} for message_type '{info.data.get('message_type')}'."
            )
        return v


class StatusMessages(BaseModel):
    """Base model for success/failure message pairs."""

    success: MessageSchema
    failure: MessageSchema


# ==== Menu Schema =====
class BaseButton(BaseModel):
    label: str | None = Field(..., max_length=80)
    emoji: str | None = Field(default=None, max_length=1)
    disabled: bool | None = False

    @model_validator(mode="after")
    def validate_label_nor_emoji(self) -> "BaseButton":
        if not self.label and not self.emoji:
            raise ValueError("Either label or emoji must be provided.")
        return self


class BaseSelect(BaseModel):
    placeholder: str | None = Field(default=None, max_length=150)
    disabled: bool | None = False


class InteractiveButton(BaseButton):
    style: str = Field(..., pattern=r"^(PRIMARY|SECONDARY|SUCCESS|DANGER|LINK)$")


class LinkButton(BaseButton):
    url: HttpUrl


# ==== Modal Schema ====
class BaseModal(BaseModel):
    title: str = Field(..., max_length=80)


class BaseTextInput(BaseModel):
    style: str = Field(..., pattern=r"^(SHORT|PARAGRAPH)$")
    label: str = Field(..., max_length=80)
    placeholder: str | None = Field(default=None, max_length=150)
    value: str | None = Field(default=None, max_length=4000)


# ==== Settings Schema ====
class Secret(BaseModel):
    token: str
    default_guild: PositiveInt

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Token cannot be empty or whitespace")
        return v


class Activity(BaseModel):
    name: str
    state: str | None = None
    url: str | None = Field(
        default=None,
        pattern=r"^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$",
    )
    type: str = Field(
        default="PLAYING",
        pattern=r"^(PLAYING|STREAMING|LISTENING|WATCHING|COMPETING)$",
    )

    @model_validator(mode="after")
    def validate_streaming_url(self) -> "Activity":
        is_streaming = self.type == "STREAMING"
        has_url = self.url is not None
        if is_streaming and not has_url:
            raise ValueError("URL must be provided if type is 'STREAMING'")
        elif has_url and not is_streaming:
            raise ValueError("URL must be None if type is not 'STREAMING'")
        return self


class Bot(BaseModel):
    status: str | None = Field(default=None, pattern=r"^(ONLINE|IDLE|DO_NOT_DISTURB|OFFLINE)$")
    activity: Activity


class Database(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        import re

        if not v.strip():
            raise ValueError("Database URL cannot be empty or whitespace")

        patterns = {
            "sqlite+aiosqlite://": r"sqlite\+aiosqlite:///.*",
            "mysql+aiomysql://": r"mysql\+aiomysql://[^:]+:.*@[^:]+:[0-9]+/[^/]+",
            "postgresql+asyncpg://": r"postgresql\+asyncpg://[^:]+:.*@[^:]+:[0-9]+/[^/]+",
        }

        for prefix, pattern in patterns.items():
            if v.startswith(prefix) and re.match(pattern, v):
                return v

        raise ValueError(
            "Invalid database URL format. Supported formats: sqlite+aiosqlite:///, mysql+aiomysql://, postgresql+asyncpg://"
        )


class WebSocketAuth(BaseModel):
    allowed_ip: str = "127.0.0.1"
    password: str = Field(default="MineAcademy", min_length=8)


class WebSocket(BaseModel):
    host: str = "localhost"
    port: PositiveInt = Field(default=8080, ge=1, le=65535)
    auth: WebSocketAuth


class Server(BaseModel):
    websocket: WebSocket


class Cooldown(BaseModel):
    algorithm: str = Field(..., pattern=r"^(fixed_window|sliding_window)$")
    bucket: str = Field(..., pattern=r"^(global|user|channel|guild)$")
    window_length: PositiveInt
    allowed_invocations: PositiveInt


class SimpleCommand(BaseModel):
    enabled: bool
    permissions: list[str] = Field(default=["NONE"])
    cooldown: Cooldown | None = None

    @model_validator(mode="after")
    def validate_permissions(self) -> "SimpleCommand":
        if self.enabled and isinstance(self.permissions, list):
            valid = hikari.Permissions.__members__
            for perm in self.permissions:
                if perm not in valid and perm != "NONE":
                    raise ValueError(f"Invalid permission: {perm}. Valid: {', '.join(valid)}")
        return self


class Log(BaseModel):
    enabled: bool
    channel: PositiveInt | None

    @model_validator(mode="after")
    def validate_channel(self) -> "Log":
        if self.enabled and self.channel is None:
            raise ValueError("Channel ID must be provided when logging is enabled.")
        return self


class LoggedCommand(SimpleCommand):
    log: Log


class Commands(BaseModel):
    link_account: LoggedCommand
    ban: LoggedCommand


class SettingsSchema(BaseModel):
    secret: Secret
    database: Database
    bot: Bot
    server: Server | None = None
    commands: Commands


# ==== Localization Schema ====
class LinkAccountOptions(BaseModel):
    username: LabeledItem


class LinkAccountCommand(LabeledItem):
    options: LinkAccountOptions


class LinkAccountMessages(BaseModel):
    class Minecraft(BaseModel):
        confirmation_code: PlainMessage
        success: PlainMessage
        failure: PlainMessage

    minecraft: Minecraft
    user: StatusMessages
    log: StatusMessages


class LinkAccountConfirmationModalFields(BaseModel):
    code: BaseTextInput


class LinkAccountConfirmationModal(BaseModal):
    fields: LinkAccountConfirmationModalFields


class LinkAccountModals(BaseModel):
    confirmation: LinkAccountConfirmationModal


class LinkAccount(BaseModel):
    command: LinkAccountCommand
    messages: LinkAccountMessages
    modal: LinkAccountModals


class BanOptions(BaseModel):
    user: LabeledItem
    duration: LabeledItem
    reason: LabeledItem


class BanCommand(LabeledItem):
    options: BanOptions


class BanMessages(BaseModel):
    class User(BaseModel):
        success: MessageSchema

    user: User


class Ban(BaseModel):
    command: BanCommand
    messages: BanMessages


class ErrorMessages(BaseModel):
    unknown_error: MessageSchema
    command_execution_error: MessageSchema
    user_record_not_found: MessageSchema
    account_already_linked: MessageSchema
    account_not_linked: MessageSchema
    player_not_online: MessageSchema


class LocalizationSchema(BaseModel):
    locale: str
    link_account: LinkAccount
    ban: Ban
    error: ErrorMessages
