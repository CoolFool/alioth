import logging

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn

from app.routers.alioth import router
from app.settings import settings
from app import housekeeping

logging.basicConfig(level = logging.INFO,format = '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')

app = FastAPI(title="alioth", description="Ingest data at scale into a Qdrant DB Cluster")

app.include_router(router=router)

@app.get("/")
def home():
    return RedirectResponse("/docs")

housekeeping.create_bucket() # Required so that gunicorn runs this when it preloads the app

if __name__ == "__main__":
    uvicorn.run(app=app,
                host=settings.HOST,
                port=settings.PORT,
                reload=settings.RELOAD,
                workers=settings.WORKERS_COUNT
                )
    