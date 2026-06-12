from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # App
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "analyzer_db"
    postgres_user: str = "analyzer_user"
    postgres_password: str

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    # Mitmproxy & Traffic
    mitmproxy_listen_port: int = 8080
    allowed_targets: str = "example.com"
    max_body_size_bytes: int = 1048576
    
    # Storage
    unstructured_pool_dir: str = "./data/unstructured"
    unstructured_ttl_hours: int = 72
    
    # Security
    strict_passive_mode: bool = True

    @property
    def allowed_targets_list(self) -> List[str]:
        return [target.strip() for target in self.allowed_targets.split(",")]

    @property
    def postgres_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

# Instantiate a global settings object
settings = Settings()