from authx import TokenPayload
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from src.api.dependencies import DBDep, PaginationDep
from src.config import config as authx_config
from src.config import security
from src.database import SessionDep
from src.enums import UserRoles
from src.exceptions import (
    ObjectIsAlreadyExistsException,
    ObjectNotAllowedException,
    ObjectNotFoundException,
    ObjectNotValidException,
)
from src.repositories.users import UsersRepository
from src.schemas.users import (
    UserAddSchema,
    UserChangePasswordSchema,
    UserCreateSchema,
    UserLoginSchema,
    UserReadSchema,
)
from src.services.auth import AuthService

router = APIRouter(
    prefix="/users", tags=["Пользователи"]
)  # Создаем отдельный router для users


def require_access_cookie(request: Request) -> None:
    if not request.cookies.get(authx_config.JWT_ACCESS_COOKIE_NAME):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Доступ разрешен только авторизованным пользователям!",
        )


async def get_current_user(
    payload: TokenPayload = Depends(security.access_token_required), db: DBDep = None
):
    try:
        user_id = int(payload.sub)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный токен"
        )

    try:
        user = await db.users.get_one_or_none(id=user_id)
        if user is None:
            raise ObjectNotFoundException()
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user


async def is_admin_required(
    _: None = Depends(require_access_cookie), current_user=Depends(get_current_user)
) -> None:
    if require_access_cookie:
        if current_user.role != UserRoles.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ только для администратора",
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
    return await db.users.get_all(limit=pagination.per_page, offset=pagination.page)


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
            detail=f"Пользователь с id: {user_id} не найден",
        )
    return user


@router.post(
    "/register",
    summary="Создание пользователя",
    response_model=UserReadSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(user: UserCreateSchema, db: DBDep):
    # 1. За хешировать пароль пользователя
    hashed_password = AuthService().get_password_hash(user.password)
    # 2. Добавить пользователя в БД
    user_model_data = UserAddSchema(email=user.email, hashed_password=hashed_password)
    try:
        new_user = await db.users.add(user_model_data)
    except ObjectIsAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с такой почтой уже существует",
        )

    await db.commit()
    return new_user


# Вход пользователя в аккаунт
@router.post("/login", summary="Вход пользователя")
async def user_login(user: UserLoginSchema, response: Response, db: DBDep):
    try:
        new_user = await db.users.get_one_or_none(email=user.email)
        if new_user is None or not AuthService().verify_password(
            user.password, new_user.hashed_password
        ):
            raise ObjectNotValidException
    except ObjectNotValidException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователя с такими данными не существует",
        )

    access_token = AuthService.create_access_token(new_user.id)
    refresh_token = AuthService.create_refresh_token(new_user.id)

    response.set_cookie(authx_config.JWT_ACCESS_COOKIE_NAME, access_token)
    response.set_cookie(authx_config.JWT_REFRESH_COOKIE_NAME, refresh_token)

    return {"success": True}


# Выход пользователя из аккаунта
@router.post(
    "/change-password",
    summary="Смена пароля пользователя",
    dependencies=[
        Depends(require_access_cookie),
        Depends(security.access_token_required),
    ],
)
async def user_change_password(
    credentials: UserChangePasswordSchema,
    db: DBDep,
    current_user=Depends(get_current_user),
):
    if credentials.new_password != credentials.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Пароли не совпадают"
        )

    if current_user["hashed_password"] != credentials.current_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Текущий пароль неверный"
        )

    current_user["hashed_password"] = credentials.new_password

    await db.commit()
    return {"message": "Пароль успешно изменен"}


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
            detail=f"Пользователь с id: {user_id} не найден",
        )


@router.post("/refresh")
async def refresh(
    response: Response, payload: TokenPayload = Depends(security.refresh_token_required)
):
    # payload.sub = uid который я передаю в ручке логина/регистрации при создании refresh токена
    new_access = security.create_access_token(uid=payload.sub, fresh=False)

    security.set_access_cookies(new_access, response=response)

    return {"message": "refreshed token"}
