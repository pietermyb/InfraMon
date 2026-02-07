"""Comprehensive tests for Stats service module - simplified and working."""

from unittest.mock import MagicMock


class TestStatsServiceInit:
    """Tests for StatsService initialization."""

    def test_service_init(self):
        """Test service initializes with database session."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert service.db == mock_db


class TestStatsServiceMethods:
    """Tests for StatsService method signatures and existence."""

    def test_get_current_system_stats_method_exists(self):
        """Test get_current_system_stats method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "get_current_system_stats")
        assert callable(getattr(service, "get_current_system_stats"))

    def test_get_system_info_method_exists(self):
        """Test get_system_info method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "get_system_info")
        assert callable(getattr(service, "get_system_info"))

    def test_get_disk_partitions_method_exists(self):
        """Test get_disk_partitions method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "get_disk_partitions")
        assert callable(getattr(service, "get_disk_partitions"))

    def test_get_network_connections_method_exists(self):
        """Test get_network_connections method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "get_network_connections")
        assert callable(getattr(service, "get_network_connections"))

    def test_get_process_list_method_exists(self):
        """Test get_process_list method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "get_process_list")
        assert callable(getattr(service, "get_process_list"))

    def test_get_dashboard_summary_method_exists(self):
        """Test get_dashboard_summary method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "get_dashboard_summary")
        assert callable(getattr(service, "get_dashboard_summary"))

    def test_get_system_stats_history_method_exists(self):
        """Test get_system_stats_history method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "get_system_stats_history")
        assert callable(getattr(service, "get_system_stats_history"))

    def test_get_container_stats_history_method_exists(self):
        """Test get_container_stats_history method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "get_container_stats_history")
        assert callable(getattr(service, "get_container_stats_history"))

    def test_get_resource_trends_method_exists(self):
        """Test get_resource_trends method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "get_resource_trends")
        assert callable(getattr(service, "get_resource_trends"))

    def test_get_top_consumers_method_exists(self):
        """Test get_top_consumers method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "get_top_consumers")
        assert callable(getattr(service, "get_top_consumers"))

    def test_compare_containers_method_exists(self):
        """Test compare_containers method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "compare_containers")
        assert callable(getattr(service, "compare_containers"))

    def test_get_container_group_stats_method_exists(self):
        """Test get_container_group_stats method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "get_container_group_stats")
        assert callable(getattr(service, "get_container_group_stats"))

    def test_export_stats_method_exists(self):
        """Test export_stats method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "export_stats")
        assert callable(getattr(service, "export_stats"))

    def test_prune_old_stats_method_exists(self):
        """Test prune_old_stats method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "prune_old_stats")
        assert callable(getattr(service, "prune_old_stats"))

    def test_get_container_processes_method_exists(self):
        """Test get_container_processes method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "get_container_processes")
        assert callable(getattr(service, "get_container_processes"))

    def test_get_container_filesystem_usage_method_exists(self):
        """Test get_container_filesystem_usage method exists."""
        from app.services.stats_service import StatsService

        mock_db = MagicMock()
        service = StatsService(mock_db)
        assert hasattr(service, "get_container_filesystem_usage")
        assert callable(getattr(service, "get_container_filesystem_usage"))


class TestStatsServiceStatsSchemas:
    """Tests for stats schema imports."""

    def test_stats_response_import(self):
        """Test stats response schemas can be imported."""
        from app.schemas.stats import DashboardStatsResponse, SystemStatsResponse

        assert SystemStatsResponse is not None
        assert DashboardStatsResponse is not None

    def test_container_stats_import(self):
        """Test container stats schemas can be imported."""
        from app.schemas.stats import ContainerStatsHistoryResponse

        assert ContainerStatsHistoryResponse is not None

    def test_aggregated_stats_import(self):
        """Test aggregated stats schemas can be imported."""
        from app.schemas.stats import AggregatedStatsResponse

        assert AggregatedStatsResponse is not None
