from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select

from api.routers.users import is_admin_required
from exeptions import ObjectIsAlreadyExistsException, ObjectNotFoundException
from repositories.hotels import HotelsRepository
from src.database import SessionDep
from src.exceptions.hotels import HotelNotFound
from src.models.hotels import HotelsOrm
from src.schemas.hotels import HotelsReadSchema, HotelsSchema

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get(
    "",
    summary="Получение списка отелей",
    response_model=list[HotelsReadSchema],
    status_code=200,
)
async def get_hotels(session: SessionDep):
    hotels_model = await HotelsRepository(session).get_all()
    return hotels_model


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
            status_code=404, detail=f"Отель с id: {hotel_id} не существует"
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
            status_code=409, detail="Отель с таким названием уже существует"
        )
    await session.commit()

    return new_hotel
