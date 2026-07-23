from pydantic import BaseModel,Field 
from typing import Optional
from bson.objectid import ObjectId

 
class Data_chunk(BaseModel):
    id : Optional[ObjectId] = Field(None,alias="_id")
    chunk_text:str =Field(..., min_length=1)
    chunk_metadata :dict
    chunk_order :int = Field(...,gt=0)
    chunk_project_id :ObjectId
    chunnk_file_id:ObjectId
    
    class Config:
         arbitrary_types_allowed = True

    #static method dont need to intailaize object from class to get it using decrotor
    #we cant use self but use cls because self related to object 
    @classmethod
    def get_indexes(cls):
        return[
            {
                "key":[
                    ("chunk_project_id",1)  # 1 to arrange ascending  -1 to arrande descending 
                ],
                "name":"project_id_index",
                "unique":False  # chunk_project id can be repeated
            }
        ]

class Retrived_document(BaseModel):
    text : str
    score : float