from celery import Celery

from app.settings import settings
from app.tasks.utils import get_collections_for_backup, get_hosts_for_backup

app = Celery("alioth")
app.config_from_object("app.tasks.celeryconfig")
collections = get_collections_for_backup()
hosts = get_hosts_for_backup()
app.conf.beat_schedule = {
    "backup-collection": {
        "task": "app.tasks.backup.backup_collection",
        "schedule": settings.BACKUP_SCHEDULE,
        "args": (collections,),
    },
    "backup-storage": {
        "task": "app.tasks.backup.backup_storage",
        "schedule": settings.BACKUP_SCHEDULE,
        "args": (hosts,),
    },
}
app.conf.timezone = "UTC"
app.autodiscover_tasks()
