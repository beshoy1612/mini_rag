from .BaseDataModel import BaseDataModel
from .dp_schemes import Data_chunk
from .enum.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne

class chunk_model(BaseDataModel):
    def __init__(self, db_client :object):
        super().__init__(db_client = db_client)
        self.connection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]


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