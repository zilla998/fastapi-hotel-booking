from src.models.bookings import BookingOrm
from src.repositories.base import BaseRepository


class BookingsRepository(BaseRepository):
    model = BookingOrm
