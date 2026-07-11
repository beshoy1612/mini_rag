from .BaseDataModel import BaseDataModel
from .dp_schemes import Data_chunk
from .enum.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne

class chunk_model(BaseDataModel):
    def __init__(self, db_client :object):
        super().__init__(db_client = db_client)
        self.connection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

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
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collection:
            self.connection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
            indexes = Data_chunk.get_indexes()
            for i in indexes:
                await self.connection.create_index(
                    i["key"],
                    name = i["name"],
                    unique = i["unique"]
                )

    async def create_chunk(self, chunk:Data_chunk):
        result = await self.connection.insert_one(chunk.dict(by_alias=True,exclude_unset=True))
        chunk._id = result.inserted_id
        return chunk 

    async def  get_chunk(self, chunk_id:str):
        result = await self.connection.find_one({
            "_id":ObjectId(chunk_id)
        })

        if result is None:
            return None
        
        return Data_chunk(**result)


    async def insert_many_chunks(self, chunks:list, batch_size:int=100):
        for i in range(0,len(chunks),batch_size):
            batch = chunks[i:i+batch_size]
            operation = [
                InsertOne(chunk.dict(by_alias=True,exclude_unset=True))
                for chunk in batch
            ]
            await self.connection.bulk_write(operation)

        return len(chunks)       