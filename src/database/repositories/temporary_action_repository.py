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
        logger.debug("Initialized TemporaryActionRepository with session")

    async def get_by_id(self, action_id: int) -> TemporaryAction | None:
        """Get a temporary action by ID."""
        logger.debug(f"Fetching temporary action with ID: {action_id}")
        result: Result[tuple[TemporaryAction]] = await self.session.execute(
            select(TemporaryAction).where(TemporaryAction.id == action_id)
        )
        action = result.scalars().first()
        logger.debug(f"Temporary action with ID {action_id} found: {action is not None}")
        return action

    async def get_by_user_id(self, user_id: int) -> list[TemporaryAction]:
        """Get all temporary actions for a specific user."""
        logger.debug(f"Fetching temporary actions for user ID: {user_id}")
        result: Result[tuple[TemporaryAction]] = await self.session.execute(
            select(TemporaryAction).where(TemporaryAction.user_id == user_id)
        )
        actions = list(result.scalars().all())
        logger.debug(f"Found {len(actions)} temporary actions for user ID: {user_id}")
        return actions

    async def get_by_punishment_type(self, punishment_type: str) -> list[TemporaryAction]:
        """Get all temporary actions of a specific type."""
        logger.debug(f"Fetching temporary actions of type: {punishment_type}")
        result: Result[tuple[TemporaryAction]] = await self.session.execute(
            select(TemporaryAction).where(TemporaryAction.punishment_type == punishment_type)
        )
        actions = list(result.scalars().all())
        logger.debug(f"Found {len(actions)} temporary actions of type: {punishment_type}")
        return actions

    async def create(self, action_schema: TemporaryActionSchema) -> TemporaryAction:
        """Create a new temporary action."""
        logger.debug(
            f"Creating new temporary action for user ID: {action_schema.user_id}, type: {action_schema.punishment_type}"
        )
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
        logger.debug(f"Created temporary action with details: {vars(temporary_action)}")
        return temporary_action

    async def update(
        self, action_id: int, action_schema: TemporaryActionSchema
    ) -> TemporaryAction | None:
        """Update an existing temporary action."""
        logger.debug(f"Attempting to update temporary action ID: {action_id}")
        temporary_action: TemporaryAction | None = await self.get_by_id(action_id)
        if not temporary_action:
            logger.debug(f"Temporary action ID {action_id} not found for update")
            return None

        # Update fields
        temporary_action.user_id = action_schema.user_id
        temporary_action.punishment_type = action_schema.punishment_type
        temporary_action.expires_at = action_schema.expires_at
        temporary_action.refresh_at = action_schema.refresh_at

        await self.session.flush()
        logger.debug(f"Updated temporary action with details: {vars(temporary_action)}")
        return temporary_action

    async def delete(self, action_id: int) -> bool:
        """Delete a temporary action by ID."""
        logger.debug(f"Attempting to delete temporary action ID: {action_id}")
        temporary_action: TemporaryAction | None = await self.get_by_id(action_id)
        if not temporary_action:
            logger.debug(f"Temporary action ID {action_id} not found for deletion")
            return False

        await self.session.delete(temporary_action)
        await self.session.flush()
        return True
