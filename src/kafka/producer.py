from faststream.kafka import KafkaBroker

from src.config import settings

broker = KafkaBroker(settings.KAFKA_BOOTSTRAP_SERVERS)

booking_delete_publisher = broker.publisher("booking.delete")
booking_created_publisher = broker.publisher("booking.created")
