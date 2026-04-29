from src.exceptions import ObjectIsAlreadyExistsException, ObjectNotFoundException
from src.schemas.users import UserAddSchema, UserCreateSchema, UserPatchProfileSchema
from src.services.auth import AuthService


class UserService:
    @staticmethod
    async def get_all(db, limit: int, offset: int):
        return await db.users.get_all(limit=limit, offset=offset)

    @staticmethod
    async def get_by_id(db, user_id: int):
        user = await db.users.get_one_or_none(id=user_id)
        if user is None:
            raise ObjectNotFoundException
        return user

    @staticmethod
    async def get_me(db, user_id: int):
        return await db.users.get_one_or_none(id=user_id)

    @staticmethod
    async def patch_profile(db, user_id: int, credentials: UserPatchProfileSchema):
        result = await db.users.patch_partial(credentials, id=user_id)
        await db.commit()
        return result

    @staticmethod
    async def delete(db, user_id: int):
        await db.users.delete(id=user_id)
        await db.commit()

    @staticmethod
    async def create(db, user_in: UserCreateSchema):
        existing = await db.users.get_one_or_none(email=user_in.email)
        if existing:
            raise ObjectIsAlreadyExistsException

        hashed_password = AuthService().get_password_hash(user_in.password)
        user_model_data = UserAddSchema(email=user_in.email, hashed_password=hashed_password)
        new_user = await db.users.add(user_model_data)
        await db.commit()
        return new_user

    @staticmethod
    async def change_password(db, user_id, new_password):
        new_hashed_password = AuthService().get_password_hash(new_password)
        await db.users.patch("hashed_password", new_hashed_password, id=user_id)
        await db.commit()
