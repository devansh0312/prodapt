from fastapi import APIRouter, Depends, status

from app.core.dependencies import require_roles
from app.schemas.port_request_schema import PortRequestCreate
from app.services.otp_service import OtpService
from app.services.port_service import PortService

router = APIRouter(prefix="/port", tags=["porting"])
service = PortService()
otp_service = OtpService()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_port_request(payload: PortRequestCreate, current_user: dict = Depends(require_roles("customer"))):
    return service.create_request(current_user, payload.model_dump(), otp_service)


@router.get("/my")
def get_my_requests(current_user: dict = Depends(require_roles("customer"))):
    return service.list_my_requests(current_user["id"])


@router.get("")
def get_all_requests(_: dict = Depends(require_roles("admin", "agent"))):
    return service.list_all()


@router.put("/{request_id}/verify")
def verify_request(request_id: str, current_user: dict = Depends(require_roles("agent"))):
    return service.verify_request(request_id, current_user)
