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
            limit=pagination.per_page, offset=pagination.page
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

        keys = await self.redis.keys("hotels:list:*")
        if keys:
            await self.redis.delete(*keys)

        return result
