from pwdlib import PasswordHash

from src.config import security
from src.exceptions import ObjectNotValidException


class AuthService:
    def __init__(
        self, password_hash: PasswordHash = PasswordHash.recommended()
    ) -> None:
        self.password_hash = password_hash

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.password_hash.verify(plain_password, hashed_password)

    def get_password_hash(self, password) -> str:
        return self.password_hash.hash(password)

    async def login(self, db, email: str, password: str):
        db_user = await db.users.get_one_or_none(email=email)
        if db_user is None or not self.verify_password(password, db_user.hashed_password):
            raise ObjectNotValidException
        return db_user

    @staticmethod
    def create_access_token(user_id: int) -> str:
        return security.create_access_token(uid=str(user_id), data={"user_id": user_id})

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        return security.create_refresh_token(uid=str(user_id))

    @staticmethod
    def refresh_access_token(uid: str) -> str:
        return security.create_access_token(uid=uid, fresh=False)
