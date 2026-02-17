import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

sys.path.append(str(Path(__file__).parent.parent))

from src.admin import setup_admin
from src.api.routers.facilities import (
    router as facilities_router,
)  # импортируем роутер facilities
from src.api.routers.hotels import router as hotels_router  # импортируем роутер hotels
from src.api.routers.rooms import router as rooms_router  # импортируем роутер rooms
from src.api.routers.users import router as users_router  # импортируем роутер users
from src.api.routers.bookings import router as booking_router
from src.config import config

app = FastAPI()

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


app.include_router(users_router)  # Подключаем роутер users
app.include_router(hotels_router)  # Подключаем роутер hotels
app.include_router(rooms_router)  # Подключаем роутер rooms
app.include_router(facilities_router)  # Подключаем роутер facilities
app.include_router(booking_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, log_level="info")
