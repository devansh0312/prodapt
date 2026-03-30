import random
from datetime import datetime, timedelta, timezone

from app.core.config import get_settings
from app.exceptions.custom_exceptions import DomainError
from app.repositories.otp_repository import OtpRepository
from app.repositories.port_repository import PortRepository
from app.utils.constants import PortRequestStatus
from app.utils.validators import validate_mobile_number


class OtpService:
    def __init__(self):
        self.repository = OtpRepository()
        self.port_repository = PortRepository()

    def send_otp(self, mobile_number: str) -> dict:
        validate_mobile_number(mobile_number)
        otp = f"{random.randint(0, 999999):06d}"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=get_settings().otp_expire_minutes)
        record = self.repository.upsert(
            mobile_number,
            {
                "mobile_number": mobile_number,
                "otp": otp,
                "verified": False,
                "expires_at": expires_at.isoformat(),
            },
        )
        return {
            "message": "OTP generated successfully",
            "mobile_number": mobile_number,
            "otp": otp,
            "expires_at": record["expires_at"],
        }

    def verify_otp(self, mobile_number: str, otp: str) -> dict:
        validate_mobile_number(mobile_number)
        record = self.repository.get_by_mobile(mobile_number)
        if not record:
            raise DomainError("OTP not found for mobile number", status_code=404)
        if datetime.fromisoformat(record["expires_at"]) < datetime.now(timezone.utc):
            raise DomainError("OTP has expired", status_code=400)
        if record["otp"] != otp:
            raise DomainError("Invalid OTP", status_code=400)
        verified = self.repository.upsert(mobile_number, {**record, "verified": True})
        for port_request in self.port_repository.list_by_mobile(mobile_number):
            if port_request["status"] == PortRequestStatus.initiated.value:
                self.port_repository.update(
                    port_request["id"],
                    {
                        "status": PortRequestStatus.otp_verified.value,
                        "otp_verified": True,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    },
                )
        return {"message": "OTP verified successfully", "otp_log": verified}
