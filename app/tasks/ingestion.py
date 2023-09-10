# ref: https://qdrant.tech/documentation/concepts/points/
import logging

from qdrant_client import QdrantClient

from app.tasks.celery_app import app
from app.settings import settings
from app.routers.schemas import IngestionBatch
from grpc import RpcError, StatusCode


logger = logging.getLogger(__name__)


@app.task()
def ingest(batch):
    client = QdrantClient(
        host=settings.QDRANT_DB_HOST,
        port=settings.QDRANT_DB_PORT,
        grpc_port=settings.QDRANT_DB_GRPC_PORT,
        prefer_grpc=True,
    )
    batch = IngestionBatch(**batch)
    try:
        client.get_collection(collection_name=batch.collection_name)
        add_record = client.upsert(
            collection_name=batch.collection_name, points=batch.batch, wait=True
        )
        return add_record.model_dump()
    except RpcError as rpc_error:
        if rpc_error.code() == StatusCode.NOT_FOUND:
            logger.warn(rpc_error.details())
            return
        logger.exception(rpc_error)
