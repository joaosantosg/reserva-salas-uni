import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config.logging import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requisições"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            f"Method: {request.method} Path: {request.url.path} "
            f"Status: {response.status_code} Time: {process_time:.3f}s"
        )
        return response
