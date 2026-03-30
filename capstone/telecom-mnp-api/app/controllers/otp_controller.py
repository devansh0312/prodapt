from fastapi import APIRouter, Depends

from app.core.dependencies import require_roles
from app.schemas.otp_schema import OtpSendRequest, OtpVerifyRequest
from app.services.otp_service import OtpService

router = APIRouter(prefix="/otp", tags=["otp"])
service = OtpService()


@router.post("/send")
def send_otp(payload: OtpSendRequest, _: dict = Depends(require_roles("customer"))):
    return service.send_otp(payload.mobile_number)


@router.post("/verify")
def verify_otp(payload: OtpVerifyRequest, _: dict = Depends(require_roles("customer"))):
    return service.verify_otp(payload.mobile_number, payload.otp)
