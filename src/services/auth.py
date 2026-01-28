from pwdlib import PasswordHash

from config import security


class AuthService:
    password_hash = PasswordHash.recommended()

    def verify_password(self, plain_password, hashed_password):
        return self.password_hash.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.password_hash.hash(password)

    @staticmethod
    def create_access_token(user_id: int):
        access_token = security.create_access_token(
            uid=str(user_id), data={"user_id": user_id}
        )
        return access_token

    @staticmethod
    def create_refresh_token(user_id: int):
        refresh_token = security.create_refresh_token(uid=str(user_id))
        return refresh_token
