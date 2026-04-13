from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import DBDep, PaginationDep, get_current_user, require_access_cookie
from src.exceptions import ObjectNotFoundException
from src.kafka.producer import booking_delete_publisher
from src.schemas.booking import BookingCreateSchema, BookingReadSchema
from src.services.booking import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.get(
    "/my",
    summary="Мои брони",
    response_model=list[BookingReadSchema],
    dependencies=[Depends(require_access_cookie)],
)
async def get_my_bookings(
    db: DBDep,
    pagination: PaginationDep,
    current_user=Depends(get_current_user),
):
    """Возвращает список броней текущего авторизованного пользователя."""
    offset = (pagination.page - 1) * pagination.per_page
    return await db.booking.get_user_bookings(
        user_id=current_user.id,
        limit=pagination.per_page,
        offset=offset,
    )


@router.post(
    "",
    summary="Бронирование отеля",
    response_model=BookingReadSchema,
    dependencies=[Depends(require_access_cookie)],
)
async def add_booking(
    booking: BookingCreateSchema,
    db: DBDep,
    current_user=Depends(get_current_user),
):
    """Добавление брони. Пользователь может забронировать только себе."""
    return await BookingService(db).add_booking(booking, current_user)


@router.delete(
    "/{booking_id}",
    dependencies=[Depends(require_access_cookie)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_booking(
    booking_id: int,
    db: DBDep,
    current_user=Depends(get_current_user),
):
    """Удаляет бронь. Пользователь может удалить только свою бронь."""
    try:
        booking = await db.booking.get_one_or_none(id=booking_id)
        if booking is None:
            raise ObjectNotFoundException
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Бронь не найдена"
        )

    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете удалить чужую бронь",
        )

    await db.booking.delete(id=booking_id)

    await booking_delete_publisher.publish(
        {
            "booking_id": booking_id,
            "message": "Бронь успешно отменена",
        },
    )
