import hikari
from hikari import RESTGuild
from lightbulb.components.modals import Modal, ModalContext, TextInput
from pydantic import PositiveInt

from database.schemas import SuggestionSchema, UserSchema
from database.services import SuggestionService, UserService
from exceptions.command import CommandExecutionError
from helper import MINECRAFT_SERVERS, ChannelHelper, CommandHelper, MessageHelper, ModalHelper
from model import CommandsKeys, MessageKeys, ModalKeys, SecretKeys
from model.schemas import (
    LinkAccountCommandConfig,
    LinkAccountConfirmationModal,
    SuggestCommandConfig,
    SuggestRespondModal,
    SuggestSendModal,
    UserReward,
)
from settings import Localization, Settings


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
        default_params: dict[str, str] = {
            "discord_username": ctx.user.username,
            "discord_user_id": str(ctx.user.id),
            "discord_user_mention": ctx.user.mention,
            "minecraft_username": self._username,
            "minecraft_uuid": self._uuid,
        }

        # Send message to the user who submitted the modal
        await MessageHelper(key=user_key, locale=self._user_locale, **default_params).send_response(
            ctx,
            ephemeral=True,  # Make message only visible to the user
        )

        # Send message to the bot's log channel with additional Discord user details
        await MessageHelper(key=log_key, **default_params).send_to_log_channel(
            ctx.client, self._helper
        )

    def _process_items(self, items: list[str], username: str, uuid: str) -> list[str]:
        return [
            item.replace("{minecraft_username}", username).replace("{minecraft_uuid}", uuid)
            if isinstance(item, str)
            else item
            for item in items
        ]

    async def _give_rewards(
        self, ctx: ModalContext, username: str, uuid: str
    ) -> dict[str, list[str]] | None:
        """
        Award configured rewards to a user upon successful account linking.

        This method handles two types of rewards:
        1. Discord role rewards - Assigns roles to the user in the Discord guild
        2. Minecraft item rewards - Records items to be granted in different Minecraft servers

        Args:
            ctx: Modal context containing user information and client

        Returns:
            A dictionary mapping Minecraft server names to lists of item rewards,
            or None if no rewards are configured
        """
        # Fetch reward configuration from settings
        data: LinkAccountCommandConfig = Settings.get(CommandsKeys.LINK_ACCOUNT)
        rewards: UserReward | None = data.reward

        if rewards is None:
            return None

        # Extract role and item rewards from the configuration
        role_reward: list[PositiveInt] | None = rewards.role  # type: ignore
        item_reward: dict[str, list[str]] | None = rewards.item  # type: ignore
        final_item_reward: dict[str, list[str]] = {}

        # Process Discord role rewards
        if role_reward:
            try:
                guild: RESTGuild = await ctx.client.rest.fetch_guild(
                    Settings.get(SecretKeys.DEFAULT_GUILD)
                )

                # Assign each configured role to the user
                for role_id in role_reward:
                    try:
                        await ctx.client.rest.add_role_to_member(
                            guild=guild, user=ctx.user, role=role_id
                        )
                    except Exception as e:
                        # Log error and raise a command execution error
                        raise CommandExecutionError(f"Failed to assign role {role_id}: {e}")
            except Exception as e:
                # Log error and raise a command execution error
                raise CommandExecutionError(f"Failed to assign roles: {e}")

        # Process Minecraft item rewards
        if item_reward:
            default_reward: list[str] | None = item_reward.get("default", None)

            # Map server names to their specific rewards or default rewards
            for server_name, items in item_reward.items():
                if server_name in MINECRAFT_SERVERS:
                    # Use server-specific rewards
                    final_item_reward[server_name] = self._process_items(items, username, uuid)
                elif server_name != "default":  # Skip the default key itself
                    # Use default rewards for non-server keys
                    final_item_reward[server_name] = (
                        self._process_items(default_reward, username, uuid)
                        if default_reward
                        else []
                    )

            return final_item_reward

        # Return None if there are no item rewards
        return None

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
                reward_inventory=await self._give_rewards(ctx, self._username, self._uuid),
            ),
            preserve_existing=False,
        )

        # Send success messages to both user and log channel
        await self._send_messages(ctx, success=True)


class SuggestRequestModal(Modal):
    def __init__(self, user_locale: str, helper: CommandHelper) -> None:
        # Get localized modal data based on user's locale
        modal_data: SuggestSendModal = Localization.get(ModalKeys.SUGGEST_SEND, locale=user_locale)

        self.title: str = modal_data.title
        # Create the code input field with appropriate constraints
        self.input: TextInput = ModalHelper.get_field(
            instance=self, key=modal_data.fields.suggestion, min_lenght=10, max_length=4000
        )

        # Store data as private attributes for later use
        self._user_locale: str = user_locale
        self._helper: CommandHelper = helper

    async def on_submit(self, ctx: ModalContext) -> None:
        suggestion: str = ctx.value_for(self.input) or "N/A"

        common_params: dict[str, str] = {
            "discord_username": ctx.user.username,
            "discord_user_id": str(ctx.user.id),
            "discord_user_mention": ctx.user.mention,
            "suggestion": suggestion,
        }

        try:
            from components.menus import SuggestConfirmMenu

            menu = SuggestConfirmMenu(self._helper)

            await MessageHelper(
                key=MessageKeys.SUGGEST_USER_SUCCESS,
                locale=self._user_locale,
                **common_params,
            ).send_response(ctx, ephemeral=True)

            log_message: hikari.Message | None = await MessageHelper(
                key=MessageKeys.SUGGEST_LOG_SUCCESS, **common_params
            ).send_to_log_channel(ctx.client, self._helper, components=menu)

            if log_message:
                await SuggestionService.create_or_update_suggestion(
                    SuggestionSchema(
                        id=log_message.id,
                        user_id=ctx.user.id,
                        suggestion=suggestion,
                        status="pending",
                    )
                )

        except Exception:
            await MessageHelper(
                key=MessageKeys.SUGGEST_USER_FAILURE,
                locale=self._user_locale,
                **common_params,
            ).send_response(ctx, ephemeral=True)
            await MessageHelper(
                key=MessageKeys.SUGGEST_LOG_FAILURE, **common_params
            ).send_to_log_channel(ctx.client, self._helper)


class SuggestResponseModal(Modal):
    def __init__(
        self, user_locale: str, helper: CommandHelper, message_id: int, respond_type: str
    ) -> None:
        # Validate respond_type early
        valid_types = {"approved", "rejectd"}
        if respond_type not in valid_types:
            raise ValueError(f"Invalid respond_type. Must be one of: {', '.join(valid_types)}")

        # Get localized modal data based on user's locale
        modal_data: SuggestRespondModal = Localization.get(
            ModalKeys.SUGGEST_RESPOND, locale=user_locale
        )

        self.title: str = modal_data.title
        # Create the input field with appropriate constraints
        self.input: TextInput = ModalHelper.get_field(
            instance=self, key=modal_data.fields.response, min_lenght=10, max_length=4000
        )

        # Store data as private attributes for later use
        self._command_data: SuggestCommandConfig = Settings.get(CommandsKeys.SUGGEST)
        self._result_channel: int = self._command_data.result_channel
        self._user_locale: str = user_locale
        self._helper: CommandHelper = helper
        self._message_id: int = message_id
        self._respond_type: str = respond_type
        # Cache message keys mapping for respond types
        self._message_key_map: dict[str, MessageKeys] = {
            "approved": MessageKeys.SUGGEST_LOG_APPROVE,
            "rejected": MessageKeys.SUGGEST_LOG_REJECT,
        }

    def _process_items(self, items: list[str], username: str, uuid: str) -> list[str]:
        """Process items by replacing placeholders with actual values."""
        return [
            item.replace("{minecraft_username}", username).replace("{minecraft_uuid}", uuid)
            if isinstance(item, str)
            else item
            for item in items
        ]

    async def _assign_role_rewards(self, ctx: ModalContext, role_reward: list[PositiveInt]) -> None:
        """Assign role rewards to the user."""
        try:
            guild: RESTGuild = await ctx.client.rest.fetch_guild(
                Settings.get(SecretKeys.DEFAULT_GUILD)
            )

            for role_id in role_reward:
                try:
                    await ctx.client.rest.add_role_to_member(
                        guild=guild, user=ctx.user, role=role_id
                    )
                except Exception as e:
                    raise CommandExecutionError(f"Failed to assign role {role_id}: {e}")
        except Exception as e:
            raise CommandExecutionError(f"Failed to assign roles: {e}")

    async def _process_item_rewards(self, user_id: int, item_reward: dict[str, list[str]]) -> None:
        """Process and assign item rewards to the user."""
        user_data: UserSchema | None = await UserService.get_user(user_id)

        if not user_data or not user_data.minecraft_username or not user_data.minecraft_uuid:
            return

        username = user_data.minecraft_username
        uuid = user_data.minecraft_uuid
        default_reward = item_reward.get("default", None)
        final_item_reward: dict[str, list[str]] = {}

        # Map server names to their specific rewards or default rewards
        for server_name, items in item_reward.items():
            if server_name in MINECRAFT_SERVERS:
                # Use server-specific rewards
                final_item_reward[server_name] = self._process_items(items, username, uuid)
            elif server_name != "default":  # Skip the default key itself
                # Use default rewards for non-server keys
                if default_reward:
                    final_item_reward[server_name] = self._process_items(
                        default_reward, username, uuid
                    )

        # Add items to user inventory in database
        for server_name, items in final_item_reward.items():
            if items:  # Only process non-empty item lists
                await UserService.add_item(user_id, server_name, items)

    async def give_rewards(self, ctx: ModalContext, user_id: int) -> None:
        """Give rewards to the user based on configuration."""
        rewards: UserReward | None = self._command_data.reward
        if not rewards:
            return

        # Process role rewards if configured
        role_reward: list[PositiveInt] | None = rewards.role  # type: ignore
        if role_reward:
            await self._assign_role_rewards(ctx, role_reward)

        # Process item rewards if configured
        item_reward: dict[str, list[str]] | None = rewards.item  # type: ignore
        if item_reward:
            await self._process_item_rewards(user_id, item_reward)

    async def on_submit(self, ctx: ModalContext) -> None:
        """Handle modal submission."""
        try:
            # Fetch suggestion data
            suggestion_data: SuggestionSchema | None = await SuggestionService.get_suggestion(
                self._message_id
            )

            if not suggestion_data:
                await MessageHelper(
                    key=MessageKeys.GENERAL_FAILURE, locale=self._user_locale
                ).send_response(ctx, ephemeral=True)
                return

            # Fetch user data
            user: hikari.User = await ctx.client.rest.fetch_user(suggestion_data.user_id)

            # Prepare common parameters for messages
            common_params: dict[str, str] = {
                "discord_username": user.username,
                "discord_user_id": str(user.id),
                "discord_user_mention": user.mention,
                "discord_staff_username": ctx.user.username,
                "discord_staff_user_id": str(ctx.user.id),
                "discord_staff_user_mention": ctx.user.mention,
                "reason": ctx.value_for(self.input) or "N/A",
                "suggestion": suggestion_data.suggestion,
            }

            # Get the appropriate message key for this response type
            message_key = self._message_key_map.get(self._respond_type)
            if not message_key:
                raise CommandExecutionError(f"Invalid respond type: {self._respond_type}")

            # Send response to result channel
            result_channel: hikari.TextableChannel = await ChannelHelper.fetch_channel(
                ctx.client, self._result_channel, hikari.TextableChannel
            )

            await ctx.client.rest.create_message(
                result_channel,
                MessageHelper(
                    key=message_key,
                    locale=self._user_locale,
                    **common_params,
                ).decode(),
            )

            # Update suggestion status in database
            await SuggestionService.create_or_update_suggestion(
                SuggestionSchema(
                    id=suggestion_data.id,
                    user_id=suggestion_data.user_id,
                    staff_id=ctx.user.id,
                    suggestion=suggestion_data.suggestion,
                    status=self._respond_type,
                )
            )

            # Give rewards if suggestion was approved
            if self._respond_type == "approved":
                await self.give_rewards(ctx, suggestion_data.user_id)

            # Send success response to user
            await MessageHelper(
                MessageKeys.GENERAL_SUCCESS, locale=self._user_locale
            ).send_response(ctx, ephemeral=True)

            # Remove buttons from the original message
            await ctx.client.rest.edit_message(
                result_channel,
                self._message_id,
                components=[],
            )

        except CommandExecutionError as e:
            # Handle specific command execution errors
            await MessageHelper(
                key=MessageKeys.GENERAL_FAILURE, locale=self._user_locale, error_message=str(e)
            ).send_response(ctx, ephemeral=True)
        except Exception:
            # Handle general errors
            await MessageHelper(
                key=MessageKeys.CHANNEL_NOT_FOUND_ERROR, locale=self._user_locale
            ).send_response(ctx, ephemeral=True)
