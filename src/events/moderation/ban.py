from datetime import datetime, timedelta, timezone

import hikari
import lightbulb

from database.schemas import PunishmentLogSchema
from database.services import PunishmentLogService
from helper import CommandHelper, MessageHelper, PunishmentHelper, TimeHelper, UserHelper
from model import CommandsKeys, MessageKeys, PunishmentSource, PunishmentType

# Helper that manages event configuration and localization
helper: CommandHelper = CommandHelper(CommandsKeys.BAN)
loader: lightbulb.Loader = helper.get_loader()


@loader.listener(hikari.AuditLogEntryCreateEvent)
async def on_ban_create(event: hikari.AuditLogEntryCreateEvent) -> None:
    """
    Handles ban events from Discord audit logs, creating punishment entries
    and sending log messages as needed.
    """
    # --- Early validation checks ---
    # Skip if no target user or not a ban event
    if (target_id := event.entry.target_id) is None:
        return

    if event.entry.action_type != hikari.AuditLogEventType.MEMBER_BAN_ADD:
        return

    if (staff_id := event.entry.user_id) is None:
        return

    # --- Check for duplicate entries ---
    # Get the most recent ban for this user
    punishment = await PunishmentLogService.get_filtered_punishment_logs(
        user_id=target_id, punishment_type=PunishmentType.BAN, get_latest=True
    )

    create_new_entry = True

    # Convert event timestamp to UTC datetime
    event_time = datetime.fromtimestamp(event.entry.id.created_at.timestamp(), tz=timezone.utc)

    # Check if this is a duplicate entry (within 120 seconds window)
    if punishment:
        assert isinstance(punishment, PunishmentLogSchema)

        punishment_time = punishment.created_at.replace(tzinfo=timezone.utc)
        time_diff = abs((event_time - punishment_time).total_seconds())

        # If a recent punishment log exists, don't create a new one
        if time_diff < 120:
            create_new_entry = False

    # --- Get and process ban reason ---
    reason_messages = PunishmentHelper.get_reason(event.entry.reason, None)

    # --- Create database entry if needed ---
    if create_new_entry:
        # This is likely a ban performed outside the bot's commands
        punishment = await PunishmentLogService.create_or_update_punishment_log(
            PunishmentLogSchema(
                user_id=target_id,
                punishment_type=PunishmentType.BAN,
                reason=reason_messages[1],
                staff_id=staff_id,
                source=PunishmentSource.DISCORD,
            )
        )

    if not punishment:  # Safety check - don't proceed if no punishment record exists
        return

    # Ensure the punishment is a valid schema instance
    assert isinstance(punishment, PunishmentLogSchema)

    # --- Fetch user information for logging ---
    target_member = await UserHelper.fetch_user(target_id)
    staff_member = await UserHelper.fetch_user(punishment.staff_id)

    if target_member is None or staff_member is None:
        return

    # --- Prepare log message parameters ---
    common_params = {
        "discord_username": target_member.username,
        "discord_user_id": str(target_member.id),
        "discord_user_mention": target_member.mention,
        "discord_staff_username": staff_member.username,
        "discord_staff_user_id": str(staff_member.id),
        "discord_staff_user_mention": staff_member.mention,
        "duration": TimeHelper().from_timedelta(timedelta(seconds=punishment.duration or 0)),
    }

    # --- Send log message ---
    await MessageHelper(
        MessageKeys.BAN_COMMAND_LOG_SUCCESS,
        **common_params,
        reason=punishment.reason,  # Staff-facing/detailed reason
    ).send_to_log_channel(helper)
