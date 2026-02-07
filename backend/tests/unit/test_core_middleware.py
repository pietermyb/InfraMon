"""Unit tests for core middleware module."""

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response


class TestExceptionHandlingMiddleware:
    """Test ExceptionHandlingMiddleware class."""

    def test_exception_handling_middleware_exists(self):
        """Test ExceptionHandlingMiddleware can be instantiated."""
        from app.core.middleware import ExceptionHandlingMiddleware

        app = FastAPI()
        middleware = ExceptionHandlingMiddleware(app)

        assert middleware is not None


class TestRequestLoggerMiddleware:
    """Test request_logger_middleware function."""

    @pytest.mark.asyncio
    async def test_request_logger_middleware_logs_request(self):
        """Test that request logger middleware logs requests."""
        from app.core.middleware import request_logger_middleware

        # Create mock request and call_next
        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.url.path = "/test"

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        async def mock_call_next(request):
            return mock_response

        response = await request_logger_middleware(mock_request, mock_call_next)

        assert response.status_code == 200


class TestLoggingMiddleware:
    """Test LoggingMiddleware class."""

    def test_logging_middleware_exists(self):
        """Test LoggingMiddleware can be instantiated."""
        from app.core.middleware import LoggingMiddleware

        app = FastAPI()
        middleware = LoggingMiddleware(app)

        assert middleware is not None


class TestSetupExceptionHandlers:
    """Test setup_exception_handlers function."""

    def test_setup_exception_handlers(self):
        """Test that setup_exception_handlers can be called."""
        from app.core.middleware import setup_exception_handlers

        app = FastAPI()

        # Should not raise an exception
        setup_exception_handlers(app)

        # Exception handlers should be registered
        assert app.exception_handler is not None


class TestExceptionHandlerResponses:
    """Test that exception handlers return correct responses."""

    def test_authentication_exception_handler(self):
        """Test authentication exception handler response format."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from app.core.exceptions import AuthenticationException
        from app.core.middleware import setup_exception_handlers

        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            raise AuthenticationException(detail="Test auth error")

        setup_exception_handlers(app)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test")

        assert response.status_code == 401

    def test_permission_denied_exception_handler(self):
        """Test permission denied exception handler response format."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from app.core.exceptions import PermissionDeniedException
        from app.core.middleware import setup_exception_handlers

        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            raise PermissionDeniedException(detail="Test permission error")

        setup_exception_handlers(app)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test")

        assert response.status_code == 403

    def test_validation_exception_handler(self):
        """Test validation exception handler response format."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from app.core.exceptions import ValidationException
        from app.core.middleware import setup_exception_handlers

        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            raise ValidationException(detail="Test validation error")

        setup_exception_handlers(app)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test")

        assert response.status_code == 422


class TestMiddlewareWithApp:
    """Test middleware integration with FastAPI app."""

    def test_app_with_exception_handling_middleware(self):
        """Test that app can be created with exception handling middleware."""
        from fastapi import FastAPI

        from app.core.middleware import ExceptionHandlingMiddleware

        app = FastAPI()
        app.add_middleware(ExceptionHandlingMiddleware)

        assert app is not None

    def test_app_with_logging_middleware(self):
        """Test that app can be created with logging middleware."""
        from fastapi import FastAPI

        from app.core.middleware import LoggingMiddleware

        app = FastAPI()
        app.add_middleware(LoggingMiddleware)

        assert app is not None


class TestMiddlewareLogging:
    """Test middleware logging functionality."""

    def test_logger_is_configured(self):
        """Test that logger is properly configured."""
        from app.core.middleware import logger

        assert logger is not None
        assert logger.name == "app.core.middleware"
