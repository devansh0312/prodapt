from fastapi import APIRouter

from app.schemas.auth_schema import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
service = AuthService()


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest):
    return service.register(payload.model_dump())


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    return service.login(payload.email, payload.password)
