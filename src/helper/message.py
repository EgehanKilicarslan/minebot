from logging import Logger
from typing import Any, cast

import hikari
import lightbulb

from debug import get_logger
from helper import ChannelHelper, CommandHelper
from model import EmbedMessage, MessageKeys, MessageSchema, PlainMessage
from settings import Localization

# Set up logger for this module
logger: Logger = get_logger(__name__)

ContextType = (
    lightbulb.Context | lightbulb.components.MenuContext | lightbulb.components.ModalContext
)


class MessageHelper:
    """
    A helper class for handling message localization and responses.

    This class provides functionality to retrieve, format, and send localized messages
    based on message keys and the specified locale. It can handle both plain text and
    embedded rich messages.

    Attributes:
        key (MessageKeys): The key identifier for the message to be retrieved.
        locale (str | hikari.Locale | None): The locale for the message. If None,
            the default locale will be used.
        kwargs (dict[str, Any]): Format parameters to be substituted in the message.

    Methods:
        decode(): Retrieves and formats the message based on the key, locale, and kwargs.
        respond(ctx, ephemeral): Sends the formatted message as a response to the given context.
    """

    def __init__(
        self, key: MessageKeys, locale: str | hikari.Locale | None = None, **kwargs
    ) -> None:
        """
        Initialize a new MessageHelper instance.

        This helper is used to manage localized messages for an application,
        allowing for messages to be retrieved by key and locale.

        Args:
            key (MessageKeys): The message key to identify the message.
            locale (str | hikari.Locale | None, optional): The locale to use for the message.
                If None, the default locale will be used. Defaults to None.
            **kwargs: Additional arguments to format the message with.

        Note:
            The initialization is logged at debug level with the provided parameters.
        """
        self.key: MessageKeys = key
        self.locale: str | hikari.Locale | None = locale
        self.kwargs: dict[str, Any] = kwargs
        logger.debug(f"[Message: {key.name}] Initialized with locale: {locale}, params: {kwargs}")

    def _decode_plain(self, content: PlainMessage | None = None) -> str:
        if content is None:
            content = cast(PlainMessage, Localization.get(key=self.key, locale=self.locale))

        result: str = content.text.format(**self.kwargs) if content.text else ""
        truncated: str = result[:50] + ("..." if len(result) > 50 else "")
        logger.debug(f"[Message: {self.key.name}] Plain content: {truncated}")
        return result

    def _decode_embed(self, content: EmbedMessage | None = None) -> hikari.Embed:
        if content is None:
            content = cast(EmbedMessage, Localization.get(key=self.key, locale=self.locale))

        embed = hikari.Embed(
            title=content.title.format(**self.kwargs) if content.title else None,
            description=content.description.format(**self.kwargs) if content.description else None,
            url=str(content.url) if content.url else None,
            color=content.color.as_hex() if content.color else None,
            timestamp=content.timestamp,
        )

        # Add fields if they exist
        if content.fields:
            logger.debug(f"[Message: {self.key.name}] Adding {len(content.fields)} fields")
            for field in content.fields:
                embed.add_field(
                    name=field.name.format(**self.kwargs) if field.name else None,
                    value=field.value.format(**self.kwargs) if field.value else None,
                    inline=field.inline,
                )

        # Set footer if exists
        if content.footer:
            embed.set_footer(
                text=content.footer.text.format(**self.kwargs) if content.footer.text else "",
                icon=str(content.footer.icon) if content.footer.icon else None,
            )

        # Set image, thumbnail and author if they exist
        if content.image:
            embed.set_image(str(content.image))

        if content.thumbnail:
            embed.set_thumbnail(str(content.thumbnail))

        if content.author:
            embed.set_author(
                name=content.author.name.format(**self.kwargs) if content.author.name else None,
                url=str(content.author.url) if content.author.url else None,
                icon=str(content.author.icon) if content.author.icon else None,
            )

        logger.debug(f"[Message: {self.key.name}] Embed message construction completed")
        return embed

    def decode(self) -> str | hikari.Embed:
        """
        Decodes a message into either a plain string or a hikari.Embed object.

        This method retrieves a message schema from the localization system using the key and locale
        specified in the instance. It then formats the message content with the provided kwargs.

        If the message type is "plain", it returns a formatted string.
        If the message type is "embed", it constructs and returns a hikari.Embed object with all
        the specified properties (title, description, fields, footer, image, thumbnail, author).

        Returns:
            str | hikari.Embed: A formatted string for plain messages or a fully constructed
                               hikari.Embed object for embed messages.

        Logs:
            Debug information about the decoding process.
        """
        logger.debug(f"[Message: {self.key.name}] Decoding {self.locale} message")
        message: MessageSchema = Localization.get(key=self.key, locale=self.locale)
        content: PlainMessage | EmbedMessage = message.content

        if message.message_type == "plain":
            content = cast(PlainMessage, content)
            return self._decode_plain(content)

        # Must be an embed message
        logger.debug(f"[Message: {self.key.name}] Building embed message")
        content = cast(EmbedMessage, content)
        return self._decode_embed(content)

    async def send_response(self, ctx: ContextType, ephemeral: bool = False) -> None:
        """
        Responds to a context with a message.

        This method decodes the message and sends it as a response to the given context.
        The message can be either a plain text or an embed.

        Args:
            ctx: The context to respond to. Can be any context type that supports the respond method.
            ephemeral: Whether the response should be ephemeral (only visible to the command invoker).
                        Defaults to False.

        Raises:
            Any exceptions that might be raised by the context's respond method.
        """
        message: str | hikari.Embed = self.decode()
        message_type = "embed" if isinstance(message, hikari.Embed) else "plain"

        logger.debug(
            f"[Message: {self.key.name}] Responding with {message_type} message (ephemeral: {ephemeral})"
        )

        await ctx.respond(content=message, ephemeral=ephemeral)
        logger.debug(f"[Message: {self.key.name}] Response sent successfully")

    async def send_to_log_channel(self, client: lightbulb.Client, helper: CommandHelper) -> None:
        """
        Sends the message to the configured log channel.

        This method checks if logging is enabled, retrieves the log channel ID,
        fetches the channel, and then sends the decoded message to it.

        Args:
            client: The Lightbulb client instance.
            helper: The CommandHelper instance to check logging configuration.

        Returns:
            None: The method returns early if logging is disabled or no channel is configured.
        """
        logger.debug(f"[Message: {self.key.name}] Checking if logging is enabled")
        if not helper.has_logging_enabled():
            logger.debug(f"[Message: {self.key.name}] Logging is disabled, skipping")
            return

        logger.debug(f"[Message: {self.key.name}] Getting log channel ID")
        channel_id = helper.get_log_channel_id()
        if not channel_id:
            logger.debug(f"[Message: {self.key.name}] No log channel configured, skipping")
            return

        logger.debug(f"[Message: {self.key.name}] Fetching channel {channel_id}")
        channel: hikari.TextableGuildChannel = await ChannelHelper.fetch_channel(
            client, channel_id, hikari.TextableGuildChannel
        )

        message: str | hikari.Embed = self.decode()
        message_type = "embed" if isinstance(message, hikari.Embed) else "plain"
        logger.debug(f"[Message: {self.key.name}] Sending {message_type} message to log channel")

        await channel.send(content=message)
        logger.debug(f"[Message: {self.key.name}] Log message sent successfully")
