from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class TicketChannel(Base):
    __tablename__: str = "ticket_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(Integer, nullable=False)
    category_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
