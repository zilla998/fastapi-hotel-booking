from sqlalchemy import select

from src.models.bookings import BookingOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingDataMapper


class BookingsRepository(BaseRepository):
    model = BookingOrm
    mapper = BookingDataMapper

    async def get_user_bookings(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0,
    ) -> list:
        """Возвращает брони конкретного пользователя, отсортированные по дате заезда."""
        query = (
            select(self.model)
            .filter_by(user_id=user_id)
            .order_by(self.model.date_from.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity_pyd(model)
            for model in result.scalars().all()
        ]
