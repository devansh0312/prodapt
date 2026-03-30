from datetime import datetime, timezone

from app.exceptions.custom_exceptions import DomainError
from app.repositories.document_repository import DocumentRepository
from app.repositories.port_repository import PortRepository


class DocumentService:
    def __init__(self):
        self.repository = DocumentRepository()
        self.port_repository = PortRepository()

    def upload(self, current_user: dict, payload: dict) -> dict:
        port_request = self.port_repository.get_by_id(payload["port_request_id"])
        if not port_request:
            raise DomainError("Port request not found", status_code=404)
        if current_user["role"] == "customer" and port_request["user_id"] != current_user["id"]:
            raise DomainError("You can upload documents only for your own requests", status_code=403)
        user_id = payload.get("user_id") or port_request["user_id"]
        document = self.repository.create(
            {
                "user_id": user_id,
                "port_request_id": payload["port_request_id"],
                "type": payload["type"].value if hasattr(payload["type"], "value") else payload["type"],
                "file_url": payload["file_url"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        self.port_repository.update(
            payload["port_request_id"],
            {
                "documents_uploaded": True,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return document

    def list_by_user(self, user_id: str) -> list[dict]:
        return self.repository.list_by_user(user_id)
