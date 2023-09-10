from app.settings import settings

CELERY_BROKER_URL = f"{settings.BROKER_PROTO}://{settings.BROKER_USER}:{settings.BROKER_PASS}@{settings.BROKER_HOST}:{settings.BROKER_PORT}/"
broker_url = CELERY_BROKER_URL
task_ignore_result = True
task_store_errors_even_if_ignored = True
task_routes = {
    "app.tasks.backup.*": {"queue": "backup"},
    "app.tasks.restore.*":{"queue": "restore"},
    "app.tasks.ingestion.*": {"queue": "ingest"},
}

task_acks_late = True
task_acks_on_failure_or_timeout = True
worker_send_task_events = True
task_send_sent_event = True
broker_pool_limit = 0

