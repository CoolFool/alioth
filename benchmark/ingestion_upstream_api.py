from locust import HttpUser, task, between
from utils import generate_json_payload
import os
from pathlib import Path

BASE_DIR = os.path.dirname(Path(__file__).parent.resolve())
MOCK_DATA_PATH = f"{BASE_DIR}/benchmark/mock_movie_data.csv"
BATCH_SIZE = int(os.getenv("ALIOTH_LOAD_TEST_BATCH_SIZE",100))


class User(HttpUser):
    wait_time = between(1, 5)

    # @task
    # def root(self):
    #     self.client.get("/")

    @task
    def put_records(self):
        self.client.put(
            "/collections/movie_collection/points",
            data=generate_json_payload(BATCH_SIZE, 100, MOCK_DATA_PATH),
        )
