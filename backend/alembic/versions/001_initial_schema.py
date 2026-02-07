"""Initial database schema

Revision ID: 001
Revises: 000000000000
Create Date: 2026-02-05

"""

import sqlalchemy as sa

from alembic import op

revision = "001"
down_revision = "000000000000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    # Create container_groups table
    op.create_table(
        "container_groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("color", sa.String(7), nullable=False, default="#3B82F6"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_container_groups_id", "container_groups", ["id"], unique=False)
    op.create_index("ix_container_groups_name", "container_groups", ["name"], unique=True)

    # Create containers table
    op.create_table(
        "containers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("container_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("image", sa.String(500), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, default="unknown"),
        sa.Column("group_id", sa.Integer(), nullable=True),
        sa.Column("docker_compose_path", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["container_groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("container_id"),
    )
    op.create_index("ix_containers_container_id", "containers", ["container_id"], unique=True)
    op.create_index("ix_containers_group_id", "containers", ["group_id"], unique=False)
    op.create_index("ix_containers_id", "containers", ["id"], unique=False)
    op.create_index("ix_containers_name", "containers", ["name"], unique=False)
    op.create_index("ix_containers_status", "containers", ["status"], unique=False)

    # Create docker_compose_projects table
    op.create_table(
        "docker_compose_projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_name", sa.String(100), nullable=False),
        sa.Column("compose_file_path", sa.String(500), nullable=False),
        sa.Column("services", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_docker_compose_projects_id", "docker_compose_projects", ["id"], unique=False
    )
    op.create_index(
        "ix_docker_compose_projects_project_name",
        "docker_compose_projects",
        ["project_name"],
        unique=False,
    )

    # Create container_stats table
    op.create_table(
        "container_stats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("container_id", sa.Integer(), nullable=False),
        sa.Column("cpu_usage", sa.Float(), nullable=False, default=0.0),
        sa.Column("memory_usage", sa.Float(), nullable=False, default=0.0),
        sa.Column("memory_limit", sa.Float(), nullable=False, default=0.0),
        sa.Column("network_rx", sa.Float(), nullable=False, default=0.0),
        sa.Column("network_tx", sa.Float(), nullable=False, default=0.0),
        sa.Column("block_read", sa.Float(), nullable=False, default=0.0),
        sa.Column("block_write", sa.Float(), nullable=False, default=0.0),
        sa.Column("pids", sa.Integer(), nullable=False, default=0),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["container_id"], ["containers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_container_stats_container_id", "container_stats", ["container_id"], unique=False
    )
    op.create_index("ix_container_stats_id", "container_stats", ["id"], unique=False)
    op.create_index("ix_container_stats_timestamp", "container_stats", ["timestamp"], unique=False)

    # Create system_stats table
    op.create_table(
        "system_stats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cpu_usage", sa.Float(), nullable=False, default=0.0),
        sa.Column("memory_usage", sa.Float(), nullable=False, default=0.0),
        sa.Column("memory_total", sa.Float(), nullable=False, default=0.0),
        sa.Column("disk_usage", sa.Float(), nullable=False, default=0.0),
        sa.Column("disk_total", sa.Float(), nullable=False, default=0.0),
        sa.Column("network_rx", sa.Float(), nullable=False, default=0.0),
        sa.Column("network_tx", sa.Float(), nullable=False, default=0.0),
        sa.Column("load_avg_1m", sa.Float(), nullable=False, default=0.0),
        sa.Column("load_avg_5m", sa.Float(), nullable=False, default=0.0),
        sa.Column("load_avg_15m", sa.Float(), nullable=False, default=0.0),
        sa.Column("uptime", sa.Float(), nullable=False, default=0.0),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_system_stats_id", "system_stats", ["id"], unique=False)
    op.create_index("ix_system_stats_timestamp", "system_stats", ["timestamp"], unique=False)

    # Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("container_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("operation", sa.String(100), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("success", sa.Integer(), nullable=False, default=1),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["container_id"], ["containers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_container_id", "audit_logs", ["container_id"], unique=False)
    op.create_index("ix_audit_logs_id", "audit_logs", ["id"], unique=False)
    op.create_index("ix_audit_logs_operation", "audit_logs", ["operation"], unique=False)
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"], unique=False)
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_logs_user_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_timestamp", table_name="audit_logs")
    op.drop_index("ix_audit_logs_operation", table_name="audit_logs")
    op.drop_index("ix_audit_logs_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_container_id", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_system_stats_timestamp", table_name="system_stats")
    op.drop_index("ix_system_stats_id", table_name="system_stats")
    op.drop_table("system_stats")

    op.drop_index("ix_container_stats_timestamp", table_name="container_stats")
    op.drop_index("ix_container_stats_id", table_name="container_stats")
    op.drop_index("ix_container_stats_container_id", table_name="container_stats")
    op.drop_table("container_stats")

    op.drop_index("ix_docker_compose_projects_project_name", table_name="docker_compose_projects")
    op.drop_index("ix_docker_compose_projects_id", table_name="docker_compose_projects")
    op.drop_table("docker_compose_projects")

    op.drop_index("ix_containers_status", table_name="containers")
    op.drop_index("ix_containers_name", table_name="containers")
    op.drop_index("ix_containers_id", table_name="containers")
    op.drop_index("ix_containers_group_id", table_name="containers")
    op.drop_index("ix_containers_container_id", table_name="containers")
    op.drop_table("containers")

    op.drop_index("ix_container_groups_name", table_name="container_groups")
    op.drop_index("ix_container_groups_id", table_name="container_groups")
    op.drop_table("container_groups")

    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
