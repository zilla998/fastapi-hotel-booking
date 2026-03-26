from faststream.kafka import KafkaBroker

broker = KafkaBroker("localhost:9094")

booking_delete_publisher = broker.publisher("booking.delete")
booking_created_publisher = broker.publisher("booking.created")
