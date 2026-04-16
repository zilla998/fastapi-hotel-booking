import json
from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from redis.asyncio import Redis

from src.api.dependencies import DBDep, PaginationDep, is_admin_required
from src.cache import get_redis
from src.exceptions import ObjectIsAlreadyExistsException, ObjectNotFoundException
from src.schemas.hotels import ChangeHotelSchema, HotelsReadSchema, HotelsSchema

router = APIRouter(prefix="/hotels", tags=["Отели"])

RedisDep = Annotated[Redis, Depends(get_redis)]


@router.get(
    "",
    summary="Получение списка отелей",
    response_model=list[HotelsReadSchema],
)
async def get_hotels(
    db: DBDep,
    pagination: PaginationDep,
    redis: RedisDep,
):
    cache_key = f"hotels:list:page={pagination.page}:per_page={pagination.per_page}"
    cached = await redis.get(cache_key)

    if cached:
        return json.loads(cached)

    hotels = await db.hotels.get_all(limit=pagination.per_page, offset=pagination.page)

    hotels_data = [hotel.model_dump() for hotel in hotels]

    await redis.set(cache_key, json.dumps(hotels_data), ex=300)

    return hotels


@router.get("/{hotel_id}", summary="Получение отеля по id")
async def get_hotel(hotel_id: int, db: DBDep):
    try:
        hotel = await db.hotels.get_one_or_none(id=hotel_id)
        if hotel is None:
            raise ObjectNotFoundException
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Отеля с id: {hotel_id} не существует",
        )

    return hotel


@router.post(
    "/add_hotel", summary="Добавление отеля", dependencies=[Depends(is_admin_required)]
)
async def add_hotel(
    hotel: HotelsSchema,
    db: DBDep,
    redis: RedisDep,
):
    try:
        await db.hotels.add(hotel)
    except ObjectIsAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Отель с таким названием уже существует",
        )
    await db.commit()

    keys = await redis.keys("hotels:list:*")
    if keys:
        await redis.delete(*keys)

    return hotel


@router.patch(
    "/{hotel_id}", summary="Изменение отеля", dependencies=[Depends(is_admin_required)]
)
async def change_hotel(
    hotel_id: int,
    new_hotel: ChangeHotelSchema,
    db: DBDep,
    redis: RedisDep,
):
    try:
        old_hotel_model = await db.hotels.get_one_or_none(id=hotel_id)
        if old_hotel_model is None:
            raise ObjectNotFoundException()
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель с таким id не существует",
        )

    update_hotel = await db.hotels.edit(new_hotel, id=hotel_id)
    await db.commit()

    keys = await redis.keys("hotels:list:*")
    if keys:
        await redis.delete(*keys)

    return update_hotel


@router.delete(
    "/{hotel_id}", summary="Удаление отеля", dependencies=[Depends(is_admin_required)]
)
async def delete_hotel(
    hotel_id: int,
    db: DBDep,
    redis: RedisDep,
):
    try:
        hotel_model = await db.hotels.get_one_or_none(id=hotel_id)
        if hotel_model is None:
            raise ObjectNotFoundException
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель с таким id не существует",
        )

    await db.hotels.delete(id=hotel_id)
    await db.commit()

    keys = await redis.keys("hotels:list:*")
    if keys:
        await redis.delete(*keys)
