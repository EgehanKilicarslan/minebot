from logging import Logger

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import TicketChannel
from database.schemas import TicketChannelSchema
from debug import get_logger

logger: Logger = get_logger(__name__)


class TicketChannelRepository:
    """
    Repository for handling TicketChannel database operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with a database session."""
        self.session: AsyncSession = session

    async def get_by_id(self, channel_id: int) -> TicketChannel | None:
        """Get a ticket channel by ID."""
        result: Result[tuple[TicketChannel]] = await self.session.execute(
            select(TicketChannel).where(TicketChannel.id == channel_id)
        )
        return result.scalars().first()

    async def get_by_owner_id(self, owner_id: int) -> list[TicketChannel]:
        """Get all ticket channels for a specific owner."""
        result: Result[tuple[TicketChannel]] = await self.session.execute(
            select(TicketChannel).where(TicketChannel.owner_id == owner_id)
        )
        return list(result.scalars().all())

    async def get_by_category_id(self, category_id: int) -> list[TicketChannel]:
        """Get all ticket channels in a specific category."""
        result: Result[tuple[TicketChannel]] = await self.session.execute(
            select(TicketChannel).where(TicketChannel.category_id == category_id)
        )
        return list(result.scalars().all())

    async def create(self, channel_schema: TicketChannelSchema) -> TicketChannel:
        """Create a new ticket channel."""
        # Convert schema to model
        ticket_channel = TicketChannel(
            id=channel_schema.id,
            owner_id=channel_schema.owner_id,
            category_id=channel_schema.category_id,
        )

        self.session.add(ticket_channel)
        await self.session.flush()
        logger.info(f"Created ticket channel with ID: {ticket_channel.id}")
        return ticket_channel

    async def update(
        self, channel_id: int, channel_schema: TicketChannelSchema
    ) -> TicketChannel | None:
        """Update an existing ticket channel."""
        ticket_channel: TicketChannel | None = await self.get_by_id(channel_id)
        if not ticket_channel:
            return None

        # Update fields
        ticket_channel.owner_id = channel_schema.owner_id
        ticket_channel.category_id = channel_schema.category_id

        await self.session.flush()
        logger.info(f"Updated ticket channel with ID: {channel_id}")
        return ticket_channel

    async def delete(self, channel_id: int) -> bool:
        """Delete a ticket channel by ID."""
        ticket_channel: TicketChannel | None = await self.get_by_id(channel_id)
        if not ticket_channel:
            return False

        await self.session.delete(ticket_channel)
        await self.session.flush()
        logger.info(f"Deleted ticket channel with ID: {channel_id}")
        return True
