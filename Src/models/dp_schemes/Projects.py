from pydantic import BaseModel,Field ,validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    id : Optional[ObjectId] = Field(None,alias="_id")
    project_id :str =Field(...,min_length = 1)

    @validator("project_id")
    def validate_project_id(cls,value:str):
        if not value.isalnum():
            raise ValueError("project id must be alphanumeric")

        return value
    
    class Config:
        arbitrary_types_allowed = True

    #static method dont need to intailaize object from class to get it using decrotor
    #we cant use self but use cls because self related to object 
    @classmethod
    def get_indexes(cls):
        return[
            {
                "key":[
                    ("project_id",1)  # 1 to arrange ascending  -1 to arrande descending 
                ],
                "name":"project_id_index",
                "unique":True  # project id must be unique 
            }
        ]

