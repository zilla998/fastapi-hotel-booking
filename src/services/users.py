from src.schemas.users import UserAddSchema, UserCreateSchema
from src.services.auth import AuthService


class UserService:
    @staticmethod
    async def create(db, user_in: UserCreateSchema):
        # 1. За хешировать пароль пользователя
        hashed_password = AuthService().get_password_hash(user_in.password)
        # 2. Добавить пользователя в БД
        user_model_data = UserAddSchema(
            email=user_in.email, hashed_password=hashed_password
        )
        new_user = await db.users.add(user_model_data)

        await db.commit()
        return new_user

    @staticmethod
    async def change_password(db, user_id, new_password):
        new_hashed_password = AuthService().get_password_hash(new_password)
        await db.users.patch("hashed_password", new_hashed_password, id=user_id)
