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

    async def get_by_id(self, user_id: int) -> User | None:
        """Get a user by ID."""
        result: Result[tuple[User]] = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()

    async def create(self, user_schema: UserSchema) -> User:
        """Create a new user."""
        # Convert schema to model
        user = User(
            id=user_schema.id,
            locale=user_schema.locale,
            minecraft_username=user_schema.minecraftUsername,
            minecraft_uuid=user_schema.minecraftUUID,
        )

        self.session.add(user)
        await self.session.flush()
        logger.info(f"Created user with ID: {user.id}")
        return user

    async def update(self, user_id: int, user_schema: UserSchema) -> User | None:
        """Update an existing user."""
        user: User | None = await self.get_by_id(user_id)
        if not user:
            return None

        # Update fields
        user.locale = user_schema.locale
        user.minecraft_username = user_schema.minecraftUsername
        user.minecraft_uuid = user_schema.minecraftUUID

        await self.session.flush()
        logger.info(f"Updated user with ID: {user_id}")
        return user

    async def delete(self, user_id: int) -> bool:
        """Delete a user by ID."""
        user: User | None = await self.get_by_id(user_id)
        if not user:
            return False

        await self.session.delete(user)
        await self.session.flush()
        logger.info(f"Deleted user with ID: {user_id}")
        return True
