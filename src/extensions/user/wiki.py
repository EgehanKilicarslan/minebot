from pathlib import Path

import hikari
import lightbulb

from helper import CommandHelper, MessageHelper, WikiHelper
from model import CommandsKeys, MessageKeys

# Helper that manages command configuration and localization
helper: CommandHelper = CommandHelper(CommandsKeys.WIKI)
loader: lightbulb.Loader = helper.get_loader()


# This function provides autocomplete suggestions for the wiki command
# It filters wiki entries based on the text the user has typed so far
async def autocomplete_callback(ctx: lightbulb.AutocompleteContext[str]) -> None:
    # Get the current value typed by user and convert to lowercase for case-insensitive matching
    current_value: str = ctx.focused.value.lower() if isinstance(ctx.focused.value, str) else ""
    # Get available wiki files for user's language/locale
    wiki_data: dict[str, Path] | None = WikiHelper.get_wiki_files(ctx.interaction.locale)

    if wiki_data is not None:
        # Filter wiki entries that contain the current input string
        values_to_recommend: list[str] = [
            key for key in wiki_data.keys() if current_value in key.lower()
        ]

        # Discord only allows up to 25 autocomplete suggestions
        if len(values_to_recommend) > 25:
            values_to_recommend = values_to_recommend[:25]

        # Send the filtered list as suggestions to the user
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
    # Define the query parameter that users will provide
    query: str = lightbulb.string(
        "extensions.wiki.options.query.label",
        "extensions.wiki.options.query.description",
        autocomplete=autocomplete_callback,
        localize=True,
    )

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        # Get the user's locale for localized responses
        user_locale: str = ctx.interaction.locale

        # Get wiki files available for the user's locale
        wiki_data: dict[str, Path] | None = WikiHelper.get_wiki_files(user_locale)

        # Check if the requested wiki entry exists
        if not wiki_data or self.query not in wiki_data.keys():
            # Send failure message if wiki entry not found
            await MessageHelper(
                MessageKeys.WIKI_COMMAND_USER_FAILURE,
                locale=user_locale,
            ).send_response(ctx, ephemeral=True)
            return

        # Retrieve the content of the requested wiki entry
        content: str | None = WikiHelper.get_wiki_file_content(user_locale, self.query)

        # Send successful response with wiki content to the user
        await MessageHelper(
            MessageKeys.WIKI_COMMAND_USER_SUCCESS,
            locale=user_locale,
            query=self.query,
            result=content,
        ).send_response(ctx, ephemeral=True)
