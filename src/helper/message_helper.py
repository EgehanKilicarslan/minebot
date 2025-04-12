from logging import Logger
from typing import Any, Literal, cast

import hikari
import lightbulb

from debug import get_logger
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
        logger.debug(f"MessageHelper initialized with key={key}, locale={locale}, kwargs={kwargs}")

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
        logger.debug(f"Decoding message with key={self.key}, locale={self.locale}")
        message: MessageSchema = Localization.get(key=self.key, locale=self.locale)
        content: PlainMessage | EmbedMessage = message.content
        logger.debug(f"Retrieved message schema: message_type={message.message_type}")

        if message.message_type == "plain":
            content = cast(PlainMessage, content)
            result: str = content.text.format(**self.kwargs) if content.text else ""
            logger.debug(f"Decoded plain message: {result[:50]}{'...' if len(result) > 50 else ''}")
            return result

        # Must be an embed message
        logger.debug("Decoding embed message")
        content = cast(EmbedMessage, content)
        embed = hikari.Embed(
            title=content.title.format(**self.kwargs) if content.title else None,
            description=content.description.format(**self.kwargs) if content.description else None,
            url=str(content.url) if content.url else None,
            color=content.color.as_hex() if content.color else None,
            timestamp=content.timestamp,
        )
        logger.debug(f"Created base embed with title: {content.title}")

        # Add fields if they exist
        if content.fields:
            logger.debug(f"Adding {len(content.fields)} fields to embed")
            for field in content.fields:
                embed.add_field(
                    name=field.name.format(**self.kwargs) if field.name else None,
                    value=field.value.format(**self.kwargs) if field.value else None,
                    inline=field.inline,
                )

        # Set footer if exists
        if content.footer:
            logger.debug("Setting footer for embed")
            embed.set_footer(
                text=content.footer.text.format(**self.kwargs) if content.footer.text else "",
                icon=str(content.footer.icon) if content.footer.icon else None,
            )

        # Set image, thumbnail and author if they exist
        if content.image:
            logger.debug(f"Setting image: {content.image}")
            embed.set_image(str(content.image))

        if content.thumbnail:
            logger.debug(f"Setting thumbnail: {content.thumbnail}")
            embed.set_thumbnail(str(content.thumbnail))

        if content.author:
            logger.debug("Setting author information")
            embed.set_author(
                name=content.author.name.format(**self.kwargs) if content.author.name else None,
                url=str(content.author.url) if content.author.url else None,
                icon=str(content.author.icon) if content.author.icon else None,
            )

        logger.debug("Embed message fully constructed")
        return embed

    async def respond(self, ctx: ContextType, ephemeral: bool = False) -> None:
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
        logger.debug(f"Responding to context with ephemeral={ephemeral}")
        message: str | hikari.Embed = self.decode()
        message_type: Literal["embed"] | Literal["plain"] = (
            "embed" if isinstance(message, hikari.Embed) else "plain"
        )
        logger.debug(f"Sending {message_type} message response")
        await ctx.respond(content=message, ephemeral=ephemeral)
        logger.debug("Response sent successfully")
