import requests
import os
import logging
from pathlib import Path
import json

import boto3
import botocore.errorfactory
from botocore.client import Config
from qdrant_client import QdrantClient

from app.settings import settings
from app.routers.schemas import Hosts, Collections

logger = logging.getLogger(__name__)

boto3_session = boto3.Session()

# Recovery Utils


def get_latest_snapshot(s3, prefix):
    paginator = s3.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=settings.S3_BUCKET_NAME, Prefix=prefix)
    latest = None
    for page in page_iterator:
        if "Contents" in page:
            latest2 = max(page["Contents"], key=lambda x: x["LastModified"])
            if latest is None or latest2["LastModified"] > latest["LastModified"]:
                latest = latest2
    return latest


def get_snapshot_signed_url_from_s3(s3, prefix):
    latest_snapshot = get_latest_snapshot(s3=s3, prefix=prefix)
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": settings.S3_BUCKET_NAME, "Key": latest_snapshot["Key"]},
        ExpiresIn=3600,
    )
    return url


def recover_collection_from_snapshot(host, snapshot_path, collection_name):
    try:
        location = {"location": str(snapshot_path)}
        response = requests.put(
            f"{settings.QDRANT_DB_PROTO}://{host.host}:{host.port}/collections/{collection_name}/snapshots/recover",
            data=json.dumps(location),
            timeout=900,
        )
        return json.loads(response.text)
    except Exception as e:
        logger.exception(e)


def restore_collection_handler(host, collection_name, snapshot_url):
    snapshot_path = snapshot_url
    if snapshot_path is None:
        logger.info("-> Creating S3 Client")
        s3_client = boto3_session.client(
            service_name="s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            endpoint_url=settings.AWS_ENDPOINT_URL,
            config=Config(signature_version="s3v4"),
        )
        prefix = f"collection/{collection_name}"
        logger.info("-> Generating S3 Pre-signed URL")
        snapshot_path = get_snapshot_signed_url_from_s3(s3_client, prefix)
    logger.info(
        f"-> Starting recovery process for collection {collection_name} on host {host.host}"
    )
    return recover_collection_from_snapshot(host, snapshot_path, collection_name)


# Backup Utils


def download_snapshot_file(url, filepath):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return filepath


def create_s3_bucket(bucket_name):
    s3_client = boto3_session.client(
        service_name="s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        endpoint_url=settings.AWS_ENDPOINT_URL,
    )
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        logger.info(f"Successfully created bucket '{bucket_name}' ")
        return True
    except botocore.errorfactory.ClientError as error:
        if error.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
            logger.info(f"Bucket '{bucket_name}' already exists")
            return
        logger.exception(error)
    except Exception as e:
        logger.exception(e)


def upload_snapshot_to_s3(snapshot_path, prefix, filename):
    s3_client = boto3_session.client(
        service_name="s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        endpoint_url=settings.AWS_ENDPOINT_URL,
    )
    object_name = f"{prefix}/{filename}"
    try:
        with open(snapshot_path, "rb") as f:
            s3_client.upload_fileobj(f, settings.S3_BUCKET_NAME, object_name)
        logger.info(
            f"Successfully upload {snapshot_path} to S3 Bucket ({settings.S3_BUCKET_NAME}) with Object Name: {object_name}"
        )
        return True
    except Exception as e:
        logger.exception(e)


def backup_handler(snapshot, snapshot_url, client, prefix, collection_name=None):
    if collection_name is not None:
        snapshot_dir = f"{settings.BASE_DIR}/snapshots/collection/{collection_name}"
    else:
        snapshot_dir = f"{settings.BASE_DIR}/snapshots/hosts/{client._client._host}"
    Path(snapshot_dir).mkdir(parents=True, exist_ok=True)
    local_filepath = f"{snapshot_dir}/{snapshot.name}"
    logger.info(f"-> Starting snapshot ({snapshot.name}) download")
    snapshot_path = download_snapshot_file(snapshot_url, local_filepath)
    logger.info(
        f"-> Snapshot: {snapshot.name} successfully downloaded to {snapshot_path}"
    )
    upload = upload_snapshot_to_s3(
        snapshot_path=snapshot_path, prefix=prefix, filename=snapshot.name
    )
    if upload:
        logger.info(f"-> Successfully uploaded snapshot {snapshot_path} to S3")
        logger.info(f"-> Deleting snapshot {snapshot.name} from Qdrant Host")
        if collection_name is None:
            c = client.delete_full_snapshot(snapshot_name=snapshot.name)
            logger.info(c)
        else:
            c = client.delete_snapshot(
                collection_name=collection_name, snapshot_name=snapshot.name
            )
            logger.info(c)
        logger.info(
            f"-> Successfully deleted snapshot {snapshot.name} from Qdrant Host"
        )
        logger.info(f"-> Deleting snapshot {snapshot_path} from Local")
        try:
            os.unlink(snapshot_path)
            logger.info(f"-> Successfully deleted snapshot {snapshot_path} from local")
        except OSError as e:
            logger.error("Error: %s - %s." % (e.filename, e.strerror))
        return True
    else:
        logger.info(f"Uploading Snapshot {snapshot.name} failed")
        return


def backup_storage_handler(qhost):
    # We need separate clients as every node as to be backed up separately
    client = QdrantClient(
        host=qhost.host,
        port=qhost.port,
        grpc_port=qhost.grpc_port,
        prefer_grpc=qhost.prefer_grpc,
    )
    snapshot = client.create_full_snapshot()
    snapshot_url = f"http://{client._client._host}:{client._client._port}/snapshots/{snapshot.name}"
    prefix = f"full-storage/{client._client._host}"
    logger.info(f"Starting backup handling process with snapshot: {snapshot.name}")
    backup = backup_handler(
        snapshot=snapshot,
        snapshot_url=snapshot_url,
        client=client,
        prefix=prefix,
    )
    if backup:
        logger.info(
            f"Backup successfully completed for host: {client._client._host} with snapshot {snapshot.name}"
        )
        return True
    else:
        logger.error(
            f"Backup creation failed for host : {client._client._host} with snapshot {snapshot.name}"
        )
        return False


def verify_collection_snapshot(snapshot_url):
    with requests.get(snapshot_url, stream=True) as r:
        if r.status_code == 200:
            return True
        return False


def get_collections_for_backup():
    collections_json = settings.QDRANT_DB_COLLECTIONS_JSON_PATH
    with open(collections_json) as f:
        collections_json = f.read()
    collections = Collections(**json.loads(collections_json))
    return collections.model_dump()


def get_hosts_for_backup():
    hosts_json = settings.QDRANT_DB_HOSTS_JSON_PATH
    with open(hosts_json) as f:
        hosts_json = f.read()
    hosts = Hosts(**json.loads(hosts_json))
    return hosts.model_dump()


def backup_collection_handler(client, collection_name, snapshot):
    snapshot_url = f"http://{client._client._host}:{client._client._port}/collections/{collection_name}/snapshots/{snapshot.name}"
    prefix = f"collection/{collection_name}"
    logger.info(
        f"Starting backup handling process with snapshot: {snapshot.name} on host {client._client._host}"
    )
    backup = backup_handler(
        snapshot=snapshot,
        snapshot_url=snapshot_url,
        client=client,
        prefix=prefix,
        collection_name=collection_name,
    )
    if backup:
        logger.info(
            f"Backup successfully completed for collection: {collection_name} with snapshot {snapshot.name}"
        )
        return True
    else:
        logger.error(
            f"Backup creation failed for collection : {collection_name} with snapshot {snapshot.name}"
        )
        return False
