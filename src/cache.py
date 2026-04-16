from redis.asyncio import Redis

# Глобальный экземпляр — создаётся один раз при старте приложения
redis_client: Redis | None = None


async def init_redis(url: str) -> None:
    """Вызывается при старте приложения."""
    global redis_client
    redis_client = Redis.from_url(
        url,
        encoding="utf-8",
        decode_responses=True,  # автоматически декодировать bytes -> str
    )


async def close_redis() -> None:
    """Вызывается при остановке приложения."""
    global redis_client
    if redis_client:
        await redis_client.aclose()


def get_redis() -> Redis:
    """Dependency для FastAPI."""
    assert redis_client is not None, "Redis не инициализирован"
    return redis_client
