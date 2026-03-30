from datetime import datetime

from pydantic import BaseModel, Field

from app.utils.constants import PortRequestStatus


class PortRequestCreate(BaseModel):
    mobile_number: str
    current_operator: str = Field(min_length=2, max_length=100)
    target_operator: str = Field(min_length=2, max_length=100)
    circle: str = Field(min_length=2, max_length=100)


class PortActionResponse(BaseModel):
    message: str
    port_request: dict


class PortRequestResponse(BaseModel):
    id: str
    user_id: str
    mobile_number: str
    current_operator: str
    target_operator: str
    circle: str
    status: PortRequestStatus
    otp_verified: bool
    documents_uploaded: bool
    created_at: datetime
    updated_at: datetime
