from typing import Annotated

from authx import TokenPayload
from fastapi import Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from redis.asyncio import Redis

from src.cache import get_redis
from src.config import config as authx_config
from src.config import security
from src.database import async_session_maker
from src.enums import ErrorCode, UserRoles
from src.exceptions import ObjectNotFoundException
from src.services.hotels import HotelsService
from src.utils.db_manager import DbManager

RedisDep = Annotated[Redis, Depends(get_redis)]


async def get_db():
    async with DbManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DbManager, Depends(get_db)]


def get_hotels_service(db: DBDep, redis: RedisDep) -> HotelsService:
    return HotelsService(db, redis)


HotelsServiceDep = Annotated[HotelsService, Depends(get_hotels_service)]


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1, description="Страница")]
    per_page: Annotated[
        int | None,
        Query(5, ge=1, le=100, description="Количество объектов на странице"),
    ]


PaginationDep = Annotated[PaginationParams, Depends()]


def require_access_cookie(request: Request) -> None:
    if not request.cookies.get(authx_config.JWT_ACCESS_COOKIE_NAME):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": ErrorCode.UNAUTHORIZED},
        )


async def get_current_user(
    payload: TokenPayload = Depends(security.access_token_required), db: DBDep = None
):
    try:
        user_id = int(payload.sub)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": ErrorCode.UNAUTHORIZED},
        )

    try:
        db_user = await db.users.get_one_or_none(id=user_id)
        if db_user is None:
            raise ObjectNotFoundException
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.USER_NOT_FOUND},
        )

    return db_user


async def is_admin_required(
    _: None = Depends(require_access_cookie), current_user=Depends(get_current_user)
) -> None:
    if current_user.role != UserRoles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": ErrorCode.FORBIDDEN},
        )


CurrentUserDep = Annotated[object, Depends(get_current_user)]
