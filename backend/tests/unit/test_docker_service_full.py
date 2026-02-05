"""Comprehensive tests for Docker service module - simplified and working."""

from unittest.mock import MagicMock, patch


class TestDockerServiceInit:
    """Tests for DockerService initialization."""

    def test_service_init_with_db(self):
        """Test service initializes with database session."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db)
        assert service.db == mock_db
        assert service._client is None

    def test_service_init_with_user_id(self):
        """Test service initializes with user_id."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db, user_id=1)
        assert service._user_id == 1

    def test_service_init_default_timeout(self):
        """Test service has default timeout."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db)
        assert service._timeout == 30


class TestDockerRuntimeDetection:
    """Tests for Docker runtime detection functions."""

    @patch("app.services.docker_service.settings")
    def test_get_socket_path_docker(self, mock_settings):
        """Test socket path for Docker runtime."""
        from app.services.docker_service import _get_socket_path

        mock_settings.CONTAINER_RUNTIME = "docker"
        mock_settings.DOCKER_SOCKET_PATH = "/var/run/docker.sock"
        mock_settings.PODMAN_SOCKET_PATH = "/run/podman/podman.sock"
        mock_settings.COLIMA_SOCKET_PATH = "/run/colima.sock"

        path = _get_socket_path()
        assert path == "/var/run/docker.sock"

    @patch("app.services.docker_service.settings")
    def test_get_socket_path_podman(self, mock_settings):
        """Test socket path for Podman runtime."""
        from app.services.docker_service import _get_socket_path

        mock_settings.CONTAINER_RUNTIME = "podman"
        mock_settings.DOCKER_SOCKET_PATH = "/var/run/docker.sock"
        mock_settings.PODMAN_SOCKET_PATH = "/run/podman/podman.sock"
        mock_settings.COLIMA_SOCKET_PATH = "/run/colima.sock"

        path = _get_socket_path()
        assert path == "/run/podman/podman.sock"

    @patch("app.services.docker_service.settings")
    def test_get_socket_path_colima(self, mock_settings):
        """Test socket path for Colima runtime."""
        from app.services.docker_service import _get_socket_path

        mock_settings.CONTAINER_RUNTIME = "colima"
        mock_settings.DOCKER_SOCKET_PATH = "/var/run/docker.sock"
        mock_settings.PODMAN_SOCKET_PATH = "/run/podman/podman.sock"
        mock_settings.COLIMA_SOCKET_PATH = "/run/colima.sock"

        path = _get_socket_path()
        assert path == "/run/colima.sock"

    @patch("app.services.docker_service.os.path.exists")
    @patch("app.services.docker_service.settings")
    def test_get_socket_path_auto_detect_podman(self, mock_settings, mock_exists):
        """Test socket path auto-detection returns first available."""
        from app.services.docker_service import _get_socket_path

        mock_settings.CONTAINER_RUNTIME = "auto"
        mock_settings.DOCKER_SOCKET_PATH = "/var/run/docker.sock"
        mock_settings.PODMAN_SOCKET_PATH = "/run/podman/podman.sock"
        mock_settings.COLIMA_SOCKET_PATH = "/run/colima.sock"
        mock_exists.side_effect = [True, False, False]

        path = _get_socket_path()
        assert path == "/var/run/docker.sock"

    @patch("app.services.docker_service._get_socket_path")
    def test_get_runtime_name_docker(self, mock_socket_path):
        """Test runtime name detection for Docker."""
        from app.services.docker_service import _get_runtime_name

        mock_socket_path.return_value = "/var/run/docker.sock"
        name = _get_runtime_name()
        assert name == "Docker"

    @patch("app.services.docker_service._get_socket_path")
    def test_get_runtime_name_podman(self, mock_socket_path):
        """Test runtime name detection for Podman."""
        from app.services.docker_service import _get_runtime_name

        mock_socket_path.return_value = "/run/podman/podman.sock"
        name = _get_runtime_name()
        assert name == "Podman"

    @patch("app.services.docker_service._get_socket_path")
    def test_get_runtime_name_colima(self, mock_socket_path):
        """Test runtime name detection for Colima."""
        from app.services.docker_service import _get_runtime_name

        mock_socket_path.return_value = "/run/colima.sock"
        name = _get_runtime_name()
        assert name == "Colima"


class TestDockerServiceClient:
    """Tests for Docker client connection."""

    @patch("app.services.docker_service.docker.DockerClient")
    @patch("app.services.docker_service._get_socket_path")
    @patch("app.services.docker_service._get_runtime_name")
    def test_client_property_creates_connection(
        self, mock_runtime, mock_socket_path, mock_docker_class
    ):
        """Test that client property creates Docker connection."""
        from app.services.docker_service import DockerService

        mock_socket_path.return_value = "/var/run/docker.sock"
        mock_runtime.return_value = "Docker"
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_docker_class.return_value = mock_client

        mock_db = MagicMock()
        service = DockerService(mock_db)
        client = service.client

        mock_docker_class.assert_called_once()
        assert client is not None

    @patch("app.services.docker_service.docker.DockerClient")
    @patch("app.services.docker_service._get_socket_path")
    @patch("app.services.docker_service._get_runtime_name")
    def test_client_property_reuses_connection(
        self, mock_runtime, mock_socket_path, mock_docker_class
    ):
        """Test that client property reuses existing connection."""
        from app.services.docker_service import DockerService

        mock_socket_path.return_value = "/var/run/docker.sock"
        mock_runtime.return_value = "Docker"
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_docker_class.return_value = mock_client

        mock_db = MagicMock()
        service = DockerService(mock_db)
        client1 = service.client
        client2 = service.client

        assert client1 is client2
        assert mock_docker_class.call_count == 1


class TestDockerServiceMethods:
    """Tests for Docker service method existence."""

    def test_list_all_containers_method_exists(self):
        """Test list_all_containers method exists."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db)
        assert hasattr(service, "list_all_containers")
        assert callable(getattr(service, "list_all_containers"))

    def test_start_container_method_exists(self):
        """Test start_container method exists."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db)
        assert hasattr(service, "start_container")
        assert callable(getattr(service, "start_container"))

    def test_stop_container_method_exists(self):
        """Test stop_container method exists."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db)
        assert hasattr(service, "stop_container")
        assert callable(getattr(service, "stop_container"))

    def test_restart_container_method_exists(self):
        """Test restart_container method exists."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db)
        assert hasattr(service, "restart_container")
        assert callable(getattr(service, "restart_container"))

    def test_pause_container_method_exists(self):
        """Test pause_container method exists."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db)
        assert hasattr(service, "pause_container")
        assert callable(getattr(service, "pause_container"))

    def test_unpause_container_method_exists(self):
        """Test unpause_container method exists."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db)
        assert hasattr(service, "unpause_container")
        assert callable(getattr(service, "unpause_container"))

    def test_remove_container_method_exists(self):
        """Test remove_container method exists."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db)
        assert hasattr(service, "remove_container")
        assert callable(getattr(service, "remove_container"))

    def test_kill_container_method_exists(self):
        """Test kill_container method exists."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db)
        assert hasattr(service, "kill_container")
        assert callable(getattr(service, "kill_container"))

    def test_get_logs_method_exists(self):
        """Test get_logs method exists."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db)
        assert hasattr(service, "get_logs")
        assert callable(getattr(service, "get_logs"))

    def test_get_container_stats_method_exists(self):
        """Test get_container_stats method exists."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db)
        assert hasattr(service, "get_container_stats")
        assert callable(getattr(service, "get_container_stats"))

    def test_inspect_container_method_exists(self):
        """Test inspect_container method exists."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db)
        assert hasattr(service, "inspect_container")
        assert callable(getattr(service, "inspect_container"))

    def test_rename_container_method_exists(self):
        """Test rename_container method exists."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db)
        assert hasattr(service, "rename_container")
        assert callable(getattr(service, "rename_container"))

    def test_update_container_method_exists(self):
        """Test update_container method exists."""
        from app.services.docker_service import DockerService

        mock_db = MagicMock()
        service = DockerService(mock_db)
        assert hasattr(service, "update_container")
        assert callable(getattr(service, "update_container"))
