from authx import TokenPayload
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select

from exeptions import (
    ObjectEmailOrPasswordNotValidException,
    ObjectIsAlreadyExistsException,
)
from schemas.users import UserAddSchema, UserSchema
from services.auth import AuthService
from src.config import config as authx_config
from src.config import security
from src.database import SessionDep
from src.exceptions.users import UserNotFound
from src.models.users import UsersOrm
from src.repositories.users import UsersRepository
from src.schemas.users import (
    UserChangePasswordScheme,
    UserCreateSchema,
    UserLoginSchema,
    UserReadSchema,
)

router = APIRouter(
    prefix="/users", tags=["Пользователи"]
)  # Создаем отдельный router для users


def require_access_cookie(request: Request) -> None:
    if not request.cookies.get(authx_config.JWT_ACCESS_COOKIE_NAME):
        raise HTTPException(status_code=401, detail="Доступ запрещен")


async def get_current_user(request: Request, session: SessionDep):
    token = request.cookies.get("my_access_token")
    if not token:
        raise HTTPException(status_code=401)

    payload = security.verify_token(token)
    user_id = payload.sub

    return user_id


@router.get(
    "",
    # Если мы делаем ручку на основной префикс то лучше оставлять path пустым! "/" может привести к ошибкам (Редиректу)
    summary="Получение списка пользователей",
    response_model=list[UserReadSchema],
    dependencies=[
        Depends(require_access_cookie),
        Depends(security.access_token_required),
    ],
    status_code=200,
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
    query = select(UsersOrm).where(UsersOrm.id == id)
    result = await session.execute(
        query
    )  # Отправляем запрос в БД делает выборку из таблицы UsersOrm с фильтром по id
    user = (
        result.scalar_one_or_none()
    )  # Возвращает объект из результата. Если объекта нет, возвращает None
    if (
        user is None
    ):  # Если пользователя с таким id нет, возвращает статус код и сообщение об ошибки
        raise UserNotFound(name="id", uid=id)
    return user


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
            status_code=409, detail="Пользователь с такой почтой уже существует"
        )
    await session.commit()
    # 3. Добавить access и refresh токены
    access_token = AuthService.create_access_token(new_user.id)
    refresh_token = AuthService.create_refresh_token(new_user.id)

    response.set_cookie(authx_config.JWT_ACCESS_COOKIE_NAME, access_token)
    response.set_cookie(authx_config.JWT_REFRESH_COOKIE_NAME, refresh_token)

    return new_user


# TODO: Сделать все по аналогии с регистрацией и сделать зависимость user_id: UserIdDep
# Вход пользователя в аккаунт
@router.post(
    "/login",
    summary="Вход пользователя",
)
async def user_login(user: UserLoginSchema, response: Response, session: SessionDep):
    try:
        new_user = await UsersRepository(session).login(user.email, user.password)
    except ObjectEmailOrPasswordNotValidException:
        raise HTTPException(
            status_code=404, detail="Пользователя с такими данными не существует"
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
    if credentials.new_password != credentials.repeat_password:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")

    if current_user["hashed_password"] != credentials.current_password:
        raise HTTPException(status_code=400, detail="Текущий пароль неверный")

    current_user["hashed_password"] = credentials.new_password
    await session.commit()

    return {"message": "Пароль успешно изменен"}


@router.post(
    "/logout",
    summary="Выход пользователя",
)
async def user_logout(response: Response, session: SessionDep):
    response.delete_cookie(authx_config.JWT_ACCESS_COOKIE_NAME)
    return {"logout": True}


# Удаление пользователя
@router.delete(
    "/{id}",
    summary="Удаление пользователя",
)
async def delete_user(id: int, session: SessionDep):
    query = select(UsersOrm).where(UsersOrm.id == id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if user is None:
        raise UserNotFound("id", id)

    await session.delete(user)
    await session.commit()

    return Response(status_code=204)


@router.post("/refresh")
async def refresh(
    response: Response,
    payload: TokenPayload = Depends(security.refresh_token_required),
):
    # payload.sub = uid который я передаю в ручке логина/регистрации при создании refresh токена
    new_access = security.create_access_token(uid=payload.sub)

    security.set_access_cookies(response, new_access)

    return {"message": "refreshed token"}
