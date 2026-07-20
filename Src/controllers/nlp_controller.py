from .Base_Controller import Base_controller
from models.dp_schemes import Project,Data_chunk
from typing import List
from stores.LLM.LLMenum import DocumentTypeEnum 
class nlp_controller(Base_controller):
    def __init__(self,vectordb_client,embedding_client,generation_client):
        super().__init__()

        self.generation_client = generation_client
        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client

    def create_collection_name(self , project_id:str):
        return f"collection_{project_id}".strip()

    def reset_vector_db_collection(self,project:Project):
        collection_name = self.create_collection_name(project_id = Project.project_id)
        return self.vectordb_client.delete_collection(collection_name = collection_name)

    def get_vetor_db_collection_info(self,project:Project) :
        collection_name = self.create_collection_name(project_id = Project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name = collection_name)
        return collection_info


    def index_into_vector_db(self,project:Project,chunk:List[Data_chunk],
                             do_reset:bool = False):
        #step 1: get collection name
        collection_name = self.create_collection_name(project_id = Project.project_id)

        #step 2: manage items
        text = [c.chunk_text for c in chunk]
        meta_data = [c.chunk_metadata for c in chunk]
        vectors = [
            self.embedding_client.embed_text(text = i ,document_type = DocumentTypeEnum.DOCUMENT.value )
            for i in text
        ]

        #step 3: create collection 
        _ = self.vectordb_client.create_collection(
            collection_name = collection_name,
            embedding_size = self.embedding_client.embedding_size,
            do_reset = do_reset
            ) 
        #step 4: insert into database
        _ = self.vectordb_client.insert_many(
            collection_name = collection_name ,
            text = text ,
            vector = vectors,
            metadata = meta_data
            )
        return True
