"""Test factories for creating test data."""

from datetime import datetime
from typing import Any


class UserFactory:
    @staticmethod
    def create(
        username="testuser", email="test@example.com", is_active=True, is_superuser=False, **kwargs
    ):
        return {
            "username": username,
            "email": email,
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4oQyHN4y6tJE9Edy",
            "is_active": is_active,
            "is_superuser": is_superuser,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            **kwargs,
        }


class ContainerFactory:
    @staticmethod
    def create(
        id="abc123", name="test-container", image="nginx:latest", status="running", **kwargs
    ):
        return {
            "id": id,
            "short_id": id[:12],
            "name": name,
            "image": image,
            "status": status,
            "image_id": None,
            "created": datetime.utcnow().isoformat(),
            "ports": {},
            "labels": {},
            "env": [],
            "cmd": [],
            "volumes": [],
            "network_settings": {},
            **kwargs,
        }


class ContainerGroupFactory:
    @staticmethod
    def create(id=1, name="Test Group", color="#3498db", **kwargs):
        return {
            "id": id,
            "name": name,
            "description": f"Description for {name}",
            "color": color,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            **kwargs,
        }


class SystemStatsFactory:
    @staticmethod
    def create(cpu_usage=25.0, memory_usage=50.0, disk_usage=45.0, **kwargs):
        return {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "memory_total": 17179869184,
            "memory_used": 8589934592,
            "memory_available": 8589934592,
            "disk_usage": disk_usage,
            "disk_total": 512000000000,
            "disk_used": 256000000000,
            "disk_free": 256000000000,
            "network_bytes_sent": 1024,
            "network_bytes_recv": 2048,
            "load_average": [1.0, 1.5, 2.0],
            "boot_time": 1672531200,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs,
        }
