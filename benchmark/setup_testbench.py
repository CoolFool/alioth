from qdrant_client import QdrantClient
from qdrant_client.http import models
import os

client = QdrantClient(
    host=os.getenv("QDRANT_DB_HOST"),
    port=os.getenv("QDRANT_DB_PORT")
)

print("-> Assuming a 3 node Qdrant Cluster")
print("-> Creating 'movie_collection' collection")
collection = client.recreate_collection(
    collection_name="movie_collection",
    vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
    on_disk_payload=True,
    shard_number=6,
)
if collection:
    print("-> 'movie_collection' collection successfully created")
else:
    raise SystemExit("-> 'movie_collection' collection creation failed")
