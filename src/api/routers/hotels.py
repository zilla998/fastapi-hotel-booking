from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from src.api.dependencies import DBDep, PaginationDep, PaginationParams
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


@router.get(
    "/{hotel_id}",
    summary="Получение отеля по id или названию",
    response_model=HotelsReadSchema,
)
async def get_hotel(hotel_id: int, session: SessionDep):
    try:
        hotel_model = await HotelsRepository(session).get_one_or_none(id=hotel_id)
        if hotel_model is None:
            raise ObjectNotFoundException()
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель с таким id не существует",
        )

    return hotel_model


@router.post(
    "/add_hotel", summary="Добавление отеля", dependencies=[Depends(is_admin_required)]
)
async def add_hotel(hotel: HotelsSchema, session: SessionDep):
    try:
        new_hotel = await HotelsRepository(session).add(hotel)
    except ObjectIsAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Отель с таким названием уже существует",
        )
    await session.commit()

    return new_hotel


@router.patch(
    "/{hotel_id}", summary="Изменение отеля", dependencies=[Depends(is_admin_required)]
)
async def change_hotel(
    hotel_id: int, new_hotel: ChangeHotelSchema, session: SessionDep
):
    try:
        old_hotel_model = HotelsRepository(session).get_one_or_none(id=hotel_id)
        if old_hotel_model is None:
            raise ObjectNotFoundException()
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель с таким id не существует",
        )

    old_hotel_model = new_hotel

    await session.commit()

    return new_hotel


@router.delete(
    "/{hotel_id}", summary="Удаление отеля", dependencies=[Depends(is_admin_required)]
)
async def delete_hotel(hotel_id: int, session: SessionDep):
    try:
        hotel_model = HotelsRepository(session).get_one_or_none(id=hotel_id)
        if hotel_model is None:
            raise ObjectNotFoundException
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель с таким id не существует",
        )

    await session.delete(hotel_model)
    await session.commit()
