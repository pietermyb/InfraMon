from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from app.db.database import Base
from datetime import datetime


class DockerComposeProject(Base):
    __tablename__ = "docker_compose_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(100), nullable=False)
    compose_file_path = Column(String(500), nullable=False)
    services = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
