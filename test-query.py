import weaviate

vector_db_client = weaviate.connect_to_local()
vector_db_client.connect()
print("DB is ready: {}".format(vector_db_client.is_ready()))

COLLECTION_NAME = "AnimeCollection"

movie_collection = vector_db_client.collections.get(COLLECTION_NAME)
response = movie_collection.query.near_text(
    query="Bocchi The Rock",limit=5
)

for result in response.objects:
    movie = result.properties
    print("Anime: {}, Genre: {}, Studio: {}" .format(movie['title'], movie['genres'], movie['studios']))
vector_db_client.close()