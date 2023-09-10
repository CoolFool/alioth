import os
from pathlib import Path
import json

from locust import HttpUser, task, between
from qdrant_client.models import Batch

from utils import generate_json_payload
from app.routers.schemas import IngestionBatch

BASE_DIR = os.path.dirname(Path(__file__).parent.resolve())
MOCK_DATA_PATH=f"{BASE_DIR}/benchmark/mock_movie_data.csv"

class User(HttpUser):
    wait_time = between(1, 5)

    @task
    def root(self):
        self.client.get("/")

    @task
    def put_records(self):
        mock_data = json.loads(generate_json_payload(25,1024,MOCK_DATA_PATH))["batch"]
        payload = Batch(ids=mock_data["ids"],vectors=mock_data["vectors"],payloads=mock_data["payloads"])
        batch = IngestionBatch(collection_name="movie_collection",batch=payload)
        self.client.post("/alioth/ingest", data=json.dumps(batch.model_dump()))