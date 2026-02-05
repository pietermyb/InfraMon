"""Custom exceptions for the application."""

from typing import Optional

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception."""

    def __init__(
        self,
        detail: str = "An error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers: Optional[dict] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class AuthenticationException(AppException):
    """Authentication related exceptions."""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCredentialsException(AuthenticationException):
    """Invalid username or password."""

    def __init__(self):
        super().__init__(detail="Incorrect username or password")


class TokenExpiredException(AuthenticationException):
    """Token has expired."""

    def __init__(self):
        super().__init__(detail="Token has expired")


class InvalidTokenException(AuthenticationException):
    """Invalid token."""

    def __init__(self):
        super().__init__(detail="Invalid authentication token")


class UserNotFoundException(AppException):
    """User not found."""

    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


class UserAlreadyExistsException(AppException):
    """User already exists."""

    def __init__(self, detail: str = "User already exists"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ContainerNotFoundException(AppException):
    """Container not found."""

    def __init__(self, container_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Container '{container_id}' not found"
        )


class ContainerOperationException(AppException):
    """Container operation failed."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class PermissionDeniedException(AppException):
    """Permission denied."""

    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ValidationException(AppException):
    """Validation error."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class RateLimitException(AppException):
    """Rate limit exceeded."""

    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": "60"},
        )
