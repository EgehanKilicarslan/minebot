import asyncio
import uuid

import lightbulb

from components.menus.ticket import TicketDropdownMenu
from components.modals.ticket import TicketInputModal
from helper import TicketHelper
from model.schemas import ChannelTicketCategory, ThreadTicketCategory

loader = lightbulb.Loader()


@loader.command
class TestCommand(
    lightbulb.SlashCommand,
    name="test",
    description="A test command to verify the extension system.",
):
    action = lightbulb.string("action", "action")

    creation_category: str | None = lightbulb.string(
        "creation_category",
        "Type of creation category",
        default="general",
    )

    creation_type: str | None = lightbulb.string(
        "creation_type", "Type of creation", default="thread"
    )

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        general_channel_category = ChannelTicketCategory(
            category_emoji="📩",
            category_name="General Support",
            category_description="For general support and questions.",
            channel_format="{ticket_owner_discord_username}-general",
            category_id=1377691179721949336,
            staff_role=1377691158897234000,
        )

        general_thread_category = ThreadTicketCategory(
            category_emoji="📩",
            category_name="General Support",
            category_description="For general support and questions.",
            channel_format="{ticket_owner_discord_username}-general",
            channel_id=1377691206695391383,
            staff_role=1377691158897234000,
        )

        report_channel_category = ChannelTicketCategory(
            category_emoji="🚨",
            category_name="Report",
            category_description="For reporting issues or rule violations.",
            channel_format="{ticket_owner_discord_username}-report",
            category_id=1377691179721949336,
            staff_role=1382856462048428133,
        )

        report_thread_category = ThreadTicketCategory(
            category_emoji="🚨",
            category_name="Report",
            category_description="For reporting issues or rule violations.",
            channel_format="{ticket_owner_discord_username}-report",
            channel_id=1377691208683360379,
            staff_role=1382856462048428133,
        )

        if self.action == "create":
            thread_category = (
                general_thread_category
                if self.creation_category == "general"
                else report_thread_category
            )

            channel_category = (
                general_channel_category
                if self.creation_category == "general"
                else report_channel_category
            )

            creation_type = thread_category if self.creation_type == "thread" else channel_category
            await TicketHelper.create_ticket_channel(creation_type, ctx.user)
        elif self.action == "delete":
            await TicketHelper.close_ticket_channel(ctx.channel_id)
        elif self.action == "modal":
            thread_category = (
                general_thread_category
                if self.creation_category == "general"
                else report_thread_category
            )

            channel_category = (
                general_channel_category
                if self.creation_category == "general"
                else report_channel_category
            )

            creation_type = thread_category if self.creation_type == "thread" else channel_category
            modal = TicketInputModal(
                self.creation_category or "report", creation_type, ctx.interaction.locale
            )

            await ctx.respond_with_modal(modal.title, c_id := str(uuid.uuid4()), components=modal)
            try:
                await modal.attach(ctx.client, c_id)
            except asyncio.TimeoutError:
                await ctx.respond("Modal timed out")
        elif self.action == "dropdown":
            menu = TicketDropdownMenu()

            resp = await ctx.respond(
                "Please select a ticket category from the dropdown menu.",
                components=menu,
            )
            try:
                await menu.attach(ctx.client, timeout=30)
            except asyncio.TimeoutError:
                await ctx.edit_response(resp, "Timed out!", components=[])
        elif self.action == "button":
            from components.menus.ticket import TicketButtonMenu

            menu = TicketButtonMenu()

            resp = await ctx.respond(
                "Please select a ticket category from the buttons below.",
                components=menu,
            )
            try:
                await menu.attach(ctx.client, timeout=30)
            except asyncio.TimeoutError:
                await ctx.edit_response(resp, "Timed out!", components=[])
