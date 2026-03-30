import logging

from fastapi import FastAPI

from app.controllers.admin_controller import router as admin_router
from app.controllers.auth_controller import router as auth_router
from app.controllers.document_controller import router as document_router
from app.controllers.operator_controller import router as operator_router
from app.controllers.otp_controller import router as otp_router
from app.controllers.port_controller import router as port_router
from app.core.config import get_settings
from app.exceptions.exception_handlers import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimiterMiddleware)
register_exception_handlers(app)


@app.get("/health")
def healthcheck():
    return {"status": "ok", "service": settings.app_name}


app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(operator_router, prefix=settings.api_prefix)
app.include_router(port_router, prefix=settings.api_prefix)
app.include_router(document_router, prefix=settings.api_prefix)
app.include_router(otp_router, prefix=settings.api_prefix)
app.include_router(admin_router, prefix=settings.api_prefix)
