from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from src.api.dependencies import RoomsServiceDep, is_admin_required
from src.exceptions import ObjectIsAlreadyExistsException, ObjectNotFoundException
from src.schemas.rooms import AddRoomSchema, ChangeRoomSchema, RoomSchema

router = APIRouter(prefix="/rooms", tags=["Отельные номера"])


@router.get("", summary="Список номеров", response_model=list[RoomSchema])
async def get_rooms(service: RoomsServiceDep):
    return await service.get_all()


@router.get("/{room_id}", summary="Получение номера", response_model=RoomSchema)
async def get_room(room_id: int, service: RoomsServiceDep):
    try:
        return await service.get_by_id(room_id)
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комнаты с таким номером не найдено",
        )


@router.post("", summary="Создание номера", dependencies=[Depends(is_admin_required)])
async def add_room(new_room: AddRoomSchema, service: RoomsServiceDep):
    try:
        return await service.add(new_room)
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель с таким id не существует",
        )
    except ObjectIsAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Такая комната уже существует"
        )


@router.patch(
    "/{room_id}", summary="Изменение номера", dependencies=[Depends(is_admin_required)]
)
async def change_room(room_id: int, new_room: ChangeRoomSchema, service: RoomsServiceDep):
    try:
        return await service.update(room_id, new_room)
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комнаты с таким номером не найдено",
        )


@router.delete(
    "/{room_id}",
    summary="Удаление комнаты",
    dependencies=[Depends(is_admin_required)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_room(room_id: int, service: RoomsServiceDep):
    try:
        await service.delete(room_id)
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комнаты с таким номером не найдено",
        )