from logging import Logger

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import TicketInfo
from database.schemas import TicketInfoSchema
from debug import get_logger

logger: Logger = get_logger(__name__)


class TicketInfoRepository:
    """
    Repository for handling TicketInfo database operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with a database session."""
        self.session: AsyncSession = session

    async def get_by_id(self, ticket_id: int) -> TicketInfo | None:
        """Get a ticket by ID."""
        result: Result[tuple[TicketInfo]] = await self.session.execute(
            select(TicketInfo).where(TicketInfo.id == ticket_id)
        )
        return result.scalars().first()

    async def get_by_channel_id(self, channel_id: int) -> TicketInfo | None:
        """Get a ticket by channel ID."""
        result: Result[tuple[TicketInfo]] = await self.session.execute(
            select(TicketInfo).where(TicketInfo.channel_id == channel_id)
        )
        return result.scalars().first()

    async def get_by_message_id(self, message_id: int) -> TicketInfo | None:
        """Get a ticket by message ID."""
        result: Result[tuple[TicketInfo]] = await self.session.execute(
            select(TicketInfo).where(TicketInfo.message_id == message_id)
        )
        return result.scalars().first()

    async def create(self, ticket_schema: TicketInfoSchema) -> TicketInfo:
        """Create a new ticket info entry."""
        # Convert schema to model
        ticket_info = TicketInfo(
            id=ticket_schema.id,
            channel_id=ticket_schema.channel_id,
            message_id=ticket_schema.message_id,
        )

        self.session.add(ticket_info)
        await self.session.flush()
        logger.info(f"Created ticket info with ID: {ticket_info.id}")
        return ticket_info

    async def update(self, ticket_id: int, ticket_schema: TicketInfoSchema) -> TicketInfo | None:
        """Update an existing ticket info entry."""
        ticket_info: TicketInfo | None = await self.get_by_id(ticket_id)
        if not ticket_info:
            return None

        # Update fields
        ticket_info.channel_id = ticket_schema.channel_id
        ticket_info.message_id = ticket_schema.message_id

        await self.session.flush()
        logger.info(f"Updated ticket info with ID: {ticket_id}")
        return ticket_info

    async def delete(self, ticket_id: int) -> bool:
        """Delete a ticket info entry by ID."""
        ticket_info: TicketInfo | None = await self.get_by_id(ticket_id)
        if not ticket_info:
            return False

        await self.session.delete(ticket_info)
        await self.session.flush()
        logger.info(f"Deleted ticket info with ID: {ticket_id}")
        return True
