from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from api.routers.users import is_admin_required, require_access_cookie
from src.database import SessionDep
from src.exceptions import ObjectIsAlreadyExistsException, ObjectNotFoundException
from src.repositories.rooms import RoomsRepository
from src.schemas.rooms import AddRoomSchema, ChangeRoomSchema, RoomSchema

router = APIRouter(prefix="/rooms", tags=["Отельные номера"])


@router.get("", summary="Список номеров", response_model=list[RoomSchema])
async def get_rooms(session: SessionDep):
    rooms_model = await RoomsRepository(session).get_all()
    return rooms_model


@router.get("/{room_id}", summary="Получение номера", response_model=RoomSchema)
async def get_room(room_id: int, session: SessionDep):
    try:
        room_model = await RoomsRepository(session).get_one_or_none(id=room_id)
        if room_model is None:
            raise ObjectNotFoundException
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комнаты с таким номером не найдено",
        )
    return room_model


@router.post("", summary="Создание номера")
async def add_room(new_room: AddRoomSchema, session: SessionDep):
    try:
        room_model = await RoomsRepository(session).add(new_room)
        if room_model is None:
            raise ObjectIsAlreadyExistsException
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель с таким id не существует",
        )
    except ObjectIsAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Такая комната уже существует"
        )
    await session.commit()
    return room_model


@router.patch("/{room_id}", summary="Изменение номера")
async def change_room(room_id: int, new_room: ChangeRoomSchema, session: SessionDep):
    try:
        room_model = await RoomsRepository(session).get_one_or_none(id=room_id)
        if room_model is None:
            raise ObjectNotFoundException
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комнаты с таким номером не найдено",
        )
    room_model.update_from_orm(new_room)
    await session.commit()
    return room_model


@router.delete(
    "/{room_id}",
    summary="Удаление комнаты",
    dependencies=[Depends(is_admin_required), Depends(require_access_cookie)],
)
async def delete_room(room_id: int, session: SessionDep):
    try:
        room_model = await RoomsRepository(session).get_one_or_none(id=room_id)
        if room_model is None:
            raise ObjectNotFoundException
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комнаты с таким номером не найдено",
        )
    del room_model
    await session.commit()
    return {"success": True}
