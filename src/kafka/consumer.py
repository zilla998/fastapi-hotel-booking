import asyncio  # стандартная библиотека для асинхронного программирования
import json  # для десериализации JSON-сообщений из Kafka

from aiokafka import AIOKafkaConsumer  # асинхронный Kafka consumer


async def consume(topics: list[str], bootstrap_servers: str = "localhost:9094"):
    # создаём consumer и подписываем его на указанные топики
    consumer = AIOKafkaConsumer(
        *topics,  # распаковываем список топиков (например, "booking.created")
        bootstrap_servers=bootstrap_servers,  # адрес Kafka-брокера
        group_id="test-consumer-group",  # группа consumer'ов — Kafka распределяет сообщения между ними
        value_deserializer=lambda v: json.loads(
            v.decode("utf-8")
        ),  # декодируем bytes → str → dict
        auto_offset_reset="earliest",  # читать с самого начала топика, если offset ещё не сохранён
    )

    await consumer.start()  # подключаемся к Kafka и начинаем получать метаданные
    print(f"Consumer запущен. Слушаю топики: {topics}")
    print("Ожидаю сообщения... (Ctrl+C для остановки)\n")

    try:
        async for msg in consumer:  # бесконечно ждём новые сообщения из топика
            print(
                f"Топик: {msg.topic} | Партиция: {msg.partition} | Offset: {msg.offset}"
            )
            print(
                f"   Данные: {msg.value}\n"
            )  # выводим десериализованное тело сообщения
    except asyncio.CancelledError:  # ловим отмену задачи (например, при Ctrl+C)
        pass
    finally:
        await consumer.stop()  # корректно закрываем соединение с Kafka в любом случае
        print("Consumer остановлен.")


if __name__ == "__main__":
    asyncio.run(
        consume(topics=["booking.created", "booking.delete"])
    )  # точка входа при запуске файла напрямую
