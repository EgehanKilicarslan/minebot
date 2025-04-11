from datetime import datetime, timezone

from sqlalchemy import DATETIME, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class PunishmentLog(Base):
    __tablename__: str = "punishment_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    punishment_type: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    moderator_id: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME, nullable=False, default=datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime | None] = mapped_column(DATETIME, nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
