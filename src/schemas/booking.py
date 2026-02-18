from datetime import date

from pydantic import BaseModel, Field, model_validator


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

    @model_validator(mode="after")
    def check_dates(self) -> "BookingsReservationSchema":
        if self.date_from >= self.date_to:
            raise ValueError("date_from должен быть раньше date_to")
        return self


class BookingAddSchema(BaseModel):
    user_id: int
    room_id: int
    date_from: date
    date_to: date
    price: float
