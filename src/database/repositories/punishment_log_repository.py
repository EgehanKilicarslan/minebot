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

    async def get_by_id(self, log_id: int) -> PunishmentLog | None:
        """Get a punishment log by ID."""
        result: Result[tuple[PunishmentLog]] = await self.session.execute(
            select(PunishmentLog).where(PunishmentLog.id == log_id)
        )
        return result.scalars().first()

    async def get_by_user_id(self, user_id: int) -> list[PunishmentLog]:
        """Get all punishment logs for a specific user."""
        result: Result[tuple[PunishmentLog]] = await self.session.execute(
            select(PunishmentLog).where(PunishmentLog.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_by_moderator_id(self, moderator_id: int) -> list[PunishmentLog]:
        """Get all punishment logs issued by a specific moderator."""
        result: Result[tuple[PunishmentLog]] = await self.session.execute(
            select(PunishmentLog).where(PunishmentLog.moderator_id == moderator_id)
        )
        return list(result.scalars().all())

    async def get_by_punishment_type(self, punishment_type: str) -> list[PunishmentLog]:
        """Get all punishment logs of a specific type."""
        result: Result[tuple[PunishmentLog]] = await self.session.execute(
            select(PunishmentLog).where(PunishmentLog.punishment_type == punishment_type)
        )
        return list(result.scalars().all())

    async def create(self, log_schema: PunishmentLogSchema) -> PunishmentLog:
        """Create a new punishment log entry."""
        # Convert schema to model
        punishment_log = PunishmentLog(
            id=log_schema.id,
            user_id=log_schema.user_id,
            punishment_type=log_schema.punishment_type,
            reason=log_schema.reason,
            moderator_id=log_schema.moderator_id,
            duration=log_schema.duration,
            created_at=log_schema.created_at,
            expires_at=log_schema.expires_at,
            source=log_schema.source,
        )

        self.session.add(punishment_log)
        await self.session.flush()
        logger.info(f"Created punishment log with ID: {punishment_log.id}")
        return punishment_log

    async def update(self, log_id: int, log_schema: PunishmentLogSchema) -> PunishmentLog | None:
        """Update an existing punishment log entry."""
        punishment_log: PunishmentLog | None = await self.get_by_id(log_id)
        if not punishment_log:
            return None

        # Update fields
        punishment_log.user_id = log_schema.user_id
        punishment_log.punishment_type = log_schema.punishment_type
        punishment_log.reason = log_schema.reason
        punishment_log.moderator_id = log_schema.moderator_id
        punishment_log.duration = log_schema.duration
        punishment_log.created_at = log_schema.created_at
        punishment_log.expires_at = log_schema.expires_at
        punishment_log.source = log_schema.source

        await self.session.flush()
        logger.info(f"Updated punishment log with ID: {log_id}")
        return punishment_log

    async def delete(self, log_id: int) -> bool:
        """Delete a punishment log entry by ID."""
        punishment_log: PunishmentLog | None = await self.get_by_id(log_id)
        if not punishment_log:
            return False

        await self.session.delete(punishment_log)
        await self.session.flush()
        logger.info(f"Deleted punishment log with ID: {log_id}")
        return True
