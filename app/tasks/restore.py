# ref: https://qdrant.tech/documentation/concepts/snapshots/

from app.routers.schemas import RestoreCollection
from app.tasks.celery_app import app
from app.tasks.utils import restore_collection_handler

"""
In distributed mode, full storage recovery can't be performed using the API. Only collection restoration is supported
"""


@app.task()
def restore_collection(collection):
    collection = RestoreCollection(**collection)
    restoration = restore_collection_handler(
        host=collection.host,
        collection_name=collection.collection_name,
        snapshot_url=collection.snapshot_url,
    )
    return restoration
