from authx import TokenPayload
from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.api.dependencies import (
    DBDep,
    PaginationDep,
    get_current_user,
    is_admin_required,
    require_access_cookie,
)
from src.config import config as authx_config
from src.config import security
from src.enums import ErrorCode
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


@router.get(
    "",
    summary="Получение списка пользователей",
    response_model=list[UserReadSchema],
    dependencies=[
        Depends(is_admin_required),
    ],
)
async def get_users(db: DBDep, pagination: PaginationDep):
    return await UserService.get_all(
        db,
        limit=pagination.per_page,
        offset=pagination.offset,
    )


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
    return await UserService.get_me(db, current_user.id)


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
        return await UserService.get_by_id(db, user_id)
    except ObjectNotFoundException as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.USER_NOT_FOUND},
        ) from err


@router.post(
    "/register",
    summary="Создание пользователя",
    response_model=UserReadSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(user: UserCreateSchema, db: DBDep):
    if user.password != user.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": ErrorCode.INVALID_CREDENTIALS},
        )
    try:
        return await UserService.create(db, user)
    except ObjectIsAlreadyExistsException as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": ErrorCode.EMAIL_ALREADY_EXISTS},
        ) from err


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
    return await UserService.patch_profile(db, current_user.id, credentials)


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

    await UserService.change_password(db, current_user.id, credentials.new_password)

    response.delete_cookie(authx_config.JWT_ACCESS_COOKIE_NAME)
    response.delete_cookie(authx_config.JWT_REFRESH_COOKIE_NAME)

    return {"message": "Пароль успешно изменен"}


# Вход пользователя в аккаунт
@router.post("/login", summary="Вход пользователя")
async def user_login(user_in: UserLoginSchema, response: Response, db: DBDep):
    try:
        db_user = await AuthService().login(db, user_in.email, user_in.password)
    except ObjectNotValidException as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": ErrorCode.INVALID_CREDENTIALS},
        ) from err

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
        await UserService.delete(db, user_id)
    except ObjectNotFoundException as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.USER_NOT_FOUND},
        ) from err


@router.post("/refresh")
async def refresh(
    response: Response, payload: TokenPayload = Depends(security.refresh_token_required)
):
    new_access = AuthService.refresh_access_token(payload.sub)
    security.set_access_cookies(new_access, response=response)
    return {"message": "refreshed token"}
