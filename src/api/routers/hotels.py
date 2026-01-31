from exeptions import ObjectIsAlreadyExistsException
from fastapi import APIRouter, HTTPException
from repositories.hotels import HotelsRepository
from sqlalchemy import select
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
    result = await session.execute(select(HotelsOrm))
    hotels = result.scalars().all()

    return hotels


@router.get(
    "/{id}",
    summary="Получение отеля по id или названию",
    response_model=HotelsReadSchema,
)
async def get_hotel(id: int | None, title: str | None, session: SessionDep):
    query = select(HotelsOrm).where(HotelsOrm.id == id or HotelsOrm.title == title)
    result = await session.execute(query)
    hotel = result.scalar_one_or_none()

    if hotel is None:
        raise HotelNotFound(id, title)

    return hotel


@router.post("/add_hotel", summary="Добавление отеля")
async def add_hotel(hotel: HotelsSchema, session: SessionDep):
    try:
        new_hotel = await HotelsRepository(session).add(hotel)
    except ObjectIsAlreadyExistsException:
        raise HTTPException(
            status_code=409, detail="Отель с таким названием уже существует"
        )
    await session.commit()

    return new_hotel
