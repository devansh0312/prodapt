from app.core.database import db


class PortRepository:
    def create(self, payload: dict) -> dict:
        return db.port_requests.insert_one(payload)

    def get_by_id(self, request_id: str) -> dict | None:
        return db.port_requests.find_one(id=request_id)

    def list_all(self) -> list[dict]:
        return db.port_requests.all()

    def list_by_user(self, user_id: str) -> list[dict]:
        return db.port_requests.find_many(user_id=user_id)

    def list_by_mobile(self, mobile_number: str) -> list[dict]:
        return db.port_requests.find_many(mobile_number=mobile_number)

    def update(self, request_id: str, updates: dict) -> dict | None:
        return db.port_requests.update_one(request_id, updates)
