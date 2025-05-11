from typing import Any

import lightbulb
from lightbulb.components.modals import Modal, ModalContext, TextInput

from database.schemas import UserSchema
from database.services import UserService
from helper import CommandHelper, MessageHelper, ModalHelper
from model import MessageKeys, ModalKeys
from model.schemas import LinkAccountConfirmationModal
from settings import Localization


class LinkAccountConfirmModal(Modal):
    """
    A modal dialog for confirming the link between a Discord account and a Minecraft account.

    This modal presents a confirmation code input field to the user. If the code entered
    matches the expected code, the user's Discord account will be linked to their Minecraft
    account in the database. Success or failure messages are sent to both the user and a log channel.
    """

    def __init__(
        self,
        username: str,
        uuid: str,
        code: str,
        user_locale: str,
        helper: CommandHelper,
        client: lightbulb.Client,
    ) -> None:
        # Get localized modal data based on user's locale
        modal_data: LinkAccountConfirmationModal = Localization.get(
            ModalKeys.LINK_ACCOUNT_CONFIRMATION, locale=user_locale
        )

        self.title: str = modal_data.title
        # Create the code input field with appropriate constraints
        self.input: TextInput = ModalHelper.get_field(
            instance=self, key=modal_data.fields.code, min_lenght=10, max_length=10
        )

        # Store data as private attributes for later use
        self._username: str = username
        self._uuid: str = uuid
        self._code: str = code  # Store the expected confirmation code
        self._user_locale: str = user_locale
        self._helper: CommandHelper = helper
        self._client: lightbulb.Client = client

    async def _send_messages(self, ctx: ModalContext, success: bool) -> None:
        """
        Helper method to send both user and log messages about account linking.

        Sends appropriate localized messages to both the user and the log channel
        based on whether the account linking was successful.
        """
        # Select appropriate message keys based on success/failure
        user_key: MessageKeys = (
            MessageKeys.LINK_ACCOUNT_USER_SUCCESS
            if success
            else MessageKeys.LINK_ACCOUNT_USER_FAILURE
        )
        log_key: MessageKeys = (
            MessageKeys.LINK_ACCOUNT_LOG_SUCCESS
            if success
            else MessageKeys.LINK_ACCOUNT_LOG_FAILURE
        )

        # Common parameters for both messages
        common_params: dict[str, str] = {
            "minecraft_username": self._username,
            "minecraft_uuid": self._uuid,
        }

        # Send message to the user who submitted the modal
        await MessageHelper(key=user_key, locale=self._user_locale, **common_params).send_response(
            ctx,
            ephemeral=True,  # Make message only visible to the user
        )

        # Send message to the bot's log channel with additional Discord user details
        log_params: dict[str, Any] = {
            "discord_username": ctx.user.username,
            "discord_user_id": ctx.user.id,
            "discord_user_mention": ctx.user.mention,
            **common_params,
        }
        await MessageHelper(key=log_key, **log_params).send_to_log_channel(
            self._client, self._helper
        )

    async def on_submit(self, ctx: ModalContext) -> None:
        """
        Handle modal submission.

        Validates the confirmation code entered by the user. If valid, links the
        Discord account to the Minecraft account in the database and sends success
        messages. If invalid, sends failure messages.
        """
        # Validate that the entered code matches the expected code
        if self._code != ctx.value_for(self.input):
            # If codes don't match, send failure messages and exit
            await self._send_messages(ctx, success=False)
            return

        # Create or update user record in the database with Minecraft account details
        await UserService.create_or_update_user(
            UserSchema(
                id=ctx.user.id,
                locale=self._user_locale,
                minecraft_username=self._username,
                minecraft_uuid=self._uuid,
            )
        )

        # Send success messages to both user and log channel
        await self._send_messages(ctx, success=True)
