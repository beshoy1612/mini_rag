from pydantic import BaseModel,Field ,validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Files(BaseModel):
    id : Optional[ObjectId] = Field(None,alias="_id")
    file_project_id : str
    file_type : str = Field(...,min_length=1)
    file_name : str =  Field(...,min_length=1)
    file_size : int = Field(ge=0,default=None)
    file_config : dict = Field(default=None)
    file_pushed_at : datetime = Field(default=datetime.utcnow)

    class Config:
            arbitrary_types_allowed = True

    #static method dont need to intailaize object from class to get it using decrotor
    #we cant use self but use cls because self related to object 
    @classmethod
    def get_indexes(cls):
        return[
            {
                "key":[
                    ("file_project_id",1)  # 1 to arrange ascending  -1 to arrande descending 
                ],
                "name":"file_project_id_index",
                "unique":False  # project id can be repeated 
            },
            {
                "key":[
                ("file_project_id",1),
                ("file_name",1)
                ],
                "name":"file_project_id_name_index",
                "unique":True  # project id with file_name must be unique
            }

        ]
