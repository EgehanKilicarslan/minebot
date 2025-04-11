from logging import Logger

from database import get_db_session
from database.models import TemporaryAction
from database.repositories import TemporaryActionRepository
from database.schemas import TemporaryActionSchema
from debug import get_logger

logger: Logger = get_logger(__name__)


class TemporaryActionService:
    """
    Service for temporary action-related business logic and operations.
    """

    @staticmethod
    async def get_temporary_action(action_id: int) -> TemporaryActionSchema | None:
        """
        Get a temporary action by ID.

        Args:
            action_id: The temporary action ID

        Returns:
            TemporaryActionSchema or None if the action doesn't exist
        """
        async with get_db_session() as session:
            repository = TemporaryActionRepository(session)
            action: TemporaryAction | None = await repository.get_by_id(action_id)
            if action:
                return TemporaryActionSchema.model_validate(action)
            return None

    @staticmethod
    async def get_temporary_actions_by_user(user_id: int) -> list[TemporaryActionSchema]:
        """
        Get all temporary actions for a specific user.

        Args:
            user_id: The Discord user ID

        Returns:
            List of TemporaryActionSchema objects
        """
        async with get_db_session() as session:
            repository = TemporaryActionRepository(session)
            actions: list[TemporaryAction] = await repository.get_by_user_id(user_id)
            return [TemporaryActionSchema.model_validate(action) for action in actions]

    @staticmethod
    async def get_temporary_actions_by_type(punishment_type: str) -> list[TemporaryActionSchema]:
        """
        Get all temporary actions of a specific type.

        Args:
            punishment_type: The type of punishment (e.g., "ban", "mute")

        Returns:
            List of TemporaryActionSchema objects
        """
        async with get_db_session() as session:
            repository = TemporaryActionRepository(session)
            actions: list[TemporaryAction] = await repository.get_by_punishment_type(
                punishment_type
            )
            return [TemporaryActionSchema.model_validate(action) for action in actions]

    @staticmethod
    async def create_or_update_temporary_action(
        action_data: TemporaryActionSchema,
    ) -> TemporaryActionSchema:
        """
        Create a new temporary action or update if it already exists.

        Args:
            action_data: The temporary action data to create or update

        Returns:
            The created/updated temporary action schema
        """
        async with get_db_session() as session:
            repository = TemporaryActionRepository(session)
            existing_action: TemporaryAction | None = await repository.get_by_id(action_data.id)

            if existing_action:
                updated_action: TemporaryAction | None = await repository.update(
                    action_data.id, action_data
                )
                return TemporaryActionSchema.model_validate(updated_action)
            else:
                new_action: TemporaryAction = await repository.create(action_data)
                return TemporaryActionSchema.model_validate(new_action)

    @staticmethod
    async def delete_temporary_action(action_id: int) -> bool:
        """
        Delete a temporary action by ID.

        Args:
            action_id: The temporary action ID

        Returns:
            True if the action was deleted, False otherwise
        """
        async with get_db_session() as session:
            repository = TemporaryActionRepository(session)
            return await repository.delete(action_id)
