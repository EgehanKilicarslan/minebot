from datetime import datetime

from sqlalchemy import DATETIME, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class TemporaryAction(Base):
    __tablename__: str = "temporary_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    punishment_type: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DATETIME, nullable=False)
    refresh_at: Mapped[datetime | None] = mapped_column(DATETIME, nullable=True)
