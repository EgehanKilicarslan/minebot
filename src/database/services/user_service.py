from logging import Logger

from database import get_db_session
from database.models import User
from database.repositories import UserRepository
from database.schemas import UserSchema
from debug import get_logger

logger: Logger = get_logger(__name__)


class UserService:
    """
    Service for user-related business logic and operations.
    """

    @staticmethod
    async def get_user(user_id: int) -> UserSchema | None:
        """
        Get a user by ID.

        Args:
            user_id: The Discord user ID

        Returns:
            UserSchema or None if the user doesn't exist
        """
        async with get_db_session() as session:
            repository = UserRepository(session)
            user: User | None = await repository.get_by_id(user_id)
            if user:
                return UserSchema.model_validate(user)
            return None

    @staticmethod
    async def create_or_update_user(user_data: UserSchema) -> UserSchema:
        """
        Create a new user or update if it already exists.

        Args:
            user_data: The user data to create or update

        Returns:
            The created/updated user schema
        """
        async with get_db_session() as session:
            repository = UserRepository(session)
            existing_user: User | None = await repository.get_by_id(user_data.id)

            if existing_user:
                updated_user: User | None = await repository.update(user_data.id, user_data)
                return UserSchema.model_validate(updated_user)
            else:
                new_user: User = await repository.create(user_data)
                return UserSchema.model_validate(new_user)

    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """
        Delete a user by ID.

        Args:
            user_id: The Discord user ID

        Returns:
            True if the user was deleted, False otherwise
        """
        async with get_db_session() as session:
            repository = UserRepository(session)
            return await repository.delete(user_id)
