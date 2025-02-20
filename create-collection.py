import pandas as pd
import weaviate
from weaviate.embedded import EmbeddedOptions
from weaviate.classes.config import Configure, Property, DataType, Tokenization


vector_db_client = weaviate.connect_to_local()
vector_db_client.connect()
print("DB is ready: {}".format(vector_db_client.is_ready()))


# Config collection name
COLLECTION_NAME = "AnimeCollection"

def preprocess_data(file_path):
    data = pd.read_csv(file_path)

    # Convert arrays properly
    array_columns = ['genres', 'producers', 'studios']
    for col in array_columns:
        data[col] = data[col].apply(lambda x: x.split(',') if isinstance(x, str) else [])
    return data

def create_collection():
    # Create schema for collection
    anime_collection = vector_db_client.collections.create(
        name=COLLECTION_NAME,
        # Using model transformers to create vectors
        vectorizer_config=Configure.Vectorizer.text2vec_transformers(),
        properties=[
            # Anime title: text, vectorized and converted to lowercase
            Property(name="title", data_type=DataType.TEXT,
                     vectorize_property_name=True, tokenization=Tokenization.LOWERCASE),
            Property(name="genres", data_type=DataType.TEXT_ARRAY, tokenization=Tokenization.WORD),
            Property(name="studios", data_type=DataType.TEXT_ARRAY, tokenization=Tokenization.WORD),
            Property(name="producers", data_type=DataType.TEXT_ARRAY, tokenization=Tokenization.WORD),
            # Anime thumbnail
            Property(name="main_picture", data_type=DataType.TEXT, skip_vectorization=True),
        ]
    )
    # Apply preprocessing before sending to Vector DB
    data = preprocess_data('data/anime_cleaned.csv')

    # Convert data for import
    sent_to_vector_db = data.to_dict(orient='records')
    total_records = len(sent_to_vector_db)
    print(f"Inserting data to Vector DB. Total records: {total_records}")

    # Import data into DB in batch
    with anime_collection.batch.dynamic() as batch:
        for data_row in sent_to_vector_db:
            print(f"Inserting: {data_row['title']}")
            batch.add_object(properties=data_row)

    print("Data saved to Vector DB")


# Check and create collection if it does not exist
if vector_db_client.collections.exists(COLLECTION_NAME):
    print("Collection {} already exists".format(COLLECTION_NAME))
else:
    create_collection()

# Close connection
vector_db_client.close()