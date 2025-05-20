import asyncio
import uuid

import hikari
import lightbulb

from components.modals import SuggestRequestModal
from helper import CommandHelper
from helper.message import MessageHelper
from model import CommandsKeys
from model.message import MessageKeys

helper: CommandHelper = CommandHelper(CommandsKeys.SUGGEST)
loader: lightbulb.Loader = helper.get_loader()


@loader.command
class Suggest(
    lightbulb.SlashCommand,
    name="extensions.suggest.label",
    description="extensions.suggest.description",
    default_member_permissions=helper.get_permissions(),
    hooks=helper.generate_hooks(),
    contexts=[hikari.ApplicationContextType.GUILD],
    localize=True,
):
    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        modal = SuggestRequestModal(ctx.interaction.locale, helper)

        await ctx.respond_with_modal(modal.title, c_id := str(uuid.uuid4()), components=modal)
        try:
            await modal.attach(ctx.client, c_id)
        except asyncio.TimeoutError:
            # Handle case when user doesn't complete the modal in time
            await MessageHelper(MessageKeys.TIMEOUT_ERROR).send_response(ctx, ephemeral=True)
