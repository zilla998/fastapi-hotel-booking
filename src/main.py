import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI

sys.path.append(str(Path(__file__).parent.parent))

from src.api.routers.users import router as users_router # импортируем роутер users
from src.api.routers.hotels import router as hotels_router # импортируем роутер hotels

# print(settings.DB_URL)
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


app.include_router(users_router)  # Подключаем роутер users
app.include_router(hotels_router) # Подключаем роутер hotels


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, log_level="info")
