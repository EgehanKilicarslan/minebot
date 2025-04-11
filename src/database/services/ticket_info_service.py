from logging import Logger

from database import get_db_session
from database.models import TicketInfo
from database.repositories import TicketInfoRepository
from database.schemas import TicketInfoSchema
from debug import get_logger

logger: Logger = get_logger(__name__)


class TicketInfoService:
    """
    Service for ticket information related business logic and operations.
    """

    @staticmethod
    async def get_ticket_by_id(ticket_id: int) -> TicketInfoSchema | None:
        """
        Get a ticket by ID.

        Args:
            ticket_id: The ticket ID

        Returns:
            TicketInfoSchema or None if the ticket doesn't exist
        """
        async with get_db_session() as session:
            repository = TicketInfoRepository(session)
            ticket_info: TicketInfo | None = await repository.get_by_id(ticket_id)
            if ticket_info:
                return TicketInfoSchema.model_validate(ticket_info)
            return None

    @staticmethod
    async def get_ticket_by_channel_id(channel_id: int) -> TicketInfoSchema | None:
        """
        Get a ticket by channel ID.

        Args:
            channel_id: The Discord channel ID

        Returns:
            TicketInfoSchema or None if the ticket doesn't exist
        """
        async with get_db_session() as session:
            repository = TicketInfoRepository(session)
            ticket_info: TicketInfo | None = await repository.get_by_channel_id(channel_id)
            if ticket_info:
                return TicketInfoSchema.model_validate(ticket_info)
            return None

    @staticmethod
    async def get_ticket_by_message_id(message_id: int) -> TicketInfoSchema | None:
        """
        Get a ticket by message ID.

        Args:
            message_id: The Discord message ID

        Returns:
            TicketInfoSchema or None if the ticket doesn't exist
        """
        async with get_db_session() as session:
            repository = TicketInfoRepository(session)
            ticket_info: TicketInfo | None = await repository.get_by_message_id(message_id)
            if ticket_info:
                return TicketInfoSchema.model_validate(ticket_info)
            return None

    @staticmethod
    async def create_or_update_ticket(ticket_data: TicketInfoSchema) -> TicketInfoSchema:
        """
        Create a new ticket or update if it already exists.

        Args:
            ticket_data: The ticket data to create or update

        Returns:
            The created/updated ticket schema
        """
        async with get_db_session() as session:
            repository = TicketInfoRepository(session)
            existing_ticket: TicketInfo | None = await repository.get_by_id(ticket_data.id)

            if existing_ticket:
                updated_ticket: TicketInfo | None = await repository.update(
                    ticket_data.id, ticket_data
                )
                return TicketInfoSchema.model_validate(updated_ticket)
            else:
                new_ticket: TicketInfo = await repository.create(ticket_data)
                return TicketInfoSchema.model_validate(new_ticket)

    @staticmethod
    async def delete_ticket(ticket_id: int) -> bool:
        """
        Delete a ticket by ID.

        Args:
            ticket_id: The ticket ID

        Returns:
            True if the ticket was deleted, False otherwise
        """
        async with get_db_session() as session:
            repository = TicketInfoRepository(session)
            return await repository.delete(ticket_id)
