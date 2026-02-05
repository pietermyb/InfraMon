import logging
import re
import time
from datetime import datetime, timedelta
from typing import Callable, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")
ALGORITHM = settings.ALGORITHM

RATE_LIMIT_STORE: dict[str, list[float]] = {}
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX_REQUESTS = 100

logger = logging.getLogger(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not getattr(current_user, "is_superuser", False):
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
    return current_user


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        if client_ip not in RATE_LIMIT_STORE:
            RATE_LIMIT_STORE[client_ip] = []

        RATE_LIMIT_STORE[client_ip] = [
            t for t in RATE_LIMIT_STORE[client_ip] if t > current_time - self.window_seconds
        ]

        if len(RATE_LIMIT_STORE[client_ip]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": self.window_seconds,
                },
                headers={"Retry-After": str(self.window_seconds)},
            )

        RATE_LIMIT_STORE[client_ip].append(current_time)
        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        response = await call_next(request)

        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }

        for header, value in security_headers.items():
            response.headers[header] = value

        return response


class RequestSizeMiddleware(BaseHTTPMiddleware):
    MAX_BODY_SIZE = 10 * 1024 * 1024

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_BODY_SIZE:
            return JSONResponse(
                status_code=413, content={"detail": "Request body too large. Maximum size is 10MB."}
            )
        return await call_next(request)


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    DANGEROUS_PATTERNS = [
        re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"on\w+\s*=", re.IGNORECASE),
        re.compile(r"\.\./"),
        re.compile(r"\x00"),
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode("utf-8", errors="ignore")
                    for pattern in self.DANGEROUS_PATTERNS:
                        if pattern.search(body_str):
                            logger.warning(f"Dangerous input from {request.client.host}")
                            return JSONResponse(
                                status_code=400, content={"detail": "Invalid input detected."}
                            )
                    request._body = body
            except Exception:
                pass

        return await call_next(request)


def get_rate_limit_stats() -> dict:
    return {
        "active_ips": len(RATE_LIMIT_STORE),
        "window_seconds": RATE_LIMIT_WINDOW,
        "max_requests": RATE_LIMIT_MAX_REQUESTS,
    }


def clear_rate_limit_store():
    RATE_LIMIT_STORE.clear()
