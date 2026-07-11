from .BaseDataModel import BaseDataModel
from .dp_schemes import Project
from .enum.DataBaseEnum import DataBaseEnum


class Project_model(BaseDataModel):
    def __init__(self, db_client :object):
        super().__init__(db_client = db_client)
        self.connection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]


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
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collection:
            self.connection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = Project.get_indexes()
            for i in indexes:
                await self.connection.create_index(
                    i["key"],
                    name = i["name"],
                    unique = i["unique"]
                )


    async def create_project(self, project:Project):
        result = await self.connection.insert_one(project.dict(by_alias=True,exclude_unset=True))    
        project._id = result.inserted_id

        return project

    async def get_project_or_create_one(self ,project_id :str):

        record = await self.connection.find_one({
            "project_id":project_id
        })
        if record is None:
            # create new project 
            project = Project(project_id = project_id)
            project = await self.create_project(project = project)

            return project
        
        return Project(** record)


    async def get_all_projects(self, page :int = 1 , page_size :int = 10):

        totla_document =  await self.connection.count_documents({})
        total_pages = totla_document//page_size
        if totla_document % page_size > 0:
            total_oages += 1

        cursor = self.connection.find().skip((page -1) * page_size ).limit(page_size)   
        projects = []
        async for document in cursor:
            projects.append(
                 projects(** document)
            )
            return projects ,total_pages