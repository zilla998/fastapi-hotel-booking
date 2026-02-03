from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class RoomsOrm(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None]
    price: Mapped[float]
    quantity: Mapped[int]

    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))

    facilities: Mapped[list["FacilitiesOrm"]] = relationship(
        secondary="room_facilities",
        back_populates="rooms",
    )
