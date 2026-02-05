"""Unit tests for core security module."""

import time
from datetime import timedelta

import pytest


class TestPasswordHashing:
    """Test password hashing functions in security module."""

    def test_verify_password(self):
        """Test password verification."""
        from app.core.security import get_password_hash, verify_password

        password = "testpassword"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_get_password_hash(self):
        """Test password hashing returns bcrypt hash."""
        from app.core.security import get_password_hash

        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert hashed.startswith("$2b$") or hashed.startswith("$2y$")


class TestTokenCreation:
    """Test token creation functions in security module."""

    def test_create_access_token(self):
        """Test access token creation."""
        from app.core.security import create_access_token

        data = {"sub": "testuser", "user_id": 123}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 100

    def test_create_access_token_with_custom_expiry(self):
        """Test access token creation with custom expiry."""
        from app.core.security import create_access_token

        data = {"sub": "testuser"}
        token = create_access_token(data, expires_delta=timedelta(hours=2))

        assert token is not None
        assert isinstance(token, str)

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        from app.core.security import create_refresh_token

        data = {"sub": "testuser", "user_id": 123}
        token = create_refresh_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 100


class TestRateLimitStore:
    """Test rate limit store functions."""

    def test_clear_rate_limit_store(self):
        """Test clearing rate limit store."""
        from app.core.security import RATE_LIMIT_STORE, clear_rate_limit_store

        # Add some entries
        RATE_LIMIT_STORE["test_ip"] = [time.time()]

        # Clear
        clear_rate_limit_store()

        assert len(RATE_LIMIT_STORE) == 0

    def test_get_rate_limit_stats(self):
        """Test getting rate limit stats."""
        from app.core.security import RATE_LIMIT_STORE, get_rate_limit_stats

        # Add some entries
        RATE_LIMIT_STORE["ip1"] = [time.time()]
        RATE_LIMIT_STORE["ip2"] = [time.time(), time.time()]

        stats = get_rate_limit_stats()

        assert stats["active_ips"] == 2
        assert stats["window_seconds"] == 60
        assert stats["max_requests"] == 100


class TestRateLimitMiddleware:
    """Test rate limit middleware."""

    @pytest.mark.asyncio
    async def test_rate_limit_middleware_allows_requests(self):
        """Test that rate limit middleware allows requests under limit."""
        from fastapi import FastAPI

        from app.core.security import RateLimitMiddleware

        app = FastAPI()
        middleware = RateLimitMiddleware(app, max_requests=100, window_seconds=60)

        assert middleware.max_requests == 100
        assert middleware.window_seconds == 60

    @pytest.mark.asyncio
    async def test_rate_limit_middleware_tracks_requests(self):
        """Test that rate limit middleware tracks requests per IP."""
        from unittest.mock import MagicMock

        from fastapi import FastAPI
        from starlette.requests import Request
        from starlette.responses import Response

        from app.core.security import RATE_LIMIT_STORE, RateLimitMiddleware

        # Clear store
        RATE_LIMIT_STORE.clear()

        app = FastAPI()
        middleware = RateLimitMiddleware(app, max_requests=2, window_seconds=60)

        # Create mock request
        mock_request = MagicMock(spec=Request)
        mock_request.client.host = "192.168.1.1"

        # Create mock call_next
        async def mock_call_next(request):
            return Response()

        mock_call_next = mock_call_next

        # First request
        response = await middleware.dispatch(mock_request, mock_call_next)
        assert response.status_code == 200

        # Second request
        response = await middleware.dispatch(mock_request, mock_call_next)
        assert response.status_code == 200


class TestSecurityHeadersMiddleware:
    """Test security headers middleware."""

    @pytest.mark.asyncio
    async def test_security_headers_middleware_exists(self):
        """Test that security headers middleware exists."""
        from fastapi import FastAPI

        from app.core.security import SecurityHeadersMiddleware

        app = FastAPI()
        middleware = SecurityHeadersMiddleware(app)

        assert middleware is not None


class TestRequestSizeMiddleware:
    """Test request size middleware."""

    @pytest.mark.asyncio
    async def test_request_size_middleware_exists(self):
        """Test that request size middleware exists."""
        from fastapi import FastAPI

        from app.core.security import RequestSizeMiddleware

        app = FastAPI()
        middleware = RequestSizeMiddleware(app)

        assert middleware is not None

    def test_request_size_middleware_max_body_size(self):
        """Test request size middleware has correct max body size."""
        from fastapi import FastAPI

        from app.core.security import RequestSizeMiddleware

        app = FastAPI()
        middleware = RequestSizeMiddleware(app)

        assert middleware.MAX_BODY_SIZE == 10 * 1024 * 1024


class TestInputSanitizationMiddleware:
    """Test input sanitization middleware."""

    def test_input_sanitization_middleware_exists(self):
        """Test that input sanitization middleware exists."""
        from fastapi import FastAPI

        from app.core.security import InputSanitizationMiddleware

        app = FastAPI()
        middleware = InputSanitizationMiddleware(app)

        assert middleware is not None

    def test_input_sanitization_has_dangerous_patterns(self):
        """Test that input sanitization has dangerous patterns."""
        from fastapi import FastAPI

        from app.core.security import InputSanitizationMiddleware

        app = FastAPI()
        middleware = InputSanitizationMiddleware(app)

        assert hasattr(middleware, "DANGEROUS_PATTERNS")
        assert len(middleware.DANGEROUS_PATTERNS) > 0


class TestOAuth2Scheme:
    """Test OAuth2 scheme configuration."""

    def test_oauth2_scheme_is_defined(self):
        """Test that OAuth2 scheme is defined."""
        from app.core.security import oauth2_scheme

        assert oauth2_scheme is not None


class TestAlgorithm:
    """Test algorithm configuration."""

    def test_algorithm_is_defined(self):
        """Test that algorithm is defined."""
        from app.core.security import ALGORITHM

        assert ALGORITHM is not None
        assert ALGORITHM == "HS256"
