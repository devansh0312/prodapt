from app.core.database import db


class OperatorRepository:
    def create(self, payload: dict) -> dict:
        return db.operators.insert_one(payload)

    def get_by_name(self, name: str) -> dict | None:
        return db.operators.find_one(name=name)

    def list_all(self) -> list[dict]:
        return db.operators.all()
