from faststream.kafka import KafkaRouter

router = KafkaRouter()


@router.subscriber("booking.delete")
async def handle_booking_delete(data: dict):
    print(f"Получено удаление брони: {data}")


@router.subscriber("booking.created")
async def handle_booking_created(data: dict):
    print(f"Новая бронь: {data}")
