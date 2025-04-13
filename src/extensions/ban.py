import hikari
import lightbulb

from helper import CommandHelper, MessageHelper
from model import CommandsKeys, MessageKeys

helper = CommandHelper(CommandsKeys.BAN)
loader: lightbulb.Loader = helper.get_loader()


@loader.command
class Ban(
    lightbulb.SlashCommand,
    name="extensions.ban.label",
    description="extensions.ban.description",
    default_member_permissions=helper.get_permissions(),
    hooks=[].append(helper.get_cooldown()),
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
    async def invoke(self, ctx: lightbulb.Context, client: lightbulb.Client) -> None:
        await MessageHelper(
            key=MessageKeys.BAN_COMMAND_USER_SUCCESS,
            locale=ctx.interaction.locale,
            user=self.user.mention,
        ).send_to_log_channel(client, helper)

        await MessageHelper(
            key=MessageKeys.BAN_COMMAND_USER_SUCCESS,
            locale=ctx.interaction.locale,
            user=self.user.mention,
        ).send_response(ctx)
