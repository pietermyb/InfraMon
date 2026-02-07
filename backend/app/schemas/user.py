"""User schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user model."""

    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr


class UserCreate(UserBase):
    """User creation model."""

    password: str = Field(..., min_length=8, max_length=128)
    password_confirm: str = Field(..., exclude=True)
    is_superuser: bool = False

    @field_validator("password_confirm")
    @classmethod
    def validate_password_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserUpdate(BaseModel):
    """User update model."""

    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserPasswordUpdate(BaseModel):
    """Password update model."""

    current_password: str = Field(...)
    new_password: str = Field(..., min_length=8, max_length=128)
    new_password_confirm: str = Field(..., exclude=True)

    @field_validator("new_password_confirm")
    @classmethod
    def validate_password_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class UserResponse(UserBase):
    """User response model."""

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """User list response with pagination."""

    users: list[UserResponse]
    total: int
    page: int
    page_size: int


class UserLogin(BaseModel):
    """User login model."""

    username: str
    password: str


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str
    user_id: Optional[int] = None
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None
    type: str = "access"


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""

    refresh_token: str


class LoginResponse(BaseModel):
    """Login response with tokens."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class LogoutResponse(BaseModel):
    """Logout response."""

    message: str = "Successfully logged out"


class TokenRefreshResponse(BaseModel):
    """Token refresh response."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class CurrentUserResponse(BaseModel):
    """Current authenticated user response."""

    user: UserResponse
    permissions: list[str] = []
