from pydantic import BaseModel
from qdrant_client.models import Batch
from app.settings import settings


class IngestionBatch(BaseModel):
    collection_name: str
    batch: Batch


class QdrantHost(BaseModel):
    port: int = (6333,)
    grpc_port: int = (6334,)
    prefer_grpc: bool = (True,)
    host: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "port": "6333",
                "grpc_port": "6334",
                "prefer_grpc": "true",
                "host": "localhost",
            }
        }


class Collections(BaseModel):
    collections: list


class Hosts(BaseModel):
    hosts: list[QdrantHost]


class RestoreCollection(BaseModel):
    collection_name: str
    host: QdrantHost
    snapshot_url: str | None = None


class StandardResponse(BaseModel):
    status_code: int


class HomePageResponse(BaseModel):
    name: str = "Alioth"
    description: str = "Ingest data at scale into a Qdrant DB Cluster"
    version: str = settings.ALIOTH_APP_VERSION
