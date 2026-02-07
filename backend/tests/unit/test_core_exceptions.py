"""Unit tests for core exceptions module."""

from fastapi import status


class TestAppException:
    """Test base AppException class."""

    def test_app_exception_default_values(self):
        """Test AppException with default values."""
        from app.core.exceptions import AppException

        exc = AppException()

        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.detail == "An error occurred"

    def test_app_exception_custom_values(self):
        """Test AppException with custom values."""
        from app.core.exceptions import AppException

        exc = AppException(detail="Custom error", status_code=404)

        assert exc.status_code == 404
        assert exc.detail == "Custom error"

    def test_app_exception_with_headers(self):
        """Test AppException with headers."""
        from app.core.exceptions import AppException

        exc = AppException(detail="Error", status_code=401, headers={"WWW-Authenticate": "Bearer"})

        assert exc.headers == {"WWW-Authenticate": "Bearer"}


class TestAuthenticationException:
    """Test AuthenticationException class."""

    def test_authentication_exception_default(self):
        """Test AuthenticationException with default detail."""
        from app.core.exceptions import AuthenticationException

        exc = AuthenticationException()

        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail == "Authentication failed"
        assert exc.headers == {"WWW-Authenticate": "Bearer"}

    def test_authentication_exception_custom(self):
        """Test AuthenticationException with custom detail."""
        from app.core.exceptions import AuthenticationException

        exc = AuthenticationException(detail="Custom auth error")

        assert exc.detail == "Custom auth error"


class TestInvalidCredentialsException:
    """Test InvalidCredentialsException class."""

    def test_invalid_credentials_exception(self):
        """Test InvalidCredentialsException has correct default."""
        from app.core.exceptions import InvalidCredentialsException

        exc = InvalidCredentialsException()

        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in exc.detail


class TestTokenExpiredException:
    """Test TokenExpiredException class."""

    def test_token_expired_exception(self):
        """Test TokenExpiredException has correct default."""
        from app.core.exceptions import TokenExpiredException

        exc = TokenExpiredException()

        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expired" in exc.detail.lower()


class TestInvalidTokenException:
    """Test InvalidTokenException class."""

    def test_invalid_token_exception(self):
        """Test InvalidTokenException has correct default."""
        from app.core.exceptions import InvalidTokenException

        exc = InvalidTokenException()

        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in exc.detail.lower()


class TestUserNotFoundException:
    """Test UserNotFoundException class."""

    def test_user_not_found_exception(self):
        """Test UserNotFoundException has correct default."""
        from app.core.exceptions import UserNotFoundException

        exc = UserNotFoundException()

        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc.detail.lower()


class TestUserAlreadyExistsException:
    """Test UserAlreadyExistsException class."""

    def test_user_already_exists_exception_default(self):
        """Test UserAlreadyExistsException with default detail."""
        from app.core.exceptions import UserAlreadyExistsException

        exc = UserAlreadyExistsException()

        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in exc.detail.lower()

    def test_user_already_exists_exception_custom(self):
        """Test UserAlreadyExistsException with custom detail."""
        from app.core.exceptions import UserAlreadyExistsException

        exc = UserAlreadyExistsException(detail="Custom user exists error")

        assert exc.detail == "Custom user exists error"


class TestContainerNotFoundException:
    """Test ContainerNotFoundException class."""

    def test_container_not_found_exception(self):
        """Test ContainerNotFoundException has correct detail."""
        from app.core.exceptions import ContainerNotFoundException

        exc = ContainerNotFoundException(container_id="test123")

        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert "test123" in exc.detail


class TestContainerOperationException:
    """Test ContainerOperationException class."""

    def test_container_operation_exception(self):
        """Test ContainerOperationException has correct defaults."""
        from app.core.exceptions import ContainerOperationException

        exc = ContainerOperationException(detail="Container operation failed")

        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.detail == "Container operation failed"


class TestPermissionDeniedException:
    """Test PermissionDeniedException class."""

    def test_permission_denied_exception_default(self):
        """Test PermissionDeniedException with default detail."""
        from app.core.exceptions import PermissionDeniedException

        exc = PermissionDeniedException()

        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert "Permission denied" in exc.detail

    def test_permission_denied_exception_custom(self):
        """Test PermissionDeniedException with custom detail."""
        from app.core.exceptions import PermissionDeniedException

        exc = PermissionDeniedException(detail="Custom permission denied")

        assert exc.detail == "Custom permission denied"


class TestValidationException:
    """Test ValidationException class."""

    def test_validation_exception(self):
        """Test ValidationException has correct defaults."""
        from app.core.exceptions import ValidationException

        exc = ValidationException(detail="Invalid input")

        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert exc.detail == "Invalid input"


class TestRateLimitException:
    """Test RateLimitException class."""

    def test_rate_limit_exception_default(self):
        """Test RateLimitException with default detail."""
        from app.core.exceptions import RateLimitException

        exc = RateLimitException()

        assert exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Rate limit exceeded" in exc.detail
        assert exc.headers == {"Retry-After": "60"}

    def test_rate_limit_exception_custom(self):
        """Test RateLimitException with custom detail."""
        from app.core.exceptions import RateLimitException

        exc = RateLimitException(detail="Custom rate limit")

        assert exc.detail == "Custom rate limit"


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""

    def test_authentication_exception_is_app_exception(self):
        """Test AuthenticationException inherits from AppException."""
        from app.core.exceptions import AppException, AuthenticationException

        exc = AuthenticationException()

        assert isinstance(exc, AppException)
        assert isinstance(exc, Exception)

    def test_validation_exception_is_app_exception(self):
        """Test ValidationException inherits from AppException."""
        from app.core.exceptions import AppException, ValidationException

        exc = ValidationException(detail="Error")

        assert isinstance(exc, AppException)
        assert isinstance(exc, Exception)

    def test_permission_denied_exception_is_app_exception(self):
        """Test PermissionDeniedException inherits from AppException."""
        from app.core.exceptions import AppException, PermissionDeniedException

        exc = PermissionDeniedException()

        assert isinstance(exc, AppException)
        assert isinstance(exc, Exception)


class TestExceptionHTTPExceptionCompatibility:
    """Test exceptions are compatible with FastAPI HTTPException."""

    def test_app_exception_is_http_exception(self):
        """Test AppException inherits from HTTPException."""
        from fastapi import HTTPException

        from app.core.exceptions import AppException

        exc = AppException()

        assert isinstance(exc, HTTPException)

    def test_authentication_exception_has_www_authenticate_header(self):
        """Test AuthenticationException has WWW-Authenticate header."""
        from app.core.exceptions import AuthenticationException

        exc = AuthenticationException()

        assert "WWW-Authenticate" in exc.headers
        assert exc.headers["WWW-Authenticate"] == "Bearer"
