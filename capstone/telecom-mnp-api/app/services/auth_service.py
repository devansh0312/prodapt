from app.core.security import create_access_token, hash_password, verify_password
from app.exceptions.custom_exceptions import DomainError
from app.repositories.user_repository import UserRepository
from app.utils.validators import validate_mobile_number


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()

    def register(self, payload: dict) -> dict:
        validate_mobile_number(payload["mobile_number"])
        if self.user_repository.get_by_email(payload["email"]):
            raise DomainError("Email is already registered", status_code=409)
        user = self.user_repository.create(
            {
                "name": payload["name"],
                "email": payload["email"],
                "password_hash": hash_password(payload["password"]),
                "mobile_number": payload["mobile_number"],
                "role": payload["role"].value if hasattr(payload["role"], "value") else payload["role"],
            }
        )
        return self._token_response(user)

    def login(self, email: str, password: str) -> dict:
        user = self.user_repository.get_by_email(email)
        if not user or not verify_password(password, user["password_hash"]):
            raise DomainError("Invalid email or password", status_code=401)
        return self._token_response(user)

    def _token_response(self, user: dict) -> dict:
        public_user = {key: value for key, value in user.items() if key != "password_hash"}
        return {
            "access_token": create_access_token(user["id"], user["role"]),
            "token_type": "bearer",
            "user": public_user,
        }
