from datetime import date

from pydantic import BaseModel, Field


class BookingsReservationSchema(BaseModel):
    room_id: int = Field(gt=0)
    date_from: date = Field(description="Дата заезда")
    date_to: date = Field(description="Дата выезда")
    price = float
