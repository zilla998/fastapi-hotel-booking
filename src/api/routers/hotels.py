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
    except ObjectNotFoundException as err:
        raise HTTPException(
            status_code=404, detail=f"Отеля с id: {hotel_id} не существует"
        ) from err


@router.post(
    "/add_hotel", summary="Добавление отеля", dependencies=[Depends(is_admin_required)]
)
async def add_hotel(
    hotel: HotelsSchema,
    service: HotelsServiceDep,
):
    try:
        return await service.add(hotel)
    except ObjectIsAlreadyExistsException as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Отель с таким названием уже существует",
        ) from err


@router.patch(
    "/{hotel_id}", summary="Изменение отеля", dependencies=[Depends(is_admin_required)]
)
async def change_hotel(
    hotel_id: int,
    new_hotel: ChangeHotelSchema,
    service: HotelsServiceDep,
):
    try:
        return await service.update(hotel_id, new_hotel)
    except ObjectNotFoundException as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель с таким id не существует",
        ) from err


@router.delete(
    "/{hotel_id}", summary="Удаление отеля", dependencies=[Depends(is_admin_required)]
)
async def delete_hotel(
    hotel_id: int,
    service: HotelsServiceDep,
):
    try:
        await service.delete(hotel_id)
    except ObjectNotFoundException as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель с таким id не существует",
        ) from err
