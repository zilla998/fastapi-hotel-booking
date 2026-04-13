from authx import TokenPayload
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from src.api.dependencies import DBDep, PaginationDep
from src.config import config as authx_config
from src.config import security
from src.enums import ErrorCode, UserRoles
from src.exceptions import (
    ObjectIsAlreadyExistsException,
    ObjectNotFoundException,
    ObjectNotValidException,
)
from src.schemas.users import (
    UserChangePasswordSchema,
    UserCreateSchema,
    UserLoginSchema,
    UserPatchProfileSchema,
    UserReadSchema,
)
from src.services.auth import AuthService
from src.services.users import UserService

router = APIRouter(prefix="/users", tags=["Пользователи"])


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
            status_code=404,
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


@router.get(
    "",
    summary="Получение списка пользователей",
    response_model=list[UserReadSchema],
    dependencies=[
        Depends(is_admin_required),
    ],
)
async def get_users(db: DBDep, pagination: PaginationDep):
    offset = (pagination.page - 1) * pagination.per_page
    return await db.users.get_all(limit=pagination.per_page, offset=offset)


@router.get(
    "/me",
    summary="Профиль текущего пользователя",
    dependencies=[
        Depends(require_access_cookie),
    ],
    response_model=UserReadSchema,
)
async def get_my_profile(db: DBDep, current_user=Depends(get_current_user)):
    """Получение профиля текущего пользователя"""
    return await db.users.get_one_or_none(id=current_user.id)


@router.get(
    "/{user_id}",
    summary="Получение пользователя по id",
    dependencies=[
        Depends(is_admin_required),
    ],
    response_model=UserReadSchema,
)
async def get_user(user_id: int, db: DBDep):
    try:
        user = await db.users.get_one_or_none(id=user_id)
        if user is None:
            raise ObjectNotFoundException
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.USER_NOT_FOUND},
        )
    return user


@router.post(
    "/register",
    summary="Создание пользователя",
    response_model=UserReadSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(user: UserCreateSchema, db: DBDep):
    if user.password != user.confirm_password:
        raise ObjectNotValidException
    try:
        user_data = await db.users.get_one_or_none(email=user.email)
        if user_data:
            raise ObjectIsAlreadyExistsException
    except ObjectIsAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": ErrorCode.EMAIL_ALREADY_EXISTS},
        )

    return await UserService().create(db, user)


@router.patch(
    "/me",
    summary="Редактирование профиля",
    dependencies=[
        Depends(require_access_cookie),
    ],
)
async def user_profile_patch(
    credentials: UserPatchProfileSchema,
    db: DBDep,
    current_user=Depends(get_current_user),
):
    """Редактирование профиля пользователя."""
    return await db.users.patch_partial(credentials, id=current_user.id)


@router.post(
    "/change-password",
    summary="Смена пароля пользователя",
    dependencies=[
        Depends(require_access_cookie),
    ],
)
async def user_change_password(
    credentials: UserChangePasswordSchema,
    db: DBDep,
    response: Response,
    current_user=Depends(get_current_user),
):
    if not AuthService().verify_password(
        credentials.current_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": ErrorCode.INVALID_CREDENTIALS},
        )

    await UserService().change_password(db, current_user.id, credentials.new_password)

    response.delete_cookie(authx_config.JWT_ACCESS_COOKIE_NAME)
    response.delete_cookie(authx_config.JWT_REFRESH_COOKIE_NAME)

    return {"message": "Пароль успешно изменен"}


# Вход пользователя в аккаунт
@router.post("/login", summary="Вход пользователя")
async def user_login(user_in: UserLoginSchema, response: Response, db: DBDep):
    try:
        db_user = await db.users.get_one_or_none(email=user_in.email)
        if db_user is None or not AuthService().verify_password(
            user_in.password, db_user.hashed_password
        ):
            raise ObjectNotValidException
    except ObjectNotValidException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": ErrorCode.INVALID_CREDENTIALS},
        )

    access_token = AuthService.create_access_token(db_user.id)
    refresh_token = AuthService.create_refresh_token(db_user.id)

    response.set_cookie(authx_config.JWT_ACCESS_COOKIE_NAME, access_token)
    response.set_cookie(authx_config.JWT_REFRESH_COOKIE_NAME, refresh_token)

    return {"success": True}


# Выход пользователя из аккаунта
@router.post("/logout", summary="Выход пользователя")
async def user_logout(response: Response):
    response.delete_cookie(authx_config.JWT_ACCESS_COOKIE_NAME)
    response.delete_cookie(authx_config.JWT_REFRESH_COOKIE_NAME)
    return {"logout": True}


# Удаление пользователя
@router.delete(
    "/{user_id}",
    summary="Удаление пользователя",
    dependencies=[Depends(is_admin_required)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id: int, db: DBDep):
    try:
        await db.users.delete(id=user_id)
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.USER_NOT_FOUND},
        )


@router.post("/refresh")
async def refresh(
    response: Response, payload: TokenPayload = Depends(security.refresh_token_required)
):
    # payload.sub = uid который я передаю в ручке логина/регистрации при создании refresh токена
    new_access = security.create_access_token(uid=payload.sub, fresh=False)

    security.set_access_cookies(new_access, response=response)

    return {"message": "refreshed token"}
