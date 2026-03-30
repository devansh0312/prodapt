from fastapi import APIRouter, Depends, status

from app.core.dependencies import require_roles
from app.schemas.operator_schema import OperatorCreate
from app.services.operator_service import OperatorService

router = APIRouter(prefix="/operators", tags=["operators"])
service = OperatorService()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_operator(payload: OperatorCreate, _: dict = Depends(require_roles("admin"))):
    return service.create(payload.model_dump())


@router.get("")
def list_operators(_: dict = Depends(require_roles("admin", "agent", "customer"))):
    return service.list_all()
