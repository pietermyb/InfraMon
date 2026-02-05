from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer

from app.db.database import Base


class SystemStats(Base):
    __tablename__ = "system_stats"

    id = Column(Integer, primary_key=True, index=True)
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    memory_total = Column(Float, default=0.0)
    disk_usage = Column(Float, default=0.0)
    disk_total = Column(Float, default=0.0)
    network_rx = Column(Float, default=0.0)
    network_tx = Column(Float, default=0.0)
    load_avg_1m = Column(Float, default=0.0)
    load_avg_5m = Column(Float, default=0.0)
    load_avg_15m = Column(Float, default=0.0)
    uptime = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
