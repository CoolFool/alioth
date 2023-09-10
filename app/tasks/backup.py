# ref: https://qdrant.tech/documentation/concepts/snapshots/
from threading import Thread
import logging

from qdrant_client import QdrantClient
from grpc import RpcError, StatusCode

from app.tasks.celery_app import app
from app.settings import settings
from app.routers.schemas import Collections, Hosts
from app.tasks.utils import (
    backup_collection_handler,
    backup_storage_handler,
    verify_collection_snapshot,
    get_hosts_for_backup,
)

logger = logging.getLogger(__name__)


@app.task()
def backup_collection(collections):
    collections = Collections(**collections)
    threads = []
    snapshot_url = ""
    hosts = get_hosts_for_backup()
    hosts = Hosts(**hosts)
    client = QdrantClient(
        host=settings.QDRANT_DB_HOST,
        port=settings.QDRANT_DB_PORT,
        grpc_port=settings.QDRANT_DB_GRPC_PORT,
        prefer_grpc=True,
    )
    for collection in collections.collections:
        try:
            snapshot = client.create_snapshot(collection_name=collection)
        except RpcError as rpc_error:
            if rpc_error.code() == StatusCode.NOT_FOUND:
                logger.warn(
                    f"{collection} replica not found on host {client._client._host}"
                )
                return
            logger.exception(rpc_error)
        """
        Qdrant doesn't give the qdrant-node (OR) hosts that actually has the collection snapshot.
        So when you send a request for creating a collection snapshot to the qdrant service endpoint it will succesfully create the snapshot but 
        when you request the snapshot from the service it will hit any one of the qdrant-node and if it doesn't contain the snapshot,
        it will give a 404 and backup operation will fail.
        To fix this, we check every hosts to see if it contains the snapshot and once the right host is found we process it further.
        """
        for host in hosts.hosts:
            snapshot_url = f"http://{host.host}:{host.port}/collections/{collection}/snapshots/{snapshot.name}"
            if (
                verify_collection_snapshot(snapshot_url=snapshot_url)
                and snapshot_url != ""
            ):
                logger.info(
                    f"{collection} snapshot {snapshot.name} found on host {host.host}"
                )
                client_with_snapshot = QdrantClient(
                    host=host.host,
                    port=host.port,
                    grpc_port=host.grpc_port,
                    prefer_grpc=True,
                )
                threads.append(
                    Thread(
                        target=backup_collection_handler,
                        args=(client_with_snapshot, collection, snapshot),
                    )
                )
                threads[-1].start()
                break
            else:
                logger.warn(
                    f"{collection} snapshot {snapshot.name} not found on host {host.host}"
                )
    for thread in threads:
        thread.join()


@app.task()
def backup_storage(hosts):
    hosts = Hosts(**hosts)
    threads = []
    for host in hosts.hosts:
        threads.append(Thread(target=backup_storage_handler, args=(host,)))
        threads[-1].start()
    for thread in threads:
        thread.join()
