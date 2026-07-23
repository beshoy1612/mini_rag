from .Base_Controller import Base_controller
from models.dp_schemes import Project,Data_chunk
from typing import List
from stores.LLM.LLMenum import DocumentTypeEnum 
import json


class nlp_controller(Base_controller):
    def __init__(self,vectordb_client,embedding_client,generation_client,template_parser):
        super().__init__()

        self.generation_client = generation_client
        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self , project_id:str):
        return f"collection_{project_id}".strip()

    def reset_vector_db_collection(self,project:Project):
        collection_name = self.create_collection_name(project_id = project.id)
        return self.vectordb_client.delete_collection(collection_name = collection_name)

    def get_vetor_db_collection_info(self,project:Project) :
        collection_name = self.create_collection_name(project_id = project.id)
        collection_info = self.vectordb_client.get_collection_info(collection_name = collection_name)
        return json.loads(
            json.dumps(collection_info,default=lambda x:x.__dict__)
        )


    def index_into_vector_db(self,project:Project,chunk:List[Data_chunk],
                             chunk_ids:List[int],
                             do_reset:bool = False):
        #step 1: get collection name
        collection_name = self.create_collection_name(project_id = project.id)

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
            metadata = meta_data,
            record_id = chunk_ids,
            )
        return True

    def search_vector_db_collection (self,project:Project ,text :str ,limit:int = 10):
        # 1 - get collection name
        collection_name = self.create_collection_name(project_id = project.id)

        # 2 - get text embedding vector
        vector  = self.embedding_client.embed_text(text = text,document_type = DocumentTypeEnum.QUERY.value)
        if not vector or len(vector) == 0:
            return False
        
        # 3 - do semantic search

        result = self.vectordb_client.search_by_vector(
            collection_name = collection_name,
            vector = vector,
              limit = limit
              )
        if not result :
            return False
        
        return result


    def answer_rag_question(self, project:Project,query:str,limit: int = 10):
        answer, full_prompt, chat_history = None, None, None
        #step 1 : retrive document from vectordb collection
        retrived_document = self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit
        )
        if not retrived_document or len(retrived_document)==0:
            return answer, full_prompt, chat_history

        #step 2: LLM prompt ==>(system prompt , user prompt(document,footer)prompt)
        system_prompt = self.template_parser.get("rag","system_prompt") # will be stored in chat history(generation model)
        # using comprehension list 
        document_prompt ="\n".join ([
            self.template_parser.get("rag","document_prompt",
                {
                    "doc_num":idx+1,
                    "chunk_text":doc.text,
                })
            for idx,doc in enumerate( retrived_document)
        ])

        footer_prompt = self.template_parser.get(
            "rag",
            "footer_prompt",
            {
                "query": query
            }
        )
         # step3: Construct Generation Client Prompts
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt = "\n\n".join([ document_prompt,  footer_prompt])

        # step4: Retrieve the Answer
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history