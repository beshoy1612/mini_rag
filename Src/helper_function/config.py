from pydantic_settings import BaseSettings, SettingsConfigDict
# base setting --> to make this class behviour like scheme
class settings(BaseSettings):

    APP_NAME: str 
    APP_VERSION: str
    OPENAI_API_KEY: str
    FILE_ALLOWED_TYPE: list
    FILE_MAX_SIZE: int
    FILE_CHUNK_SIZE:int
    MONGODB_URL :str
    MONGODB_DATABASE:str
    
    GENERATION_BACKEND :str
    EMBEDDING_BACKEND :str

    #================================OPENAI ,COHERE CONFIG =========================
    OPENAI_API_KEY :str = None
    OPENAI_API_URL :str = None
    COHERE_API_KEY :str = None

    GENERATION_MODEL_ID :str = None
    EMBEDDING_MODEL_ID :str = None
    EMBEDDING_MODEL_SIZE :int  = None

    default_input_max_character :int  = None
    default_output_max_character :int  = None
    default_generation_temprature :float  = None
     #================================= vector DB config============================
    VECTOR_DB_BACKEND :str
    VECTOR_DB_PATH :str
    VECTOR_DB_DISTANCE_METHOD :str = None
    
    #SettingsConfigDict tells Pydantic where and how to load environment variables
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

def get_settings():
    return settings()        