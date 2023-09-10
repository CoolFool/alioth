import csv
import random
import uuid
import json


def generate_json_payload(n, vector_size, csv_filename="mock_movie_data.csv"):
    with open(csv_filename, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        num_rows = len(rows)

        uuids = [str(uuid.uuid4()) for _ in range(n)] 
        vectors = [
            [round(random.uniform(0, 1), 3) for _ in range(vector_size)]
            for _ in range(n)
        ] 

        movies = []

        for _ in range(n):
            if num_rows < 2:
                break 

            row1 = random.choice(rows)
            row2 = random.choice(rows)

            
            movie = {
                "director": row1["director"],
                "genre": row2["genre"],
                "name": row1["name"] + " " + row2["name"], 
            }

            movies.append(movie)

        payload = {"batch": {"ids": uuids, "payloads": movies, "vectors": vectors}}
        return json.dumps(payload)
