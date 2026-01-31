from src.models.hotels import HotelsOrm
from src.repositories.base import BaseRepository


class HotelsRepository(BaseRepository):
    model = HotelsOrm
