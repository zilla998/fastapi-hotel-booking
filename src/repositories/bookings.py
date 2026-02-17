from src.models.bookings import BookingOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingDataMapper


class BookingsRepository(BaseRepository):
    model = BookingOrm
    mapper = BookingDataMapper
