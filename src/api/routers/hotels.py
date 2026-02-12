from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from src.api.dependencies import DBDep, PaginationDep
from src.api.routers.users import is_admin_required
from src.database import SessionDep
from src.exceptions import ObjectIsAlreadyExistsException, ObjectNotFoundException
from src.repositories.hotels import HotelsRepository
from src.schemas.hotels import ChangeHotelSchema, HotelsReadSchema, HotelsSchema

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get(
    "",
    summary="Получение списка отелей",
    response_model=list[HotelsReadSchema],
)
async def get_hotels(db: DBDep, pagination: PaginationDep):
    return await db.hotels.get_all(limit=pagination.per_page, offset=pagination.page)


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
async def add_hotel(hotel: HotelsSchema, db: DBDep):
    try:
        await db.hotels.add(hotel)
    except ObjectIsAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Отель с таким названием уже существует",
        )
    await db.commit()

    return hotel


@router.patch(
    "/{hotel_id}", summary="Изменение отеля", dependencies=[Depends(is_admin_required)]
)
async def change_hotel(hotel_id: int, new_hotel: ChangeHotelSchema, db: DBDep):
    try:
        old_hotel_model = await db.hotels.get_one_or_none(id=hotel_id)
        if old_hotel_model is None:
            raise ObjectNotFoundException()
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель с таким id не существует",
        )

    old_hotel_model = new_hotel

    await db.commit()

    return new_hotel


@router.delete(
    "/{hotel_id}", summary="Удаление отеля", dependencies=[Depends(is_admin_required)]
)
async def delete_hotel(hotel_id: int, db: DBDep):
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
