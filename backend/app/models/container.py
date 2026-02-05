from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime


class Container(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True, index=True)
    container_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    image = Column(String(500), nullable=False)
    status = Column(String(50), default="unknown")
    group_id = Column(Integer, ForeignKey("container_groups.id"), nullable=True)
    docker_compose_path = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    group = relationship("ContainerGroup", back_populates="containers")
    stats = relationship("ContainerStats", back_populates="container", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="container")
