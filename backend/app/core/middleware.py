"""Global exception handlers and middleware."""

import logging
import traceback
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.exceptions import (
    AppException,
    AuthenticationException,
    PermissionDeniedException,
    ValidationException,
)

logger = logging.getLogger(__name__)


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    """Global exception handling middleware."""

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            return await self.handle_exception(request, exc)

    async def handle_exception(self, request: Request, exc: Exception) -> Response:
        if isinstance(exc, AppException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
                headers=exc.headers,
            )

        if isinstance(exc, PermissionError):
            logger.error(f"Permission error: {exc}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Permission denied"},
            )

        if isinstance(exc, ValueError):
            logger.error(f"Value error: {exc}")
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": str(exc)},
            )

        logger.error(f"Unhandled exception: {exc}")
        logger.error(traceback.format_exc())

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


async def request_logger_middleware(request: Request, call_next):
    """Log incoming requests."""
    logger.info(f"Incoming request: {request.method} {request.url.path}")

    response = await call_next(request)

    logger.info(f"Response: {request.method} {request.url.path} - {response.status_code}")

    return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Detailed request/response logging middleware."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = datetime.now()

        try:
            response = await call_next(request)

            process_time = (datetime.now() - start_time).total_seconds()

            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )

            return response
        except Exception as exc:
            process_time = (datetime.now() - start_time).total_seconds()
            logger.error(
                f"{request.method} {request.url.path} - "
                f"Error: {exc} - "
                f"Time: {process_time:.3f}s"
            )
            raise


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup exception handlers for the application."""

    @app.exception_handler(AuthenticationException)
    async def authentication_exception_handler(
        request: Request, exc: AuthenticationException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )

    @app.exception_handler(PermissionDeniedException)
    async def permission_denied_exception_handler(
        request: Request, exc: PermissionDeniedException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(
        request: Request, exc: ValidationException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
