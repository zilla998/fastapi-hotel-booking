from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 64


class UserReadSchema(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)  # Разрешаем читать ORM-объекты


# Схема пользователя
class UserSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)

    model_config = ConfigDict(
        extra="forbid"
    )  # Запрещаем передавать дополнительные параметры кроме тех которые указаны в схеме


# Схема создания пользователя
class UserCreateSchema(UserSchema):
    confirm_password: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        return self


# Схема авторизации пользователя
class UserLoginSchema(UserSchema):
    pass


class UserChangePasswordSchema(BaseModel):
    current_password: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )
    new_password: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )
    confirm_password: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        return self


class UserAddSchema(BaseModel):
    email: EmailStr
    hashed_password: str

    model_config = ConfigDict(extra="forbid")


class UserInternalSchema(UserReadSchema):
    hashed_password: str


# Backward compatibility alias.
UserChangePasswordScheme = UserChangePasswordSchema
