from pwdlib import PasswordHash

from src.config import security


class AuthService:
    def __init__(
        self, password_hash: PasswordHash = PasswordHash.recommended()
    ) -> None:
        self.password_hash = password_hash

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.password_hash.verify(plain_password, hashed_password)

    def get_password_hash(self, password) -> str:
        return self.password_hash.hash(password)

    @staticmethod
    def create_access_token(user_id: int) -> str:
        access_token = security.create_access_token(
            uid=str(user_id), data={"user_id": user_id}
        )
        return access_token

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        refresh_token = security.create_refresh_token(uid=str(user_id))
        return refresh_token
