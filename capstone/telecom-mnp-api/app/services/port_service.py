from datetime import datetime, timezone

from app.exceptions.custom_exceptions import DomainError
from app.repositories.document_repository import DocumentRepository
from app.repositories.operator_repository import OperatorRepository
from app.repositories.port_repository import PortRepository
from app.repositories.otp_repository import OtpRepository
from app.utils.constants import PortRequestStatus
from app.utils.validators import ensure_distinct_operators, validate_mobile_number


class PortService:
    def __init__(self):
        self.port_repository = PortRepository()
        self.operator_repository = OperatorRepository()
        self.document_repository = DocumentRepository()
        self.otp_repository = OtpRepository()

    def create_request(self, user: dict, payload: dict, otp_service) -> dict:
        validate_mobile_number(payload["mobile_number"])
        ensure_distinct_operators(payload["current_operator"], payload["target_operator"])
        current_operator = self.operator_repository.get_by_name(payload["current_operator"])
        target_operator = self.operator_repository.get_by_name(payload["target_operator"])
        if not current_operator or not target_operator:
            raise DomainError("Both current and target operators must exist", status_code=404)
        existing = [
            request
            for request in self.port_repository.list_by_mobile(payload["mobile_number"])
            if request["status"] not in {PortRequestStatus.rejected.value, PortRequestStatus.completed.value}
        ]
        if existing:
            raise DomainError("An active port request already exists for this mobile number", status_code=409)
        now = datetime.now(timezone.utc).isoformat()
        port_request = self.port_repository.create(
            {
                "user_id": user["id"],
                "mobile_number": payload["mobile_number"],
                "current_operator": payload["current_operator"],
                "target_operator": payload["target_operator"],
                "circle": payload["circle"],
                "status": PortRequestStatus.initiated.value,
                "otp_verified": False,
                "documents_uploaded": False,
                "created_at": now,
                "updated_at": now,
            }
        )
        otp_service.send_otp(payload["mobile_number"])
        return port_request

    def list_my_requests(self, user_id: str) -> list[dict]:
        return self.port_repository.list_by_user(user_id)

    def list_all(self) -> list[dict]:
        return self.port_repository.list_all()

    def verify_request(self, request_id: str, agent: dict) -> dict:
        port_request = self._require_request(request_id)
        otp_log = self.otp_repository.get_by_mobile(port_request["mobile_number"])
        if not otp_log or not otp_log["verified"]:
            raise DomainError("OTP verification must be completed first", status_code=400)
        if not self.document_repository.list_by_port_request(request_id):
            raise DomainError("At least one KYC document must be uploaded before verification", status_code=400)
        updated = self.port_repository.update(
            request_id,
            {
                "status": PortRequestStatus.verified.value,
                "verified_by": agent["id"],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return updated

    def admin_decision(self, request_id: str, admin: dict, action: str) -> dict:
        port_request = self._require_request(request_id)
        if action == "approve":
            if port_request["status"] != PortRequestStatus.verified.value:
                raise DomainError("Only verified requests can be approved", status_code=400)
            final_status = PortRequestStatus.completed.value
            message = "Port request approved and completed"
        else:
            if port_request["status"] == PortRequestStatus.completed.value:
                raise DomainError("Completed requests cannot be rejected", status_code=400)
            final_status = PortRequestStatus.rejected.value
            message = "Port request rejected"
        updated = self.port_repository.update(
            request_id,
            {
                "status": final_status,
                "admin_action_by": admin["id"],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return {"message": message, "port_request": updated}

    def _require_request(self, request_id: str) -> dict:
        port_request = self.port_repository.get_by_id(request_id)
        if not port_request:
            raise DomainError("Port request not found", status_code=404)
        return port_request
