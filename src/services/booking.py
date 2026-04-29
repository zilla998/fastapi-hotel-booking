from src.exceptions import (
    ObjectIsAlreadyExistsException,
    ObjectNotAllowedException,
    ObjectNotFoundException,
)
from src.kafka.producer import booking_created_publisher, booking_delete_publisher
from src.validators.booking import BookingValidator


class BookingService:
    def __init__(self, session):
        self.session = session

    async def get_user_bookings(self, user_id: int, limit: int, offset: int):
        return await self.session.booking.get_user_bookings(
            user_id=user_id, limit=limit, offset=offset
        )

    async def delete_booking(self, booking_id: int, user_id: int):
        booking = await self.session.booking.get_one_or_none(id=booking_id)
        if booking is None:
            raise ObjectNotFoundException
        if booking.user_id != user_id:
            raise ObjectNotAllowedException

        await self.session.booking.delete(id=booking_id)
        await self.session.commit()

        await booking_delete_publisher.publish(
            {
                "booking_id": booking_id,
                "message": "Бронь успешно отменена",
            },
        )

    async def add_booking(self, booking, current_user):
        if await BookingValidator.has_overlapping_booking(booking, self.session):
            raise ObjectIsAlreadyExistsException

        room_data = await self.session.rooms.get_one_or_none(id=booking.room_id)
        if room_data is None:
            raise ObjectNotFoundException

        new_booking = {
            "user_id": current_user.id,
            **booking.model_dump(),
            "price": room_data.price,
        }

        created_booking = await self.session.booking.add(new_booking)
        await self.session.commit()

        await booking_created_publisher.publish(
            {
                "booking_id": created_booking.id,
                "user_id": current_user.id,
                "room_id": booking.room_id,
                "message": "Номер успешно забронирован",
            },
        )

        return created_booking
