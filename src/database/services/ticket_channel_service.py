from logging import Logger

from database import get_db_session
from database.models import TicketChannel
from database.repositories import TicketChannelRepository
from database.schemas import TicketChannelSchema
from debug import get_logger

logger: Logger = get_logger(__name__)


class TicketChannelService:
    """
    Service for ticket channel-related business logic and operations.
    """

    @staticmethod
    async def get_ticket_channel(channel_id: int) -> TicketChannelSchema | None:
        """
        Get a ticket channel by ID.

        Args:
            channel_id: The Discord channel ID

        Returns:
            TicketChannelSchema or None if the ticket channel doesn't exist
        """
        async with get_db_session() as session:
            repository = TicketChannelRepository(session)
            ticket_channel: TicketChannel | None = await repository.get_by_id(channel_id)
            if ticket_channel:
                return TicketChannelSchema.model_validate(ticket_channel)
            return None

    @staticmethod
    async def get_ticket_channels_by_owner(owner_id: int) -> list[TicketChannelSchema]:
        """
        Get all ticket channels owned by a specific user.

        Args:
            owner_id: The Discord user ID of the owner

        Returns:
            List of TicketChannelSchema objects
        """
        async with get_db_session() as session:
            repository = TicketChannelRepository(session)
            ticket_channels: list[TicketChannel] = await repository.get_by_owner_id(owner_id)
            return [TicketChannelSchema.model_validate(channel) for channel in ticket_channels]

    @staticmethod
    async def get_ticket_channels_by_category(category_id: int) -> list[TicketChannelSchema]:
        """
        Get all ticket channels in a specific category.

        Args:
            category_id: The Discord category ID

        Returns:
            List of TicketChannelSchema objects
        """
        async with get_db_session() as session:
            repository = TicketChannelRepository(session)
            ticket_channels: list[TicketChannel] = await repository.get_by_category_id(category_id)
            return [TicketChannelSchema.model_validate(channel) for channel in ticket_channels]

    @staticmethod
    async def create_or_update_ticket_channel(
        channel_data: TicketChannelSchema,
    ) -> TicketChannelSchema:
        """
        Create a new ticket channel or update if it already exists.

        Args:
            channel_data: The ticket channel data to create or update

        Returns:
            The created/updated ticket channel schema
        """
        async with get_db_session() as session:
            repository = TicketChannelRepository(session)
            existing_channel: TicketChannel | None = await repository.get_by_id(channel_data.id)

            if existing_channel:
                updated_channel: TicketChannel | None = await repository.update(
                    channel_data.id, channel_data
                )
                return TicketChannelSchema.model_validate(updated_channel)
            else:
                new_channel: TicketChannel = await repository.create(channel_data)
                return TicketChannelSchema.model_validate(new_channel)

    @staticmethod
    async def delete_ticket_channel(channel_id: int) -> bool:
        """
        Delete a ticket channel by ID.

        Args:
            channel_id: The Discord channel ID

        Returns:
            True if the ticket channel was deleted, False otherwise
        """
        async with get_db_session() as session:
            repository = TicketChannelRepository(session)
            return await repository.delete(channel_id)
