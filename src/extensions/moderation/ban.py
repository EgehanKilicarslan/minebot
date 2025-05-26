import datetime

import hikari
import lightbulb

from database.schemas import PunishmentLogSchema, TemporaryActionSchema
from database.services import PunishmentLogService, TemporaryActionService
from helper import CommandHelper, MessageHelper, PunishmentHelper, TimeHelper, UserHelper
from model import CommandsKeys, MessageKeys

helper = CommandHelper(CommandsKeys.BAN)
loader: lightbulb.Loader = helper.get_loader()


@loader.command
class Ban(
    lightbulb.SlashCommand,
    name="extensions.ban.label",
    description="extensions.ban.description",
    default_member_permissions=helper.get_permissions(),
    hooks=helper.generate_hooks(),
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
        target_member: hikari.Member | None = await UserHelper.fetch_member(self.user)

        assert ctx.member is not None
        assert target_member is not None

        if not PunishmentHelper.can_moderate(target_member, ctx.member):
            await MessageHelper(
                MessageKeys.CAN_NOT_MODERATE, locale=ctx.interaction.locale
            ).send_response(ctx)
            return

        if self.duration:
            parsed_duration = TimeHelper(ctx.interaction.locale).parse_time_string(self.duration)

            if parsed_duration.total_seconds() > 0:
                temporary_action = await TemporaryActionService.create_or_update_temporary_action(
                    TemporaryActionSchema(
                        user_id=target_member.id,
                        punishment_type="ban",
                        expires_at=datetime.datetime.now(datetime.timezone.utc) + parsed_duration,
                    )
                )

                @ctx.client.task(
                    lightbulb.uniformtrigger(seconds=int(parsed_duration.total_seconds())),
                    max_invocations=1,
                )
                async def handle_temporary_ban() -> None:
                    await target_member.unban(
                        reason=MessageHelper(key=MessageKeys.GENERAL_NO_REASON)._decode_plain()
                    )

                    assert temporary_action.id is not None
                    await TemporaryActionService.delete_temporary_action(temporary_action.id)

        reason_messages = PunishmentHelper.get_reason(self.reason, ctx.interaction.locale)
        await target_member.ban(reason=reason_messages[0])

        await PunishmentLogService.create_or_update_punishment_log(
            PunishmentLogSchema(
                user_id=target_member.id,
                punishment_type="ban",
                reason=reason_messages[1],
                staff_id=ctx.member.id,
                source="discord",
            )
        )
