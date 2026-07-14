from .BaseDataModel import BaseDataModel
from .dp_schemes import Files
from .enum.DataBaseEnum import DataBaseEnum
from bson import ObjectId

class Files_model(BaseDataModel):
    def __init__(self, db_client :object):
            super().__init__(db_client = db_client)
            self.connection = self.db_client[DataBaseEnum.COLLECTION_FILE_NAME.value]
    

    # we must call init__connection with constructor to make index just the project_model called
    # and we cant  call init_collection in __init__ because its async and __init__ cannot to be async
    # because constructor shouldnt be async and we cant use await in __init__  
    #so we create function that call __init__ and init_collection function will be static 
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client) # call __init__
        await instance.init_connection() # call init_collection
        return instance
    
    # async because deal with mongodb and motors 
    async def init_connection(self):
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_FILE_NAME.value not in all_collection:
            self.connection = self.db_client[DataBaseEnum.COLLECTION_FILE_NAME.value]
            indexes = Files.get_indexes()
            for i in indexes:
                await self.connection.create_index(
                    i["key"],
                    name = i["name"],
                    unique = i["unique"]
                )
    # create files with file scheme that we implemented in files.py
    async def create_file(self, files:Files):
        result = await self.connection.insert_one(files.dict(by_alias=True,exclude_unset=True))    
        files.id = result.inserted_id
        return files

    
    async def get_all_project_files(self,files_project_id:str):
         return await self.connection.find({
              "file_project_id" :ObjectId(files_project_id) if isinstance(files_project_id,str) 
              else files_project_id
         }).to_list(length = None) # none to get all things
   