import hikari
import lightbulb

from helper.message_helper import MessageHelper
from model.message_keys import MessageKeys

loader = lightbulb.Loader()


@loader.command
class Ban(
    lightbulb.SlashCommand,
    name="extensions.ban.label",
    description="extensions.ban.description",
    default_member_permissions=hikari.Permissions.BAN_MEMBERS,
    contexts=[hikari.ApplicationContextType.GUILD],
    localize=True,
):
    user: hikari.User = lightbulb.user(
        "extensions.ban.options.user.label",
        "extensions.ban.options.user.description",
        localize=True,
    )

    duration: str | None = lightbulb.string(
        "extensions.ban.options.duration.label",
        "extensions.ban.options.duration.description",
        localize=True,
        default=None,
    )

    reason: str | None = lightbulb.string(
        "extensions.ban.options.reason.label",
        "extensions.ban.options.reason.description",
        localize=True,
        default=None,
    )

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        await MessageHelper(
            key=MessageKeys.BAN_COMMAND_USER_SUCCESS,
            locale=ctx.interaction.locale,
            user=self.user.mention,
        ).respond(ctx)
