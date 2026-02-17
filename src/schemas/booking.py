from datetime import date

from pydantic import BaseModel, Field


class BookingSchema(BaseModel):
    id: int
    user_id: int
    room_id: int
    date_from: date
    date_to: date
    price: float


class BookingsReservationSchema(BaseModel):
    room_id: int = Field(gt=0)
    date_from: date = Field(description="Дата заезда")
    date_to: date = Field(description="Дата выезда")


class BookingAddSchema(BaseModel):
    user_id: int
    room_id: int
    date_from: date
    date_to: date
    price: float
