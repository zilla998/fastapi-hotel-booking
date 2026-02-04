from authx import TokenPayload
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select

from src.config import config as authx_config
from src.config import security
from src.database import SessionDep
from src.enums import UserRoles
from src.exceptions import (
    ObjectEmailOrPasswordNotValidException,
    ObjectIsAlreadyExistsException,
    ObjectNotFoundException,
)
from src.models.users import UsersOrm
from src.repositories.users import UsersRepository
from src.schemas.users import (
    UserAddSchema,
    UserChangePasswordScheme,
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
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Доступ запрещен"
        )


async def get_current_user(
    payload: TokenPayload = Depends(security.access_token_required),
    session: SessionDep = None,
):
    try:
        user_id = int(payload.sub)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный токен"
        )

    try:
        user = await UsersRepository(session).get_one_or_none(id=user_id)
        if user is None:
            raise ObjectNotFoundException()
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user


async def is_admin_required(current_user=Depends(get_current_user)) -> None:
    if current_user.role != UserRoles.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Ты не админ!"
        )


@router.get(
    "",
    # Если мы делаем ручку на основной префикс то лучше оставлять path пустым! "/" может привести к ошибкам (Редиректу)
    summary="Получение списка пользователей",
    response_model=list[UserReadSchema],
    dependencies=[
        Depends(require_access_cookie),
        Depends(security.access_token_required),
    ],
    status_code=status.HTTP_200_OK,
)
async def get_users(session: SessionDep):
    query = select(UsersOrm)
    result = await session.execute(query)
    users = (
        result.scalars().all()
    )  # scalars это что-то типа objects в Django (User.objects.all())
    return users


@router.get(
    "/{id}",
    summary="Получение пользователя по id",
    dependencies=[
        Depends(require_access_cookie),
        Depends(security.access_token_required),
    ],
    response_model=UserReadSchema,  # Указываем схему, по которой будет возвращаться наш запрос
    status_code=200,
)
async def get_user(id: int, session: SessionDep):
    try:
        user_model = await UsersRepository(session).get_one_or_none(id=id)
        if user_model is None:
            raise ObjectNotFoundException()
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    return user_model


@router.post(
    "/register",
    summary="Создание пользователя",
    response_model=UserReadSchema,  # Указываем схему ответа без пароля для безопасности
    status_code=201,
)
async def register_user(
    user: UserCreateSchema, session: SessionDep, response: Response
):
    # 1. За хешировать пароль пользователя
    hashed_password = AuthService().get_password_hash(user.password)
    # 2. Добавить пользователя в БД
    user_model_data = UserAddSchema(email=user.email, hashed_password=hashed_password)
    try:
        new_user = await UsersRepository(session).add(user_model_data)
    except ObjectIsAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с такой почтой уже существует",
        )
    await session.commit()

    return new_user


# Вход пользователя в аккаунт
@router.post("/login", summary="Вход пользователя")
async def user_login(user: UserLoginSchema, response: Response, session: SessionDep):
    try:
        new_user = await UsersRepository(session).get_one_or_none(email=user.email)
        if not new_user or not AuthService().verify_password(
            user.password, new_user.hashed_password
        ):
            raise ObjectEmailOrPasswordNotValidException
    except ObjectEmailOrPasswordNotValidException:
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
    credentials: UserChangePasswordScheme,
    session: SessionDep,
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
    await session.commit()

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
)
async def delete_user(user_id: int, session: SessionDep):
    try:
        user = await UsersRepository(session).get_one_or_none(id=user_id)
        if user is None:
            raise ObjectNotFoundException()
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким id не найден",
        )

    await session.delete(user)
    await session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/refresh")
async def refresh(
    response: Response, payload: TokenPayload = Depends(security.refresh_token_required)
):
    # payload.sub = uid который я передаю в ручке логина/регистрации при создании refresh токена
    new_access = security.create_access_token(uid=payload.sub)

    security.set_access_cookies(response, new_access)

    return {"message": "refreshed token"}


@router.post(
    "/change-role",
    summary="Изменение роли пользователя",
    response_model=UserReadSchema,
    # dependencies=[Depends(is_admin_required)],
)
async def change_role(user_id: int, role: str, session: SessionDep):
    try:
        user_model = await UsersRepository(session).get_one_or_none(id=user_id)
        if user_model is None:
            raise ObjectNotFoundException()
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Юзер не найден"
        )

    user_model.role = role
    await session.commit()
    await session.refresh(user_model)
    return user_model
