import os.path
from pathlib import Path
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(Path(__file__).parent.resolve())


class Settings(BaseSettings):
    """Application settings."""

    ENV: str = "dev"
    HOST: str = "0.0.0.0"
    PORT: int = 1337
    BASE_URL_: str = f"https://{HOST}:{PORT}"
    # quantity of workers for uvicorn
    WORKERS_COUNT: int = 1
    # Enable uvicorn reloading
    RELOAD: bool = False
    BASE_DIR: str = os.path.dirname(Path(__file__).parent.resolve())
    ALIOTH_APP_VERSION: str = os.getenv("ALIOTH_APP_VERSION", "latest")

    BACKUP_SCHEDULE: int = os.getenv("BACKUP_SCHEDULE", 3600)

    QDRANT_DB_HOST: str = os.getenv("QDRANT_DB_HOST", "localhost")
    QDRANT_DB_PORT: int = os.getenv("QDRANT_DB_PORT", 6333)
    QDRANT_DB_GRPC_PORT: int = os.getenv("QDRANT_DB_GRPC_PORT", 6334)
    QDRANT_DB_PROTO: str = os.getenv("QDRANT_DB_PROTO", "http")

    BROKER_PROTO: str = os.getenv("BROKER_PROTO", "amqp")
    BROKER_HOST: str = os.getenv("BROKER_HOST", "localhost")
    BROKER_PORT: int = os.getenv("BROKER_PORT", 5672)
    BROKER_USER: str = os.getenv("BROKER_USER", "guest")
    BROKER_PASS: str = os.getenv("BROKER_PASS", "guest")

    AWS_ACCESS_KEY: str = os.getenv("AWS_ACCESS_KEY", "admin")
    AWS_SECRET_KEY: str = os.getenv("AWS_SECRET_KEY", "supersecret")
    AWS_ENDPOINT_URL: str = os.getenv("AWS_ENDPOINT_URL", "http://127.0.0.1:9000")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "alioth")

    QDRANT_DB_HOSTS_JSON_PATH: str = os.getenv(
        "QDRANT_DB_HOSTS_JSON_PATH", f"{BASE_DIR}/config/hosts.json"
    )
    QDRANT_DB_COLLECTIONS_JSON_PATH: str = os.getenv(
        "QDRANT_DB_COLLECTIONS_JSON_PATH", f"{BASE_DIR}/config/collections.json"
    )

    ALIOTH_HOST: str = os.getenv("ALIOTH_HOST", "0.0.0.0")
    ALIOTH_PORT: int = os.getenv("ALIOTH_PORT", 1337)

    GUNICORN_WORKERS: int = os.getenv("GUNICORN_WORKERS", 4)

    @property
    def BASE_URL(self) -> str:
        return self.BASE_URL_ if self.BASE_URL_.endswith("/") else f"{self.BASE_URL_}/"

    model_config = SettingsConfigDict(
        env_file=".env", extra="allow", case_sensitive=True
    )


settings = Settings()
