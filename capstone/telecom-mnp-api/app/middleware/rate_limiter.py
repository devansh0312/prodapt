import time
from collections import defaultdict, deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        settings = get_settings()
        self.limit = settings.rate_limit_requests
        self.window_seconds = settings.rate_limit_window_seconds

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current = time.time()
        timeline = self._requests[client_ip]
        while timeline and current - timeline[0] > self.window_seconds:
            timeline.popleft()
        if len(timeline) >= self.limit:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        timeline.append(current)
        return await call_next(request)
