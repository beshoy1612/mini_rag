from qdrant_client import QdrantClient,models
from ..VectorDBInterface import VectorDBInterface
import logging
from ..VectorDBEnum import DistanceMethodEnum
from typing import List
from models.dp_schemes import Retrived_document


class QdrantDB(VectorDBInterface):
    def __init__(self,db_path: str, distance_method: str):
        self.db_path = db_path
        self.client = None # will intalize in connect function
        self.distance_method = distance_method

        distance_method = distance_method.upper()

        distance_map = {
            "COSINE": models.Distance.COSINE,
            "DOT": models.Distance.DOT,
            "EUCLID": models.Distance.EUCLID,
            "MANHATTAN": models.Distance.MANHATTAN,
        }

        self.distance_method = distance_map[distance_method]

        self.logger = logging.getLogger(__name__)


    def connect(self):
        self.client = QdrantClient(path=self.db_path)


    def disconnect(self):
        self.client = None

    def is_collection_exist(self, collection_name) -> bool:
        return self.client.collection_exists(collection_name= collection_name)


    def list_all_collection(self) -> List:
        return self.client.get_collection()

    def get_collection_info(self,collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name):
        if self.is_collection_exist(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)


    def create_collection(self,collection_name: str,
                              embedding_size: int,
                              do_reset: bool = False) :
        if do_reset:
            _ =  self.delete_collection(collection_name=collection_name)

        if not self.is_collection_exist(collection_name=collection_name):
             _ =  self.client.create_collection(
                   collection_name = collection_name,
                    vectors_config =models.VectorParams(
                        size= embedding_size,
                        distance=self.distance_method
                    ) 
         )        
             return True
        
        return False


    def insert_one(self,collection_name: str,
                      text: str ,vector:list,
                      metadata: str = None, record_id:str = None):
        if not self.is_collection_exist(collection_name=collection_name):
            self.logger.error(f"cant insert new record to non_existance collection : {collection_name}")
            return False
        try:    
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id = [record_id],
                        vector=vector,
                        payload={
                            "metadata": metadata,
                            "text": text
                        }
                    )
                ]
            )
        except Exception as e :
            self.logger.error(f"error while inserting record {e}")
            return False
        
        return True


    def insert_many(self,collection_name: str, text: list ,
                vector:list, metadata: list = None,
                    record_id:list = None, batch_size: int = 50):
        if metadata is None:
            metadata = [None] * len(text)

        if record_id is None:
            record_id = list(range(0,len(text)))    

        for i in range(0,len(text),batch_size):
            batch_end = i + batch_size
            batch_text = text[i:batch_end]
            batch_vector = vector[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_id = record_id[i:batch_end]
            batch_record = [
                models.Record(
                    id = batch_record_id[x],
                    vector = batch_vector[x],
                    payload={
                        "metadata": batch_metadata[x],
                        "text": batch_text[x]
                    }
                )
                for x in range(len(batch_text))
            ]
            try:
                _ = self.client.upload_records(
                            collection_name=collection_name,
                            records=batch_record
                            )
            except Exception as e:
                self.logger.error(f"error while insert batch {e}")
                return False
            
        return True
 

    def search_by_vector(self,collection_name: str,vector:list, limit: int):
        # we dont need to get the returned vector db from qdrant only but we intiate 
        # scheme so will use it in a different thing and make it general scheme
        results =  self.client.search(
            collection_name= collection_name,
            query_vector= vector,
            limit= limit
        )
        if not results or len(results) == 0:
            return None

        return[
            Retrived_document(**{
                "score":result.score,
                "text": result.payload["text"]
            })
            for result in results
        ]