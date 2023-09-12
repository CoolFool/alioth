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
    for collection in collections.collections:
        """The collection on each host will be different as qdrant replicates the collection across. So, if at the time
        of creating the snapshot the host that is behind a load balancer doesn't have the latest collection it will take snapshot of a older one from some other node and store it there. 
        So, we go one by one to all the hosts and create a collection snapshot for each one of them. That way when we recover the collection on a particular
        host, the collection state on the host will be reset to exactly the way it was at the time of backup.
        This ofcourse won't be required if the replication factor and write_consistency_factor for the collection is set in a way that collection or the records
        in a collection is only accepted if it is replicated across all the nodes."""
        for host in hosts.hosts:
            client = QdrantClient(
                host=host.host,
                port=host.port,
                grpc_port=host.grpc_port,
                prefer_grpc=True,
            )
            try:
                snapshot = client.create_snapshot(collection_name=collection)
            except RpcError as rpc_error:
                if rpc_error.code() == StatusCode.NOT_FOUND:
                    logger.warn(
                        f"{collection} replica not found on host {client._client._host}"
                    )
                    return
                logger.exception(rpc_error)
            snapshot_url = f"http://{host.host}:{host.port}/collections/{collection}/snapshots/{snapshot.name}"
            if (
                verify_collection_snapshot(snapshot_url=snapshot_url)
                and snapshot_url != ""
            ):
                logger.info(
                    f"{collection} snapshot {snapshot.name} found on host {host.host}"
                )
                threads.append(
                    Thread(
                        target=backup_collection_handler,
                        args=(client, collection, snapshot),
                    )
                )
                threads[-1].start()
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
