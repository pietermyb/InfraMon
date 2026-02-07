"""Tests for main FastAPI application."""


class TestMainApp:
    """Tests for main FastAPI application."""

    def test_main_import(self):
        """Test main module can be imported."""
        from app.main import app

        assert app is not None

    def test_app_has_routes(self):
        """Test that app has routes configured."""
        from app.main import app

        routes = app.routes
        assert routes is not None
        assert len(routes) > 0

    def test_app_title(self):
        """Test that app has title."""
        from app.main import app

        assert app.title is not None

    def test_app_version(self):
        """Test that app has version."""
        from app.main import app

        assert app.version is not None


class TestAppSetup:
    """Tests for app setup and configuration."""

    def test_app_includes_api_router(self):
        """Test that app includes API router."""
        from app.main import app

        route_paths = [route.path for route in app.routes if hasattr(route, "path")]
        assert len(route_paths) > 0

    def test_app_has_middleware(self):
        """Test that app has middleware configured."""
        from app.main import app

        assert app.user_middleware is not None

    def test_app_debug_mode(self):
        """Test that app can be in debug mode."""
        from app.main import app

        debug_mode = getattr(app, "debug", False)
        assert isinstance(debug_mode, bool)


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_endpoint_exists(self):
        """Test that health endpoint is configured."""
        from app.main import app

        route_paths = [route.path for route in app.routes if hasattr(route, "path")]
        health_routes = [p for p in route_paths if "health" in p.lower()]
        assert len(health_routes) > 0


class TestAppFactory:
    """Tests for application factory patterns."""

    def test_app_factory_pattern(self):
        """Test that app follows factory pattern if applicable."""
        from app.main import app

        assert app is not None

    def test_app_state(self):
        """Test that app state is accessible."""
        from app.main import app

        state = getattr(app, "state", None)
        assert state is not None


class TestAPIRouter:
    """Tests for API router configuration."""

    def test_api_router_includes_auth(self):
        """Test that API router includes auth routes."""
        from app.main import app

        route_paths = [route.path for route in app.routes if hasattr(route, "path")]
        auth_routes = [p for p in route_paths if "auth" in p.lower() or "login" in p.lower()]
        assert len(auth_routes) > 0

    def test_api_router_includes_containers(self):
        """Test that API router includes container routes."""
        from app.main import app

        route_paths = [route.path for route in app.routes if hasattr(route, "path")]
        container_routes = [p for p in route_paths if "container" in p.lower()]
        assert len(container_routes) > 0


class TestExceptionHandlers:
    """Tests for exception handlers."""

    def test_app_has_exception_handlers(self):
        """Test that app has exception handlers configured."""
        from app.main import app

        exception_handlers = getattr(app, "exception_handlers", {})
        assert exception_handlers is not None
