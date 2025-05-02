from logging import Logger

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.schemas import UserSchema
from debug import get_logger

logger: Logger = get_logger(__name__)


class UserRepository:
    """
    Repository for handling User database operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with a database session."""
        self.session: AsyncSession = session
        logger.debug("Initialized UserRepository with session")

    async def get_by_id(self, user_id: int) -> User | None:
        """Get a user by ID."""
        logger.debug(f"Fetching user with ID: {user_id}")
        result: Result[tuple[User]] = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalars().first()
        logger.debug(f"User with ID {user_id} found: {user is not None}")
        return user

    async def create(self, user_schema: UserSchema) -> User:
        """Create a new user."""
        logger.debug(
            f"Creating new user with ID: {user_schema.id}, minecraft username: {user_schema.minecraft_username}"
        )
        # Convert schema to model
        user = User(
            id=user_schema.id,
            locale=user_schema.locale,
            minecraft_username=user_schema.minecraft_username,
            minecraft_uuid=user_schema.minecraft_uuid,
            reward_inventory=user_schema.reward_inventory,
        )

        self.session.add(user)
        await self.session.flush()
        logger.debug(f"Created user with details: {vars(user)}")
        return user

    async def update(self, user_id: int, user_schema: UserSchema) -> User | None:
        """Update an existing user."""
        logger.debug(f"Attempting to update user with ID: {user_id}")
        user: User | None = await self.get_by_id(user_id)
        if not user:
            logger.debug(f"User with ID {user_id} not found for update")
            return None

        # Update fields
        user.locale = user_schema.locale
        user.minecraft_username = user_schema.minecraft_username
        user.minecraft_uuid = user_schema.minecraft_uuid
        user.reward_inventory = user_schema.reward_inventory

        await self.session.flush()
        logger.debug(f"Updated user with details: {vars(user)}")
        return user

    async def delete(self, user_id: int) -> bool:
        """Delete a user by ID."""
        logger.debug(f"Attempting to delete user with ID: {user_id}")
        user: User | None = await self.get_by_id(user_id)
        if not user:
            logger.debug(f"User with ID {user_id} not found for deletion")
            return False

        await self.session.delete(user)
        await self.session.flush()
        logger.debug(f"Successfully deleted user with ID: {user_id}")
        return True
