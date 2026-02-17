from fastapi import HTTPException, status

from src.exceptions import ObjectNotFoundException
from src.schemas.booking import BookingAddSchema
from src.validators.booking import BookingValidator


class BookingService:
    @staticmethod
    async def add_booking(booking, db, current_user):
        if booking.date_from >= booking.date_to:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="date_from должен быть раньше date_to",
            )

        if await BookingValidator.has_overlapping_booking(booking, db):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Этот номер уже забронирован на выбранные даты.",
            )

        try:
            room_data = await db.rooms.get_one_or_none(id=booking.room_id)
            if room_data is None:
                raise ObjectNotFoundException
        except ObjectNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Комната не найдена"
            )

        new_booking = BookingAddSchema(
            user_id=current_user.id, **booking.model_dump(), price=room_data.price
        )

        created_booking = await db.booking.add(new_booking)
        await db.commit()

        return created_booking
