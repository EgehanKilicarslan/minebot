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
class DescriptiveElement(BaseModel):
    """Base model for labeled descriptive elements."""

    label: str
    description: str


# ==== Message Schema ====
class TextMessage(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class EmbedFieldData(BaseModel):
    name: str = Field(..., max_length=256)
    value: str = Field(..., max_length=1024)
    inline: bool = Field(default=False)


class EmbedFooterData(BaseModel):
    text: str = Field(..., max_length=2048)
    icon: HttpUrl | None = None


class EmbedAuthorData(BaseModel):
    name: str | None = Field(default=None, max_length=256)
    url: HttpUrl | None = None
    icon: HttpUrl | None = None


class DiscordEmbed(BaseModel):
    title: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=4096)
    url: HttpUrl | None = None
    color: Color | None = None
    timestamp: datetime | None = None
    fields: list[EmbedFieldData] | None = None
    footer: EmbedFooterData | None = None
    image: HttpUrl | None = None
    thumbnail: HttpUrl | None = None
    author: EmbedAuthorData | None = None

    @field_validator("fields", mode="before")
    @classmethod
    def ensure_fields_are_list(
        cls, v: list[EmbedFieldData] | EmbedFieldData
    ) -> list[EmbedFieldData]:
        return [v] if isinstance(v, EmbedFieldData) else v

    @model_validator(mode="after")
    def validate_title_or_description(self) -> "DiscordEmbed":
        if not self.title and not self.description:
            raise ValueError("Either title or description must be provided.")
        return self


class DiscordMessage(BaseModel):
    message_type: str = Field(..., pattern=r"^(plain|embed)$")
    content: TextMessage | DiscordEmbed

    @field_validator("content")
    @classmethod
    def validate_content_by_type(
        cls, v: TextMessage | DiscordEmbed, info: ValidationInfo
    ) -> TextMessage | DiscordEmbed:
        expected = TextMessage if info.data.get("message_type") == "plain" else DiscordEmbed
        if not isinstance(v, expected):
            raise ValueError(
                f"Content must be of type {expected.__name__} for message_type '{info.data.get('message_type')}'."
            )
        return v


class StatusMessagePair(BaseModel):
    """Model for success/failure message pairs."""

    success: DiscordMessage
    failure: DiscordMessage


# ==== Menu Schema =====
class ButtonBase(BaseModel):
    label: str | None = Field(..., max_length=80)
    emoji: str | None = Field(default=None, max_length=1)
    disabled: bool = False

    @model_validator(mode="after")
    def validate_label_nor_emoji(self) -> "ButtonBase":
        if not self.label and not self.emoji:
            raise ValueError("Either label or emoji must be provided.")
        return self


class SelectBase(BaseModel):
    placeholder: str | None = Field(default=None, max_length=150)
    disabled: bool | None = False


class ActionButton(ButtonBase):
    style: str = Field(..., pattern=r"^(PRIMARY|SECONDARY|SUCCESS|DANGER)$")


class HyperlinkButton(ButtonBase):
    url: HttpUrl


# ==== Modal Schema ====
class ModalBase(BaseModel):
    title: str = Field(..., max_length=80)


class TextInputField(BaseModel):
    style: str = Field(..., pattern=r"^(SHORT|PARAGRAPH)$")
    label: str = Field(..., max_length=80)
    placeholder: str | None = Field(default=None, max_length=150)
    value: str | None = Field(default=None, max_length=4000)


# ==== Reward Schema =====
class UserReward(BaseModel):
    mode: str = Field(..., pattern=r"^(ROLE|ITEM|BOTH)$")
    role: PositiveInt | list[PositiveInt] | None = None
    item: dict[str, str | list[str]] | None = None

    @field_validator("role", mode="before")
    @classmethod
    def ensure_role_id_is_list(cls, v: PositiveInt | list[PositiveInt]) -> list[PositiveInt]:
        return [v] if isinstance(v, int) else v

    @field_validator("item", mode="before")
    @classmethod
    def ensure_command_is_list(cls, v: str | list[str]) -> list[str]:
        return [v] if isinstance(v, str) else v

    @model_validator(mode="after")
    def validate_reward(self) -> "UserReward":
        if self.mode == "ROLE" and not self.role:
            raise ValueError("Role reward must be provided when mode is 'ROLE'.")
        elif self.mode == "ITEM" and not self.item:
            raise ValueError("Item reward must be provided when mode is 'ITEM'.")
        elif self.mode == "BOTH" and (not self.role or not self.item):
            raise ValueError("Both role and item rewards must be provided when mode is 'BOTH'.")
        return self


# ==== Settings Schema ====
class BotCredentials(BaseModel):
    token: str
    default_guild: PositiveInt

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Token cannot be empty or whitespace")
        return v


class BotActivity(BaseModel):
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
    def validate_streaming_url(self) -> "BotActivity":
        is_streaming = self.type == "STREAMING"
        has_url = self.url is not None
        if is_streaming and not has_url:
            raise ValueError("URL must be provided if type is 'STREAMING'")
        elif has_url and not is_streaming:
            raise ValueError("URL must be None if type is not 'STREAMING'")
        return self


class BotConfiguration(BaseModel):
    status: str | None = Field(default=None, pattern=r"^(ONLINE|IDLE|DO_NOT_DISTURB|OFFLINE)$")
    activity: BotActivity


class DatabaseConnection(BaseModel):
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


class WebSocketAuthentication(BaseModel):
    allowed_ip: str = "127.0.0.1"
    password: str = Field(default="MineAcademy", min_length=8)


class WebSocketConfig(BaseModel):
    host: str = "localhost"
    port: PositiveInt = Field(default=8080, ge=1, le=65535)
    auth: WebSocketAuthentication


class ServerConfiguration(BaseModel):
    websocket: WebSocketConfig


class BasicEvent(BaseModel):
    log: PositiveInt | None = None


class GuildBoostEvent(BasicEvent):
    reward: UserReward | None = None


class EventConfiguration(BaseModel):
    guild_boost: GuildBoostEvent | None = None


class CommandCooldown(BaseModel):
    algorithm: str = Field(..., pattern=r"^(fixed_window|sliding_window)$")
    bucket: str = Field(..., pattern=r"^(global|user|channel|guild)$")
    window_length: PositiveInt
    allowed_invocations: PositiveInt


class BasicCommand(BaseModel):
    permissions: list[str] = Field(default=["NONE"])
    cooldown: CommandCooldown | None = None

    @model_validator(mode="after")
    def validate_permissions(self) -> "BasicCommand":
        if isinstance(self.permissions, list):
            valid = hikari.Permissions.__members__
            for perm in self.permissions:
                if perm not in valid and perm != "NONE":
                    raise ValueError(f"Invalid permission: {perm}. Valid: {', '.join(valid)}")
        return self


class LoggedCommandConfig(BasicCommand):
    log: PositiveInt | None = None


class LinkAccountCommandConfig(LoggedCommandConfig):
    reward: UserReward | None = None


class SuggestCommandConfig(BasicCommand):
    pending_channel: PositiveInt
    result_channel: PositiveInt
    reward: UserReward | None = None


class CommandConfiguration(BaseModel):
    link_account: LinkAccountCommandConfig | None = None
    withdraw_rewards: LoggedCommandConfig | None = None
    ban: LoggedCommandConfig | None = None
    unban: LoggedCommandConfig | None = None
    timeout: LoggedCommandConfig | None = None
    untimeout: LoggedCommandConfig | None = None
    clear: LoggedCommandConfig | None = None
    lock: LoggedCommandConfig | None = None
    unlock: LoggedCommandConfig | None = None
    suggest: SuggestCommandConfig | None = None
    wiki: BasicCommand | None = None


class BotSettings(BaseModel):
    secret: BotCredentials
    database: DatabaseConnection
    bot: BotConfiguration | None = None
    server: ServerConfiguration | None = None
    events: EventConfiguration | None = None
    commands: CommandConfiguration | None = None


# ==== Localization Schema ====
class LinkAccountParameters(BaseModel):
    username: DescriptiveElement


class LinkAccountCommandInfo(DescriptiveElement):
    options: LinkAccountParameters


class LinkAccountMessages(BaseModel):
    class Minecraft(BaseModel):
        confirmation_code: TextMessage
        success: TextMessage
        failure: TextMessage

    minecraft: Minecraft
    user: StatusMessagePair
    log: StatusMessagePair


class LinkAccountConfirmationFields(BaseModel):
    code: TextInputField


class LinkAccountConfirmationModal(ModalBase):
    fields: LinkAccountConfirmationFields


class LinkAccountModals(BaseModel):
    confirmation: LinkAccountConfirmationModal


class LinkAccountLocalization(BaseModel):
    command: LinkAccountCommandInfo
    messages: LinkAccountMessages
    modal: LinkAccountModals


class WithdrawRewardsMessages(BaseModel):
    user: StatusMessagePair
    log: StatusMessagePair


class WithdrawRewardsLocalization(BaseModel):
    command: DescriptiveElement
    messages: WithdrawRewardsMessages


class BanParameters(BaseModel):
    user: DescriptiveElement
    duration: DescriptiveElement
    reason: DescriptiveElement


class BanCommandParameters(DescriptiveElement):
    options: BanParameters


class BanMessages(BaseModel):
    class SuccessMessage(BaseModel):
        success: DiscordMessage

    user: SuccessMessage
    log: SuccessMessage


class BanLocalization(BaseModel):
    command: BanCommandParameters
    messages: BanMessages


class UnBanParameters(BaseModel):
    user: DescriptiveElement
    reason: DescriptiveElement


class UnBanCommandParameters(DescriptiveElement):
    options: UnBanParameters


class UnBanMessages(BaseModel):
    class SuccessMessage(BaseModel):
        success: DiscordMessage

    user: SuccessMessage
    log: SuccessMessage


class UnBanLocalization(BaseModel):
    command: UnBanCommandParameters
    messages: UnBanMessages


class TimeoutParameters(BaseModel):
    user: DescriptiveElement
    duration: DescriptiveElement
    reason: DescriptiveElement


class TimeoutCommandParameters(DescriptiveElement):
    options: TimeoutParameters


class TimeoutMessages(BaseModel):
    class SuccessMessage(BaseModel):
        success: DiscordMessage

    user: SuccessMessage
    log: SuccessMessage


class TimeoutLocalization(BaseModel):
    command: TimeoutCommandParameters
    messages: TimeoutMessages


class UnTimeoutParameters(BaseModel):
    user: DescriptiveElement
    reason: DescriptiveElement


class UnTimeoutCommandParameters(DescriptiveElement):
    options: UnTimeoutParameters


class UnTimeoutMessages(BaseModel):
    class SuccessMessage(BaseModel):
        success: DiscordMessage

    user: SuccessMessage
    log: SuccessMessage


class UnTimeoutLocalization(BaseModel):
    command: UnTimeoutCommandParameters
    messages: UnTimeoutMessages


class ClearParamters(BaseModel):
    amount: DescriptiveElement
    reason: DescriptiveElement


class ClearCommandParameters(DescriptiveElement):
    options: ClearParamters


class ClearMessages(BaseModel):
    class SuccessMessage(BaseModel):
        success: DiscordMessage

    user: SuccessMessage
    log: SuccessMessage


class ClearLocalization(BaseModel):
    command: ClearCommandParameters
    messages: ClearMessages


class LockParameters(BaseModel):
    channel: DescriptiveElement
    reason: DescriptiveElement


class LockCommandParameters(DescriptiveElement):
    options: LockParameters


class LockMessages(BaseModel):
    class SuccessMessage(BaseModel):
        success: DiscordMessage

    user: SuccessMessage
    log: SuccessMessage


class LockLocalization(BaseModel):
    command: LockCommandParameters
    messages: LockMessages


class UnlockParameters(BaseModel):
    channel: DescriptiveElement
    reason: DescriptiveElement


class UnlockCommandParameters(DescriptiveElement):
    options: UnlockParameters


class UnlockMessages(BaseModel):
    class SuccessMessage(BaseModel):
        success: DiscordMessage

    user: SuccessMessage
    log: SuccessMessage


class UnlockLocalization(BaseModel):
    command: UnlockCommandParameters
    messages: UnlockMessages


class SuggestMessages(BaseModel):
    class Minecraft(BaseModel):
        approve: TextMessage
        reject: TextMessage

    class Result(BaseModel):
        approve: DiscordMessage
        reject: DiscordMessage

    minecraft: Minecraft
    user: StatusMessagePair
    pending: StatusMessagePair
    result: Result


class SuggestConfirmationButtons(BaseModel):
    approve: ActionButton
    reject: ActionButton


class SuggestMenus(BaseModel):
    confirmation: SuggestConfirmationButtons


class SuggestSendModalFields(BaseModel):
    suggestion: TextInputField


class SuggestSendModal(ModalBase):
    fields: SuggestSendModalFields


class SuggestRespondModalFields(BaseModel):
    response: TextInputField


class SuggestRespondModal(ModalBase):
    fields: SuggestRespondModalFields


class SuggestModals(BaseModel):
    send: SuggestSendModal
    respond: SuggestRespondModal


class SuggestLocalization(BaseModel):
    command: DescriptiveElement
    messages: SuggestMessages
    menu: SuggestMenus
    modal: SuggestModals


class WikiParameters(BaseModel):
    query: DescriptiveElement


class WikiCommandParameters(DescriptiveElement):
    options: WikiParameters


class WikiMessages(BaseModel):
    user: StatusMessagePair


class WikiLocalization(BaseModel):
    command: WikiCommandParameters
    messages: WikiMessages


class CommandLocalization(BaseModel):
    link_account: LinkAccountLocalization
    withdraw_rewards: WithdrawRewardsLocalization
    ban: BanLocalization
    unban: UnBanLocalization
    timeout: TimeoutLocalization
    untimeout: UnTimeoutLocalization
    clear: ClearLocalization
    lock: LockLocalization
    unlock: UnlockLocalization
    suggest: SuggestLocalization
    wiki: WikiLocalization


class GuildBoostMessages(BaseModel):
    class Log(BaseModel):
        success: DiscordMessage

    log: Log


class GuildBoostLocalization(BaseModel):
    messages: GuildBoostMessages


class EventLocalization(BaseModel):
    guild_boost: GuildBoostLocalization


class GeneralLocalization(BaseModel):
    success: DiscordMessage
    failure: DiscordMessage
    no_reason: TextMessage


class ErrorLocalization(BaseModel):
    unknown_error: DiscordMessage
    timeout_error: DiscordMessage
    user_not_found: DiscordMessage
    member_not_found: DiscordMessage
    channel_not_found: DiscordMessage
    command_execution_error: DiscordMessage
    user_record_not_found: DiscordMessage
    account_already_linked: DiscordMessage
    account_not_linked: DiscordMessage
    player_not_online: DiscordMessage
    can_not_moderate: DiscordMessage
    user_already_timed_out: DiscordMessage
    user_not_timed_out: DiscordMessage


class TimeUnitsLocalization(BaseModel):
    class BasicUnit(BaseModel):
        singular: str | list[str]
        plural: str | list[str]

        @field_validator("singular", "plural", mode="before")
        @classmethod
        def ensure_as_list(cls, v: str | list[str]) -> list[str]:
            return [v] if isinstance(v, str) else v

    year: BasicUnit
    month: BasicUnit
    week: BasicUnit
    day: BasicUnit
    hour: BasicUnit
    minute: BasicUnit
    second: BasicUnit


class LocalizationData(BaseModel):
    locale: str
    events: EventLocalization
    commands: CommandLocalization
    general: GeneralLocalization
    error: ErrorLocalization
    time_units: TimeUnitsLocalization
