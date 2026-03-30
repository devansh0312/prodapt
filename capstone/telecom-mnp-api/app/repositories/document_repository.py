from app.core.database import db


class DocumentRepository:
    def create(self, payload: dict) -> dict:
        return db.documents.insert_one(payload)

    def list_by_user(self, user_id: str) -> list[dict]:
        return db.documents.find_many(user_id=user_id)

    def list_by_port_request(self, port_request_id: str) -> list[dict]:
        return db.documents.find_many(port_request_id=port_request_id)
