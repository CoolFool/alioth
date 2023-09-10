import logging

from fastapi import APIRouter

from app.routers.schemas import IngestionBatch, Collections, Hosts, RestoreCollection, StandardResponse, HomePageResponse
from app.tasks.ingestion import ingest
from app.tasks.backup import backup_collection, backup_storage
from app.tasks.restore import restore_collection

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/alioth",
    tags=["alioth"],
)


@router.get("/",response_model=HomePageResponse)
def home():
    return HomePageResponse()


@router.post("/ingest", response_model=StandardResponse)
def ingest_handler(batch: IngestionBatch):
    try:
        ingest.delay(batch.model_dump())
        return StandardResponse(status_code=200)
    except Exception as e:
        logger.exception(e)
        return StandardResponse(status_code=500)


"""
In distributed mode Qdrant will need the backups from a specific node (for collections as well as storage).
So, we need to create a new client for each Qdrant node.
"""


@router.post("/backup/collection", response_model=StandardResponse)
def collection_snapshot_handler(collections: Collections):
    try:
        backup_collection.delay(collections.model_dump())
        return StandardResponse(status_code=200)
    except Exception as e:
        logger.exception(e)
        return StandardResponse(status_code=500)


@router.post("/backup/storage", response_model=StandardResponse)
def storage_snapshot_handler(hosts: Hosts):
    try:
        backup_storage.delay(hosts.model_dump())
        return StandardResponse(status_code=200)
    except Exception as e:
        logger.exception(e)
        return StandardResponse(status_code=500)


@router.post("/restore/collection", response_model=StandardResponse)
def restore_collection_handler(collection: RestoreCollection):
    try:
        restore_collection.delay(collection.model_dump())
        return StandardResponse(status_code=200)
    except Exception as e:
        logger.exception(e)
        return StandardResponse(status_code=500)
