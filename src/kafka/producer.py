import json  # для сериализации данных в JSON перед отправкой в Kafka
from aiokafka import AIOKafkaProducer  # асинхронный Kafka producer
from src.config import settings  # настройки приложения (в т.ч. KAFKA_BOOTSTRAP_SERVERS)

producer: AIOKafkaProducer | None = None  # глобальный экземпляр producer'а, переиспользуется во всём приложении

async def get_producer() -> AIOKafkaProducer:
    global producer  # обращаемся к глобальной переменной
    if producer is None:  # создаём producer только один раз (singleton)
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,  # адрес Kafka-брокера из .env
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),  # сериализуем dict → JSON → bytes
        )
        await producer.start()  # подключаемся к Kafka, после этого можно отправлять сообщения
    return producer  # возвращаем готовый producer

async def stop_producer():
    global producer  # обращаемся к глобальной переменной
    if producer:  # останавливаем только если producer был создан
        await producer.stop()  # корректно закрываем соединение с Kafka
        producer = None  # сбрасываем, чтобы при следующем вызове get_producer создался заново
