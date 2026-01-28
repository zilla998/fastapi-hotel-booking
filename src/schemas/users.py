from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserReadSchema(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)  # Разрешаем читать ORM-объекты


# Схема пользователя
class UserSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)

    model_config = ConfigDict(
        extra="forbid"
    )  # Запрещаем передавать дополнительные параметры кроме тех которые указаны в схеме


# Схема создания пользователя
class UserCreateSchema(UserSchema):
    confirm_password: str = Field(min_length=8, max_length=64)


# Схема авторизации пользователя
class UserLoginSchema(UserSchema):
    pass


class UserChangePasswordScheme(BaseModel):
    current_password: str = Field(min_length=8, max_length=64)
    new_password: str = Field(min_length=8, max_length=64)
    confirm_password: str = Field(min_length=8, max_length=64)

    model_config = ConfigDict(extra="forbid")


class UserAddSchema(BaseModel):
    email: EmailStr
    hashed_password: str
