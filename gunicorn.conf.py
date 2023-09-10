import os
from dotenv import load_dotenv

load_dotenv()

bind = f"{os.getenv('ALIOTH_HOST','0.0.0.0')}:{os.getenv('ALIOTH_PORT','1337')}"

workers = int(os.getenv("GUNICORN_WORKERS", 1))

worker_class = "uvicorn.workers.UvicornWorker"

preload_app = True

PRODUCTION = str(os.getenv("PRODUCTION", "False")).lower() in ("true", "1", "t")

if PRODUCTION:
    statsd_host = (
        f"{os.getenv('STATSD_EXPORTER_HOST', 'statsd-exporter.default.svc.cluster.local')}:"
        f"{os.getenv('STATSD_EXPORTER_HOST_PORT', '9125')}"
    )

statsd_prefix = "alioth"
