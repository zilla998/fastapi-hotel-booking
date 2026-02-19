from sqlalchemy import and_

from src.models.bookings import BookingOrm
from src.schemas.booking import BookingCreateSchema


class BookingValidator:
    @staticmethod
    async def has_overlapping_booking(booking: BookingCreateSchema, db) -> bool:
        overlap_condition = and_(
            BookingOrm.room_id == booking.room_id,
            BookingOrm.date_from < booking.date_to,
            BookingOrm.date_to > booking.date_from,
        )
        return await db.booking.exists(overlap_condition)
