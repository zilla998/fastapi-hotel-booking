import json

from src.exceptions import ObjectNotFoundException


class HotelsService:
    def __init__(self, db, redis):
        self.db = db
        self.redis = redis

    async def get_all(self, pagination):
        cache_key = f"hotels:list:page={pagination.page}:per_page={pagination.per_page}"

        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        hotels = await self.db.hotels.get_all(
            limit=pagination.per_page, offset=pagination.offset
        )
        await self.redis.set(
            cache_key, json.dumps([h.model_dump() for h in hotels]), ex=300
        )
        return hotels

    async def get_by_id(self, hotel_id: int):
        hotel = await self.db.hotels.get_one_or_none(id=hotel_id)
        if hotel is None:
            raise ObjectNotFoundException
        return hotel

    async def add(self, hotel):
        result = await self.db.hotels.add(hotel)
        await self.db.commit()

        await self._invalidate_cache()
        return result

    async def update(self, hotel_id: int, new_hotel):
        updated = await self.db.hotels.edit(new_hotel, id=hotel_id)
        await self.db.commit()
        await self._invalidate_cache()
        return updated

    async def delete(self, hotel_id: int):
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()
        await self._invalidate_cache()

    async def _invalidate_cache(self):
        keys = await self.redis.keys("hotels:list:*")
        if keys:
            await self.redis.delete(*keys)
