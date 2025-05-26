import datetime

import hikari
import lightbulb

from database.schemas import PunishmentLogSchema, TemporaryActionSchema
from database.services import PunishmentLogService, TemporaryActionService
from helper import CommandHelper, MessageHelper, PunishmentHelper, TimeHelper, UserHelper
from model import CommandsKeys, MessageKeys

# Helper that manages command configuration and localization
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
    # Command parameters for banning a user
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
        # Get Member object for target user
        target_member: hikari.Member | None = await UserHelper.fetch_member(self.user)

        # Safety assertions to ensure member objects are available
        assert ctx.member is not None
        assert target_member is not None

        # Common parameters used in multiple message templates
        common_params = {
            "discord_username": target_member.username,
            "discord_user_id": str(target_member.id),
            "discord_user_mention": target_member.mention,
            "discord_staff_username": ctx.member.username,
            "discord_staff_user_id": str(ctx.member.id),
            "discord_staff_user_mention": ctx.member.mention,
        }

        # Check if the moderator has sufficient permissions to ban the target
        # (prevents banning users with higher roles, other moderators, etc.)
        if not PunishmentHelper.can_moderate(target_member, ctx.member):
            await MessageHelper(
                MessageKeys.CAN_NOT_MODERATE, locale=ctx.interaction.locale
            ).send_response(ctx, ephemeral=True)
            return

        # Handle temporary ban if duration is provided
        if self.duration:
            # Convert duration string (like "1d2h") to a timedelta object
            parsed_duration = TimeHelper(ctx.interaction.locale).parse_time_string(self.duration)

            if parsed_duration.total_seconds() > 0:
                # Store temporary action in database for tracking and recovery in case of bot restart
                temporary_action = await TemporaryActionService.create_or_update_temporary_action(
                    TemporaryActionSchema(
                        user_id=target_member.id,
                        punishment_type="ban",
                        expires_at=datetime.datetime.now(datetime.timezone.utc) + parsed_duration,
                    )
                )

                # Schedule the unban task to run after the specified duration
                @ctx.client.task(
                    lightbulb.uniformtrigger(seconds=int(parsed_duration.total_seconds())),
                    max_invocations=1,  # Only run once
                )
                async def handle_temporary_ban() -> None:
                    # Unban the user when duration expires
                    await target_member.unban(
                        reason=MessageHelper(key=MessageKeys.GENERAL_NO_REASON)._decode_plain()
                    )

                    # Clean up the temporary action from the database
                    assert temporary_action.id is not None
                    await TemporaryActionService.delete_temporary_action(temporary_action.id)

        # Get formatted reason messages for different contexts (user-facing and logs)
        reason_messages = PunishmentHelper.get_reason(self.reason, ctx.interaction.locale)

        # Execute the ban with the staff-facing reason
        await target_member.ban(reason=reason_messages[1])

        # Log the punishment in the database for record-keeping
        await PunishmentLogService.create_or_update_punishment_log(
            PunishmentLogSchema(
                user_id=target_member.id,
                punishment_type="ban",
                reason=reason_messages[1],
                staff_id=ctx.member.id,
                source="discord",
            )
        )

        # Send success message to the command executor
        await MessageHelper(
            MessageKeys.BAN_COMMAND_USER_SUCCESS,
            locale=ctx.interaction.locale,
            **common_params,
            reason=reason_messages[0],  # User-facing reason
        ).send_response(ctx, ephemeral=True)

        # Log the ban in a designated moderation log channel
        await MessageHelper(
            MessageKeys.BAN_COMMAND_LOG_SUCCESS,
            locale=ctx.interaction.locale,
            **common_params,
            reason=reason_messages[1],  # Staff-facing/detailed reason
        ).send_to_log_channel(helper)
