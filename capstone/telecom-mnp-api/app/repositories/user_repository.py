from app.core.database import db


class UserRepository:
    def create(self, payload: dict) -> dict:
        return db.users.insert_one(payload)

    def get_by_email(self, email: str) -> dict | None:
        return db.users.find_one(email=email)

    def get_by_id(self, user_id: str) -> dict | None:
        return db.users.find_one(id=user_id)

    def list_all(self) -> list[dict]:
        return db.users.all()
