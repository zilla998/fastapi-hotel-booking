from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from src.api.dependencies import (
    HotelsServiceDep,
    PaginationDep,
    is_admin_required,
)
from src.exceptions import ObjectIsAlreadyExistsException, ObjectNotFoundException
from src.schemas.hotels import ChangeHotelSchema, HotelsReadSchema, HotelsSchema

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get(
    "",
    summary="Получение списка отелей",
    response_model=list[HotelsReadSchema],
)
async def get_hotels(pagination: PaginationDep, service: HotelsServiceDep):
    return await service.get_all(pagination)


@router.get(
    "/{hotel_id}",
    summary="Получение отеля по id",
)
async def get_hotel(hotel_id: int, service: HotelsServiceDep):
    try:
        return await service.get_by_id(hotel_id)
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=404, detail=f"Отеля с id: {hotel_id} не существует"
        )


@router.post(
    "/add_hotel", summary="Добавление отеля", dependencies=[Depends(is_admin_required)]
)
async def add_hotel(
    hotel: HotelsSchema,
    service: HotelsServiceDep,
):
    try:
        return await service.add(hotel)
    except ObjectIsAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Отель с таким названием уже существует",
        )


@router.patch(
    "/{hotel_id}", summary="Изменение отеля", dependencies=[Depends(is_admin_required)]
)
async def change_hotel(
    hotel_id: int,
    new_hotel: ChangeHotelSchema,
    service: HotelsServiceDep,
):
    try:
        old_hotel_model = await service.db.hotels.get_one_or_none(id=hotel_id)
        if old_hotel_model is None:
            raise ObjectNotFoundException()
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель с таким id не существует",
        )

    update_hotel = await service.db.hotels.edit(new_hotel, id=hotel_id)
    await service.db.commit()

    keys = await service.redis.keys("hotels:list:*")
    if keys:
        await service.redis.delete(*keys)

    return update_hotel


@router.delete(
    "/{hotel_id}", summary="Удаление отеля", dependencies=[Depends(is_admin_required)]
)
async def delete_hotel(
    hotel_id: int,
    service: HotelsServiceDep,
):
    try:
        hotel_model = await service.db.hotels.get_one_or_none(id=hotel_id)
        if hotel_model is None:
            raise ObjectNotFoundException
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель с таким id не существует",
        )

    await service.db.hotels.delete(id=hotel_id)
    await service.db.commit()

    keys = await service.redis.keys("hotels:list:*")
    if keys:
        await service.redis.delete(*keys)
