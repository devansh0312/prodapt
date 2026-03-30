from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user, require_roles
from app.schemas.document_schema import DocumentCreate
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])
service = DocumentService()


@router.post("", status_code=status.HTTP_201_CREATED)
def upload_document(payload: DocumentCreate, current_user: dict = Depends(require_roles("customer", "agent", "admin"))):
    return service.upload(current_user, payload.model_dump())


@router.get("/{user_id}")
def list_documents(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "customer" and current_user["id"] != user_id:
        return []
    return service.list_by_user(user_id)
