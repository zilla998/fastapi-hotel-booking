from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import DBDep
from src.api.routers.users import get_current_user, require_access_cookie
from src.exceptions import ObjectNotFoundException
from src.kafka.producer import get_producer
from src.schemas.booking import BookingCreateSchema, BookingReadSchema
from src.services.booking import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.get(
    "", summary="Получение списка бронирования", response_model=list[BookingReadSchema]
)
async def get_all_booking(db: DBDep):
    return await db.booking.get_all()


@router.post(
    "",
    summary="Бронирование отеля",
    response_model=BookingReadSchema,
    dependencies=[Depends(require_access_cookie)],
)
async def hotel_reservation(
    booking: BookingCreateSchema,
    db: DBDep,
    current_user=Depends(get_current_user),
):
    return await BookingService(db).add_booking(booking, current_user)


@router.delete(
    "/{booking_id}",
    dependencies=[Depends(require_access_cookie)],
    status_code=204,
)
async def delete_booking(booking_id: int, db: DBDep):
    try:
        await db.booking.delete(id=booking_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Booking not found")

    producer = await get_producer()
    await producer.send_and_wait(
        "booking.delete",
        {
            "booking_id": booking_id,
            "message": "Бронь успешно отменена",
        },
    )  # Эта функция с гарантией доставки, а send() без гарантии доставки
