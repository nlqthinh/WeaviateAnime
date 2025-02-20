import pandas as pd
import weaviate
from weaviate.embedded import EmbeddedOptions
from weaviate.classes.config import Configure, Property, DataType, Tokenization


vector_db_client = weaviate.connect_to_local()
vector_db_client.connect()
print("DB is ready: {}".format(vector_db_client.is_ready()))


COLLECTION_NAME = "AnimeCollection"

# Function to delete collection
def delete_collection():
    if vector_db_client.collections.exists(COLLECTION_NAME):
        vector_db_client.collections.delete(COLLECTION_NAME)
        print(f"Collection {COLLECTION_NAME} has been deleted.")
    else:
        print(f"Collection {COLLECTION_NAME} does not exist.")

# Call the function to delete the collection
delete_collection()
vector_db_client.close()