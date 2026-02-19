from fastapi import HTTPException, status

from src.exceptions import ObjectNotFoundException
from src.validators.booking import BookingValidator


class BookingService:
    def __init__(self, session):
        self.session = session

    async def add_booking(self, booking, current_user):
        if await BookingValidator.has_overlapping_booking(booking, self.session):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Этот номер уже забронирован на выбранные даты.",
            )

        try:
            room_data = await self.session.rooms.get_one_or_none(id=booking.room_id)
            if room_data is None:
                raise ObjectNotFoundException
        except ObjectNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Комната не найдена"
            )

        new_booking = {
            "user_id": current_user.id,
            **booking.model_dump(),
            "price": room_data.price,
        }

        created_booking = await self.session.booking.add(new_booking)
        await self.session.commit()

        return created_booking
