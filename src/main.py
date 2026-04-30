import sys
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src.admin import setup_admin
from src.api.routers.bookings import router as booking_router
from src.api.routers.facilities import (
    router as facilities_router,
)
from src.api.routers.hotels import router as hotels_router
from src.api.routers.rooms import router as rooms_router
from src.api.routers.users import router as users_router
from src.cache import close_redis, init_redis
from src.config import config, settings
from src.kafka.consumer import router as kafka_router
from src.kafka.producer import broker


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis(settings.REDIS_URL)  # Запускаем redis

    broker.include_router(kafka_router)  # Подключаем Kafka-router
    await broker.start()  # запускаем брокер
    yield
    await broker.close()  # останавливаем при завершении
    await close_redis()


app = FastAPI(lifespan=lifespan)

# Добавляем SessionMiddleware, необходимый для sqladmin
app.add_middleware(SessionMiddleware, secret_key=config.JWT_SECRET_KEY)

# Подключаем админку
setup_admin(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


# routers
app.include_router(users_router)
app.include_router(hotels_router)
app.include_router(rooms_router)
app.include_router(facilities_router)
app.include_router(booking_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, log_level="info")
