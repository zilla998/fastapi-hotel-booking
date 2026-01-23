from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    DB_NAME: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_HOST: str

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    _env_path = Path(__file__).resolve().parent.parent / ".env"
    model_config = SettingsConfigDict(env_file=_env_path, env_file_encoding="utf-8")

    # Так не смогло найти .env
    # model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
