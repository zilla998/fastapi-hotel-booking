from src.models.hotels import HotelsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import HotelDataMapper


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    mapper = HotelDataMapper
