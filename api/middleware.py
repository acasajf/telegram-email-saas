import logging
from fastapi import Request

logger = logging.getLogger(__name__)


async def log_requests(request: Request, call_next):
    """Middleware para logar requisições."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response
