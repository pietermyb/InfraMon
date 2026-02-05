from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class ContainerStats(Base):
    __tablename__ = "container_stats"

    id = Column(Integer, primary_key=True, index=True)
    container_id = Column(Integer, ForeignKey("containers.id"), nullable=False)
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    memory_limit = Column(Float, default=0.0)
    network_rx = Column(Float, default=0.0)
    network_tx = Column(Float, default=0.0)
    block_read = Column(Float, default=0.0)
    block_write = Column(Float, default=0.0)
    pids = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

    container = relationship("Container", back_populates="stats")
