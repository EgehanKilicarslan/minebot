from logging import Logger

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import TemporaryAction
from database.schemas import TemporaryActionSchema
from debug import get_logger

logger: Logger = get_logger(__name__)


class TemporaryActionRepository:
    """
    Repository for handling TemporaryAction database operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with a database session."""
        self.session: AsyncSession = session

    async def get_by_id(self, action_id: int) -> TemporaryAction | None:
        """Get a temporary action by ID."""
        result: Result[tuple[TemporaryAction]] = await self.session.execute(
            select(TemporaryAction).where(TemporaryAction.id == action_id)
        )
        return result.scalars().first()

    async def get_by_user_id(self, user_id: int) -> list[TemporaryAction]:
        """Get all temporary actions for a specific user."""
        result: Result[tuple[TemporaryAction]] = await self.session.execute(
            select(TemporaryAction).where(TemporaryAction.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_by_punishment_type(self, punishment_type: str) -> list[TemporaryAction]:
        """Get all temporary actions of a specific type."""
        result: Result[tuple[TemporaryAction]] = await self.session.execute(
            select(TemporaryAction).where(TemporaryAction.punishment_type == punishment_type)
        )
        return list(result.scalars().all())

    async def create(self, action_schema: TemporaryActionSchema) -> TemporaryAction:
        """Create a new temporary action."""
        # Convert schema to model
        temporary_action = TemporaryAction(
            id=action_schema.id,
            user_id=action_schema.user_id,
            punishment_type=action_schema.punishment_type,
            expires_at=action_schema.expires_at,
            refresh_at=action_schema.refresh_at,
        )

        self.session.add(temporary_action)
        await self.session.flush()
        logger.info(f"Created temporary action with ID: {temporary_action.id}")
        return temporary_action

    async def update(
        self, action_id: int, action_schema: TemporaryActionSchema
    ) -> TemporaryAction | None:
        """Update an existing temporary action."""
        temporary_action: TemporaryAction | None = await self.get_by_id(action_id)
        if not temporary_action:
            return None

        # Update fields
        temporary_action.user_id = action_schema.user_id
        temporary_action.punishment_type = action_schema.punishment_type
        temporary_action.expires_at = action_schema.expires_at
        temporary_action.refresh_at = action_schema.refresh_at

        await self.session.flush()
        logger.info(f"Updated temporary action with ID: {action_id}")
        return temporary_action

    async def delete(self, action_id: int) -> bool:
        """Delete a temporary action by ID."""
        temporary_action: TemporaryAction | None = await self.get_by_id(action_id)
        if not temporary_action:
            return False

        await self.session.delete(temporary_action)
        await self.session.flush()
        logger.info(f"Deleted temporary action with ID: {action_id}")
        return True
