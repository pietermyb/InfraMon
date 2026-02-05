"""Test factories for creating test data."""
import factory
from datetime import datetime
from typing import Any


class UserFactory(factory.Factory):
    class Meta:
        model = dict
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj['username']}@example.com")
    hashed_password = factory.LazyFunction(lambda: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4oQyHN4y6tJE9Edy")
    is_active = True
    is_superuser = False
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class ContainerFactory(factory.Factory):
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: f"abc123{n}")
    short_id = factory.LazyAttribute(lambda obj: obj["id"][:12])
    name = factory.Sequence(lambda n: f"container-{n}")
    image = "nginx:latest"
    status = "running"
    image_id = None
    created = factory.LazyFunction(datetime.utcnow)
    ports = {}
    labels = {}
    env = []
    cmd = []
    volumes = []
    network_settings = {}


class ContainerStatsFactory(factory.Factory):
    class Meta:
        model = dict
    
    cpu_usage = factory.Sequence(lambda n: 10.0 + n)
    memory_usage = factory.LazyFunction(lambda: 100000000 + 1000000)
    memory_limit = 536870912
    network_rx = factory.Sequence(lambda n: 1000 * n)
    network_tx = factory.Sequence(lambda n: 2000 * n)
    block_read = factory.Sequence(lambda n: 500 * n)
    block_write = factory.Sequence(lambda n: 300 * n)
    pids = 5
    timestamp = factory.LazyFunction(datetime.utcnow)


class SystemStatsFactory(factory.Factory):
    class Meta:
        model = dict
    
    cpu_usage = factory.Sequence(lambda n: 25.0 + n)
    memory_usage = factory.LazyFunction(lambda: 50.0)
    memory_total = 17179869184
    memory_used = 8589934592
    memory_available = 8589934592
    disk_usage = factory.LazyFunction(lambda: 45.0)
    disk_total = 512000000000
    disk_used = 256000000000
    disk_free = 256000000000
    network_bytes_sent = factory.Sequence(lambda n: 1024 * n)
    network_bytes_recv = factory.Sequence(lambda n: 2048 * n)
    load_average = factory.LazyFunction(lambda: (1.0, 1.5, 2.0))
    boot_time = factory.LazyFunction(lambda: 1672531200)
    timestamp = factory.LazyFunction(datetime.utcnow)


class ContainerGroupFactory(factory.Factory):
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"Group {n}")
    description = factory.LazyAttribute(lambda obj: f"Description for {obj['name']}")
    color = "#3498db"
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class DockerComposeProjectFactory(factory.Factory):
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"project-{n}")
    compose_file_path = factory.LazyAttribute(lambda obj: f"/opt/projects/{obj['name']}/docker-compose.yaml")
    project_name = factory.LazyAttribute(lambda obj: obj["name"])
    services = factory.LazyFunction(lambda: ["web", "redis", "postgres"])
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class AuditLogFactory(factory.Factory):
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n + 1)
    container_id = factory.Sequence(lambda n: f"abc123{n}")
    user_id = factory.Sequence(lambda n: n + 1)
    operation = factory.Iterator(["start", "stop", "restart", "remove", "logs"])
    details = factory.LazyAttribute(lambda obj: f"Performed {obj['operation']} operation")
    timestamp = factory.LazyFunction(datetime.utcnow)
