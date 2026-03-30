from app.exceptions.custom_exceptions import DomainError
from app.repositories.operator_repository import OperatorRepository


class OperatorService:
    def __init__(self):
        self.repository = OperatorRepository()

    def create(self, payload: dict) -> dict:
        if self.repository.get_by_name(payload["name"]):
            raise DomainError("Operator already exists", status_code=409)
        return self.repository.create(payload)

    def list_all(self) -> list[dict]:
        return self.repository.list_all()
