from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.rooms import RoomsOrm


class FacilitiesOrm(Base):
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))

    rooms: Mapped[list["RoomsOrm"]] = relationship(
        secondary="room_facilities",
        back_populates="facilities",
    )


class RoomsFacilitiesOrm(Base):
    __tablename__ = "room_facilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    facilities_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))
