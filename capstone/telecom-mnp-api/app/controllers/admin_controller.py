from collections import Counter

from fastapi import APIRouter, Depends

from app.core.dependencies import require_roles
from app.repositories.port_repository import PortRepository
from app.services.port_service import PortService

router = APIRouter(prefix="/admin", tags=["admin"])
service = PortService()
repository = PortRepository()


@router.put("/port/{request_id}/approve")
def approve_request(request_id: str, current_user: dict = Depends(require_roles("admin"))):
    return service.admin_decision(request_id, current_user, "approve")


@router.put("/port/{request_id}/reject")
def reject_request(request_id: str, current_user: dict = Depends(require_roles("admin"))):
    return service.admin_decision(request_id, current_user, "reject")


@router.get("/reports")
def get_reports(_: dict = Depends(require_roles("admin"))):
    requests = repository.list_all()
    status_counts = Counter(request["status"] for request in requests)
    return {
        "total_requests": len(requests),
        "status_breakdown": dict(status_counts),
    }
