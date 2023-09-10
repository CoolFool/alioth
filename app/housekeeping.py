import logging

from app.settings import settings
from app.tasks.utils import create_s3_bucket

logger = logging.getLogger(__name__)

def create_bucket():
    logger.info("-> Creating S3 bucket for snapshot storage and retrieval...")
    create_s3_bucket(bucket_name=settings.S3_BUCKET_NAME)