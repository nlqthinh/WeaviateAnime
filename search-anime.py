import gradio as gr
import weaviate
from weaviate.embedded import EmbeddedOptions



vector_db_client = weaviate.connect_to_local()

vector_db_client.connect()
print("DB is ready: {}".format(vector_db_client.is_ready()))

COLLECTION_NAME = "AnimeCollection"


def search_movie(query):
    # Semantic Search - NEAR TEXT
    movie_collection = vector_db_client.collections.get(COLLECTION_NAME)
    response = movie_collection.query.near_text(
        query=query, limit=10
    )

    results = []
    for movie in response.objects:
        movie_tuple = (movie.properties['main_picture'], movie.properties['title'])
        results.append(movie_tuple)
    print(results)
    return results


with gr.Blocks(title="Tìm kiếm anime với Weaviate") as interface:
    query = gr.Textbox(label="Tìm kiếm Anime", placeholder="Tên, thể loại,...")
    search = gr.Button(value="Search")
    gallery = gr.Gallery(label="Anime", show_label=False, columns=[5], rows=[3], object_fit="contain", height="auto")

    # When the user clicks search, we call the search_movie function with the query input and pass the result to the gallery.
    search.click(fn=search_movie, inputs=query, outputs=gallery)

interface.queue().launch()