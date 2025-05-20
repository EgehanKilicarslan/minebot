from pathlib import Path

import hikari
import lightbulb

from helper import CommandHelper
from helper.message import MessageHelper
from helper.wiki import WikiHelper
from model import CommandsKeys
from model.message import MessageKeys

helper: CommandHelper = CommandHelper(CommandsKeys.WIKI)
loader: lightbulb.Loader = helper.get_loader()


async def autocomplete_callback(ctx: lightbulb.AutocompleteContext[str]) -> None:
    current_value: str = ctx.focused.value.lower() if isinstance(ctx.focused.value, str) else ""
    wiki_data: dict[str, Path] | None = WikiHelper.get_wiki_files(ctx.interaction.locale)

    if wiki_data is not None:
        values_to_recommend: list[str] = [
            key for key in wiki_data.keys() if current_value in key.lower()
        ]

        if len(values_to_recommend) > 25:
            values_to_recommend = values_to_recommend[:25]

        await ctx.respond(values_to_recommend)


@loader.command
class Wiki(
    lightbulb.SlashCommand,
    name="extensions.wiki.label",
    description="extensions.wiki.description",
    default_member_permissions=helper.get_permissions(),
    hooks=helper.generate_hooks(),
    contexts=[hikari.ApplicationContextType.GUILD],
    localize=True,
):
    query: str = lightbulb.string(
        "extensions.wiki.options.query.label",
        "extensions.wiki.options.query.description",
        autocomplete=autocomplete_callback,
        localize=True,
    )

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        user_locale: str = ctx.interaction.locale

        wiki_data: dict[str, Path] | None = WikiHelper.get_wiki_files(user_locale)

        if not wiki_data or self.query not in wiki_data.keys():
            await MessageHelper(
                MessageKeys.WIKI_COMMAND_USER_FAILURE,
                locale=user_locale,
            ).send_response(ctx, ephemeral=True)
            return

        content: str | None = WikiHelper.get_wiki_file_content(user_locale, self.query)

        await MessageHelper(
            MessageKeys.WIKI_COMMAND_USER_SUCCESS,
            locale=user_locale,
            query=self.query,
            result=content,
        ).send_response(ctx, ephemeral=True)
