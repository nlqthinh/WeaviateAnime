# Viết code để insert dữ liệu vào Weavite
# Import các thư viện cần thiết
import pandas as pd
import weaviate
from weaviate.embedded import EmbeddedOptions
from weaviate.classes.config import Configure, Property, DataType, Tokenization


# Cần chạy docker container cho model embedding:
# docker run -itp "8000:8080" semitechnologies/transformers-inference:sentence-transformers-multi-qa-MiniLM-L6-cos-v1
embedded_options = EmbeddedOptions(
    additional_env_vars={
        # Kích hoạt các module cần thiết: text2vec-transformers
        "ENABLE_MODULES": "backup-filesystem,text2vec-transformers",
        "BACKUP_FILESYSTEM_PATH": "/tmp/backups",  # Chỉ định thư mục backup
        "LOG_LEVEL": "panic",  # Chỉ định level log, chỉ log khi có lỗi
        "TRANSFORMERS_INFERENCE_API": "http://localhost:8000"  # API của model embedding
    },
    persistence_data_path="data",  # Thư mục lưu dữ liệu
)

# Khởi tạo Weaviate và kết nối
# vector_db_client = weaviate.WeaviateClient(
#     embedded_options=embedded_options
# )
vector_db_client = weaviate.connect_to_local()
vector_db_client.connect()
print("DB is ready: {}".format(vector_db_client.is_ready()))


# Cấu hình tên collection
COLLECTION_NAME = "AnimeCollection"

def preprocess_data(file_path):
    data = pd.read_csv(file_path)

    # Convert arrays properly
    array_columns = ['genres', 'producers', 'studios']
    for col in array_columns:
        data[col] = data[col].apply(lambda x: x.split(',') if isinstance(x, str) else [])
    return data

def create_collection():
    # Tạo schema cho collection
    anime_collection = vector_db_client.collections.create(
        name=COLLECTION_NAME,
        # Sử dụng model transformers để tạo vector
        vectorizer_config=Configure.Vectorizer.text2vec_transformers(),
        properties=[
            # Tiêu đề anime: text, được vector hóa và chuyển thành chữ thường
            Property(name="title", data_type=DataType.TEXT,
                     vectorize_property_name=True, tokenization=Tokenization.LOWERCASE),
            Property(name="genres", data_type=DataType.TEXT_ARRAY, tokenization=Tokenization.WORD),
            Property(name="studios", data_type=DataType.TEXT_ARRAY, tokenization=Tokenization.WORD),
            Property(name="producers", data_type=DataType.TEXT_ARRAY, tokenization=Tokenization.WORD),
            Property(name="main_picture", data_type=DataType.TEXT, skip_vectorization=True),
        ]
    )
    # Apply preprocessing before sending to Vector DB
    data = preprocess_data('anime_cleaned.csv')

    # Chuyển đổi dữ liệu để import
    sent_to_vector_db = data.to_dict(orient='records')
    total_records = len(sent_to_vector_db)
    print(f"Inserting data to Vector DB. Total records: {total_records}")

    # Import dữ liệu vào DB theo batch
    with anime_collection.batch.dynamic() as batch:
        for data_row in sent_to_vector_db:
            print(f"Inserting: {data_row['title']}")
            batch.add_object(properties=data_row)

    print("Data saved to Vector DB")


# Kiểm tra và tạo collection nếu chưa tồn tại
if vector_db_client.collections.exists(COLLECTION_NAME):
    print("Collection {} already exists".format(COLLECTION_NAME))
else:
    create_collection()

# Đóng kết nối
vector_db_client.close()