from datetime import timedelta
from pathlib import Path

from authx import AuthX, AuthXConfig
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_NAME: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_HOST: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    JWT_SECRET_KEY: str

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    _env_path = Path(__file__).resolve().parent.parent / ".env"
    model_config = SettingsConfigDict(env_file=_env_path, env_file_encoding="utf-8")


settings = Settings()


# AuthX JWT Token auth
config = AuthXConfig()
config.JWT_SECRET_KEY = settings.JWT_SECRET_KEY

config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_REFRESH_COOKIE_NAME = "my_refresh_token"

config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
config.JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

config.JWT_COOKIE_CSRF_PROTECT = False  # Отключается только для разработки

security = AuthX(config=config)
