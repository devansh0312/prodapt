from datetime import datetime

from pydantic import BaseModel

from app.utils.constants import DocumentType


class DocumentCreate(BaseModel):
    user_id: str | None = None
    port_request_id: str
    type: DocumentType
    file_url: str


class DocumentResponse(BaseModel):
    id: str
    user_id: str
    port_request_id: str
    type: DocumentType
    file_url: str
    created_at: datetime
