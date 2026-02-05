"""Unit tests for core auth module."""

from datetime import timedelta


class TestPasswordHashing:
    """Test password hashing functions."""

    def test_password_hash_not_plaintext(self):
        """Test that password hash is not plaintext."""
        from app.core.auth import get_password_hash

        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 50

    def test_password_verify_correct(self):
        """Test password verification with correct password."""
        from app.core.auth import get_password_hash, verify_password

        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_verify_incorrect(self):
        """Test password verification with wrong password."""
        from app.core.auth import get_password_hash, verify_password

        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password("wrongpassword", hashed) is False

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        from app.core.auth import get_password_hash

        hash1 = get_password_hash("password1")
        hash2 = get_password_hash("password2")

        assert hash1 != hash2


class TestTokenBlacklist:
    """Test token blacklist functionality."""

    def test_blacklist_token(self):
        """Test adding token to blacklist."""
        from app.core.auth import blacklist_token, token_blacklist

        token = "test_token_to_blacklist"
        blacklist_token(token)

        assert token_blacklist.is_blacklisted(token) is True

    def test_blacklist_multiple_tokens(self):
        """Test adding multiple tokens to blacklist."""
        from app.core.auth import blacklist_token, token_blacklist

        token1 = "token1"
        token2 = "token2"

        blacklist_token(token1)
        blacklist_token(token2)

        assert token_blacklist.is_blacklisted(token1) is True
        assert token_blacklist.is_blacklisted(token2) is True


class TestTokenDecoding:
    """Test token decoding functions."""

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        from app.core.auth import create_access_token, decode_token

        data = {"sub": "testuser", "user_id": 123}
        token = create_access_token(data)

        decoded = decode_token(token)

        assert decoded is not None
        assert decoded.get("sub") == "testuser"
        assert decoded.get("user_id") == 123
        assert decoded.get("type") == "access"

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        from app.core.auth import decode_token

        decoded = decode_token("invalid_token")

        assert decoded is None

    def test_decode_expired_token(self):
        """Test decoding an expired token returns None."""
        from app.core.auth import create_access_token, decode_token

        # Create a token that expires immediately
        data = {"sub": "testuser", "user_id": 123}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        decoded = decode_token(token)

        assert decoded is None


class TestTokenCreation:
    """Test token creation functions."""

    def test_create_access_token(self):
        """Test access token creation."""
        from app.core.auth import create_access_token

        data = {"sub": "testuser", "user_id": 123}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 100

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        from app.core.auth import create_refresh_token

        data = {"sub": "testuser", "user_id": 123}
        token = create_refresh_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 100

    def test_create_access_token_with_custom_expiry(self):
        """Test access token creation with custom expiry."""
        from app.core.auth import create_access_token

        data = {"sub": "testuser", "user_id": 123}
        token = create_access_token(data, expires_delta=timedelta(hours=2))

        assert token is not None
        assert isinstance(token, str)

    def test_access_token_has_correct_type(self):
        """Test access token has correct type claim."""
        from app.core.auth import create_access_token, decode_token

        token = create_access_token(data={"sub": "testuser"})
        decoded = decode_token(token)

        assert decoded is not None
        assert decoded.get("type") == "access"

    def test_refresh_token_has_correct_type(self):
        """Test refresh token has correct type claim."""
        from app.core.auth import create_refresh_token, decode_token

        token = create_refresh_token(data={"sub": "testuser"})
        decoded = decode_token(token)

        assert decoded is not None
        assert decoded.get("type") == "refresh"


class TestCreateTokensForUser:
    """Test create_tokens_for_user function."""

    def test_create_tokens_for_user_structure(self):
        """Test creating tokens for a user has correct structure."""
        from unittest.mock import MagicMock

        from app.core.auth import create_tokens_for_user
        from app.models.user import User

        # Create a mock user
        mock_user = MagicMock(spec=User)
        mock_user.username = "testuser"
        mock_user.id = 1

        tokens = create_tokens_for_user(mock_user)

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        assert "expires_in" in tokens


class TestTokenExpiry:
    """Test token expiry functionality."""

    def test_access_token_expiry_time(self):
        """Test access token has correct expiry time."""
        from app.core.auth import create_access_token, decode_token

        data = {"sub": "testuser"}
        token = create_access_token(data, expires_delta=timedelta(minutes=30))
        decoded = decode_token(token)

        assert decoded is not None
        expiry_time = decoded.get("exp")
        assert expiry_time is not None

        import time

        current_time = time.time()

        # Token should expire in approximately 30 minutes
        assert 29 * 60 < expiry_time - current_time < 31 * 60

    def test_refresh_token_expiry_time(self):
        """Test refresh token has correct expiry time."""
        from app.core.auth import create_refresh_token, decode_token

        data = {"sub": "testuser"}
        token = create_refresh_token(data)
        decoded = decode_token(token)

        assert decoded is not None
        expiry_time = decoded.get("exp")
        assert expiry_time is not None

        import time

        current_time = time.time()

        # Refresh token expires in 7 days by default
        assert 6 * 24 * 60 * 60 < expiry_time - current_time < 8 * 24 * 60 * 60


class TestTokenBlacklistExpiration:
    """Test token blacklist expiration handling."""

    def test_remove_expired_tokens_method_exists(self):
        """Test removing expired tokens from blacklist method exists."""
        from app.core.auth import token_blacklist

        # Verify the method exists and is callable
        assert hasattr(token_blacklist, "remove_expired")
        assert callable(token_blacklist.remove_expired)


class TestPasswordHashingExtended:
    """Extended password hashing tests."""

    def test_password_hash_uses_bcrypt(self):
        """Test that password hashing uses bcrypt algorithm."""
        from app.core.auth import get_password_hash

        password = "testpassword123"
        hashed = get_password_hash(password)

        # Bcrypt hashes start with $2b$ or $2y$
        assert hashed.startswith("$2b$") or hashed.startswith("$2y$")

    def test_password_hash_is_deterministic_but_with_salt(self):
        """Test that same password produces different hashes (due to salt)."""
        from app.core.auth import get_password_hash

        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Different due to salt
        assert hash1 != hash2

        # But both verify correctly
        from app.core.auth import verify_password

        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestSettings:
    """Test configuration settings."""

    def test_settings_import(self):
        """Test settings can be imported."""
        from app.core.config import settings

        assert settings is not None

    def test_database_url_configured(self):
        """Test database URL is configured."""
        from app.core.config import settings

        assert settings.DATABASE_URL is not None
        assert (
            "sqlite" in settings.DATABASE_URL.lower()
            or "postgresql" in settings.DATABASE_URL.lower()
        )

    def test_secret_key_configured(self):
        """Test secret key is configured."""
        from app.core.config import settings

        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) > 0

    def test_access_token_expire_minutes(self):
        """Test access token expiration is configured."""
        from app.core.config import settings

        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES is not None
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
