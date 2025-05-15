from logging import Logger

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import PunishmentLog
from database.schemas import PunishmentLogSchema
from debug import get_logger

logger: Logger = get_logger(__name__)


class PunishmentLogRepository:
    """
    Repository for handling PunishmentLog database operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with a database session."""
        self.session: AsyncSession = session
        logger.debug("Initialized PunishmentLogRepository with session")

    async def get_by_id(self, log_id: int) -> PunishmentLog | None:
        """Get a punishment log by ID."""
        logger.debug(f"Fetching punishment log with ID: {log_id}")
        result: Result[tuple[PunishmentLog]] = await self.session.execute(
            select(PunishmentLog).where(PunishmentLog.id == log_id)
        )
        log = result.scalars().first()
        logger.debug(f"Punishment log with ID {log_id} found: {log is not None}")
        return log

    async def get_by_user_id(self, user_id: int) -> list[PunishmentLog]:
        """Get all punishment logs for a specific user."""
        logger.debug(f"Fetching punishment logs for user ID: {user_id}")
        result: Result[tuple[PunishmentLog]] = await self.session.execute(
            select(PunishmentLog).where(PunishmentLog.user_id == user_id)
        )
        logs = list(result.scalars().all())
        logger.debug(f"Found {len(logs)} punishment logs for user ID: {user_id}")
        return logs

    async def get_by_staff_id(self, staff_id: int) -> list[PunishmentLog]:
        """Get all punishment logs issued by a specific staff."""
        logger.debug(f"Fetching punishment logs by staff ID: {staff_id}")
        result: Result[tuple[PunishmentLog]] = await self.session.execute(
            select(PunishmentLog).where(PunishmentLog.staff_id == staff_id)
        )
        logs = list(result.scalars().all())
        logger.debug(f"Found {len(logs)} punishment logs by staff ID: {staff_id}")
        return logs

    async def get_by_punishment_type(self, punishment_type: str) -> list[PunishmentLog]:
        """Get all punishment logs of a specific type."""
        logger.debug(f"Fetching punishment logs of type: {punishment_type}")
        result: Result[tuple[PunishmentLog]] = await self.session.execute(
            select(PunishmentLog).where(PunishmentLog.punishment_type == punishment_type)
        )
        logs = list(result.scalars().all())
        logger.debug(f"Found {len(logs)} punishment logs of type: {punishment_type}")
        return logs

    async def create(self, log_schema: PunishmentLogSchema) -> PunishmentLog:
        """Create a new punishment log entry."""
        logger.debug(
            f"Creating new punishment log for user ID: {log_schema.user_id}, type: {log_schema.punishment_type}"
        )
        # Convert schema to model
        punishment_log = PunishmentLog(
            id=log_schema.id,
            user_id=log_schema.user_id,
            punishment_type=log_schema.punishment_type,
            reason=log_schema.reason,
            staff_id=log_schema.staff_id,
            duration=log_schema.duration,
            created_at=log_schema.created_at,
            expires_at=log_schema.expires_at,
            source=log_schema.source,
        )

        self.session.add(punishment_log)
        await self.session.flush()
        logger.debug(f"Created punishment log with details: {vars(punishment_log)}")
        return punishment_log

    async def update(self, log_id: int, log_schema: PunishmentLogSchema) -> PunishmentLog | None:
        """Update an existing punishment log entry."""
        logger.debug(f"Attempting to update punishment log ID: {log_id}")
        punishment_log: PunishmentLog | None = await self.get_by_id(log_id)
        if not punishment_log:
            logger.debug(f"Punishment log ID {log_id} not found for update")
            return None

        # Update fields
        punishment_log.user_id = log_schema.user_id
        punishment_log.punishment_type = log_schema.punishment_type
        punishment_log.reason = log_schema.reason
        punishment_log.staff_id = log_schema.staff_id
        punishment_log.duration = log_schema.duration
        punishment_log.created_at = log_schema.created_at
        punishment_log.expires_at = log_schema.expires_at
        punishment_log.source = log_schema.source

        await self.session.flush()
        logger.debug(f"Updated punishment log with details: {vars(punishment_log)}")
        return punishment_log

    async def delete(self, log_id: int) -> bool:
        """Delete a punishment log entry by ID."""
        logger.debug(f"Attempting to delete punishment log ID: {log_id}")
        punishment_log: PunishmentLog | None = await self.get_by_id(log_id)
        if not punishment_log:
            logger.debug(f"Punishment log ID {log_id} not found for deletion")
            return False

        await self.session.delete(punishment_log)
        await self.session.flush()
        return True
