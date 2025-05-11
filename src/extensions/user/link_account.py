import asyncio
import secrets
import uuid

import hikari
import lightbulb

from components.models import LinkAccountConfirmModal
from helper import CommandHelper, MessageHelper, MinecraftHelper
from model import CommandsKeys, MessageKeys, MessageType

helper: CommandHelper = CommandHelper(CommandsKeys.LINK_ACCOUNT)
loader: lightbulb.Loader = helper.get_loader()


@loader.command
class LinkAccount(
    lightbulb.SlashCommand,
    name="extensions.link_account.label",
    description="extensions.link_account.description",
    default_member_permissions=helper.get_permissions(),
    hooks=helper.generate_hooks(),
    contexts=[hikari.ApplicationContextType.GUILD],
    localize=True,
):
    username: str = lightbulb.string(
        "extensions.link_account.options.username.label",
        "extensions.link_account.options.username.description",
        localize=True,
    )

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context, client: lightbulb.Client) -> None:
        user_locale: str = ctx.interaction.locale
        code: str = secrets.token_hex(5).upper()  # 10 characters

        if not await MinecraftHelper.fetch_player_status(username=self.username):
            await MessageHelper(
                key=MessageKeys.PLAYER_NOT_ONLINE,
                locale=user_locale,
                discord_username=ctx.user.username,
                discord_user_id=ctx.user.id,
                discord_user_mention=ctx.user.mention,
                minecraft_username=self.username,
                minecraft_uuid="None",
            ).send_response(ctx, ephemeral=True)

        await MinecraftHelper.send_player_message(
            message_type=MessageType.INFO,
            username=self.username,
            message=MessageHelper(
                key=MessageKeys.LINK_ACCOUNT_MINECRAFT_CONFIRMATION_CODE,
                locale=user_locale,
                confirmation_code=code,
            )._decode_plain(),
        )

        player_uuid = await MinecraftHelper.fetch_player_uuid(self.username)

        modal = LinkAccountConfirmModal(
            username=self.username,
            uuid=player_uuid or "N/A",
            code=code,
            user_locale=ctx.interaction.locale,
            helper=helper,
            client=client,
        )

        await ctx.respond_with_modal(modal.title, c_id := str(uuid.uuid4()), components=modal)
        try:
            await modal.attach(client, c_id)
        except asyncio.TimeoutError:
            await ctx.respond("Modal timed out")
