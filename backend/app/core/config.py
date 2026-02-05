from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "InfraMon"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8065
    API_V1_PREFIX: str = "/api/v1"
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./inframon.db"
    DATABASE_ECHO: bool = False
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://192.168.2.95:9876"]
    
    DOCKER_SOCKET_PATH: str = "/var/run/docker.sock"
    DOCKER_API_VERSION: str = "1.45"
    PODMAN_SOCKET_PATH: str = "/run/user/0/podman/podman.sock"
    COLIMA_SOCKET_PATH: str = "/run/colima/socket/docker.sock"
    CONTAINER_RUNTIME: str = "auto"  # Options: "auto", "docker", "podman", "colima"
    
    LOG_LEVEL: str = "INFO"
    
    ADMIN_USERNAME: str = "admin"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = ""
    
    HOST_FS_ROOT: str = ""
    
    class Config:
        env_file = Path(__file__).parent.parent.parent / ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
