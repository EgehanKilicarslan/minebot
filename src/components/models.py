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
    def __init__(
        self,
        username: str,
        uuid: str,
        code: str,
        user_locale: str,
        helper: CommandHelper,
        client: lightbulb.Client,
    ) -> None:
        modal_data: LinkAccountConfirmationModal = Localization.get(
            ModalKeys.LINK_ACCOUNT_CONFIRMATION, locale=user_locale
        )

        self.title: str = modal_data.title
        self.input: TextInput = ModalHelper.get_field(
            instance=self, key=modal_data.fields.code, min_lenght=10, max_length=10
        )

        # Store data as private attributes
        self._username: str = username
        self._uuid: str = uuid
        self._code: str = code
        self._user_locale: str = user_locale
        self._helper: CommandHelper = helper
        self._client: lightbulb.Client = client

    async def _send_messages(self, ctx: ModalContext, success: bool) -> None:
        """Helper method to send both user and log messages."""
        user_key: MessageKeys | MessageKeys = (
            MessageKeys.LINK_ACCOUNT_USER_SUCCESS
            if success
            else MessageKeys.LINK_ACCOUNT_USER_FAILURE
        )
        log_key: MessageKeys | MessageKeys = (
            MessageKeys.LINK_ACCOUNT_LOG_SUCCESS
            if success
            else MessageKeys.LINK_ACCOUNT_LOG_FAILURE
        )

        # Common parameters for both messages
        common_params: dict[str, str] = {
            "minecraft_username": self._username,
            "minecraft_uuid": self._uuid,
        }

        # User message
        await MessageHelper(key=user_key, locale=self._user_locale, **common_params).send_response(
            ctx, ephemeral=True
        )

        # Log message
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
        # Validate code input
        if self._code != ctx.value_for(self.input):
            await self._send_messages(ctx, success=False)
            return

        # Create or update user
        await UserService.create_or_update_user(
            UserSchema(
                id=ctx.user.id,
                locale=self._user_locale,
                minecraft_username=self._username,
                minecraft_uuid=self._uuid,
            )
        )

        # Send success messages
        await self._send_messages(ctx, success=True)
