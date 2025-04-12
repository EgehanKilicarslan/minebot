from logging import Logger

from database import get_db_session
from database.models import PunishmentLog
from database.repositories import PunishmentLogRepository
from database.schemas import PunishmentLogSchema
from debug import get_logger

logger: Logger = get_logger(__name__)


class PunishmentLogService:
    """
    Service for punishment log-related business logic and operations.
    """

    @staticmethod
    async def get_punishment_log(log_id: int) -> PunishmentLogSchema | None:
        """
        Get a punishment log by ID.

        Args:
            log_id: The punishment log ID

        Returns:
            PunishmentLogSchema or None if the log doesn't exist
        """
        async with get_db_session() as session:
            repository = PunishmentLogRepository(session)
            log: PunishmentLog | None = await repository.get_by_id(log_id)
            if log:
                return PunishmentLogSchema.model_validate(log)
            return None

    @staticmethod
    async def get_punishment_logs_by_user(user_id: int) -> list[PunishmentLogSchema]:
        """
        Get all punishment logs for a specific user.

        Args:
            user_id: The Discord user ID

        Returns:
            List of PunishmentLogSchema objects
        """
        async with get_db_session() as session:
            repository = PunishmentLogRepository(session)
            logs: list[PunishmentLog] = await repository.get_by_user_id(user_id)
            return [PunishmentLogSchema.model_validate(log) for log in logs]

    @staticmethod
    async def get_punishment_logs_by_moderator(moderator_id: int) -> list[PunishmentLogSchema]:
        """
        Get all punishment logs issued by a specific moderator.

        Args:
            moderator_id: The Discord moderator ID

        Returns:
            List of PunishmentLogSchema objects
        """
        async with get_db_session() as session:
            repository = PunishmentLogRepository(session)
            logs: list[PunishmentLog] = await repository.get_by_moderator_id(moderator_id)
            return [PunishmentLogSchema.model_validate(log) for log in logs]

    @staticmethod
    async def get_punishment_logs_by_type(punishment_type: str) -> list[PunishmentLogSchema]:
        """
        Get all punishment logs of a specific type.

        Args:
            punishment_type: The type of punishment (e.g., "ban", "mute")

        Returns:
            List of PunishmentLogSchema objects
        """
        async with get_db_session() as session:
            repository = PunishmentLogRepository(session)
            logs: list[PunishmentLog] = await repository.get_by_punishment_type(punishment_type)
            return [PunishmentLogSchema.model_validate(log) for log in logs]

    @staticmethod
    async def create_or_update_punishment_log(log_data: PunishmentLogSchema) -> PunishmentLogSchema:
        """
        Create a new punishment log or update if it already exists.

        Args:
            log_data: The punishment log data to create or update

        Returns:
            The created/updated punishment log schema
        """
        async with get_db_session() as session:
            repository = PunishmentLogRepository(session)

            # Check if we have an ID and if it exists in the database
            if log_data.id is not None:
                existing_log: PunishmentLog | None = await repository.get_by_id(log_data.id)
                if existing_log:
                    updated_log: PunishmentLog | None = await repository.update(
                        log_data.id, log_data
                    )
                    return PunishmentLogSchema.model_validate(updated_log)

            # If no ID or record doesn't exist, create a new one
            new_log: PunishmentLog = await repository.create(log_data)
            return PunishmentLogSchema.model_validate(new_log)

    @staticmethod
    async def delete_punishment_log(log_id: int) -> bool:
        """
        Delete a punishment log by ID.

        Args:
            log_id: The punishment log ID

        Returns:
            True if the log was deleted, False otherwise
        """
        async with get_db_session() as session:
            repository = PunishmentLogRepository(session)
            return await repository.delete(log_id)
