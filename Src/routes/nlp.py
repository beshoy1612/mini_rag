from fastapi import FastAPI, APIRouter,Depends,UploadFile,status,Request
from fastapi.responses import JSONResponse
from routes.schemes.nlp import Push_Request,Search_Request
from models.Project_model import Project_model
from controllers import nlp_controller
from models import ResponseEnum
from models.chunk_model import chunk_model

import os
import logging

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix="/api/v1/nlp"
)


#first: end point to store embedding text into vector db 
@nlp_router.post("/index/push/{project_id}")
async def index_project(request:Request,project_id:str,push_request:Push_Request):
    project_model = await Project_model.create_instance(
    db_client = request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id = project_id
    )
    chunkmodel = await chunk_model.create_instance(
        db_client = request.app.db_client
    )
    if not project :
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {
                "siganl" : ResponseEnum.PROJECT_NOT_FOUND_ERROR.value 
            }
        )
    nlpcontroller = nlp_controller(
        vectordb_client = request.app.vectordb_client,
        embedding_client = request.app.embedding_client,
        generation_client = request.app.generation_client,
        template_parser=request.app.template_parser
    )
    is_record = True
    page_no = 1
    inserted_count = 0
    idx = 0

    while(is_record):
        page_chunks = await chunkmodel.get_project_chunk(project_id=project.id,page_no=page_no)

        if len(page_chunks):
            page_no+=1

        if len(page_chunks) == 0 or not page_chunks :
            is_record = False
            break

        chunk_id = list(range(idx,idx+len(page_chunks)))
        idx += len(page_chunks)
        
        is_inserted = nlpcontroller.index_into_vector_db(
            project = project,
            chunk = page_chunks,
            do_reset = push_request.do_reset,
            chunk_ids= chunk_id
            )   
        if not is_inserted:
            return JSONResponse(
                status_code= status.HTTP_400_BAD_REQUEST,
                content={
                    "signal" : ResponseEnum.INSERT_INTO_VECTOR_DB_ERROR.value
                }
            )
        inserted_count+= len(page_chunks)

    return JSONResponse(
        content={
            "signal" : ResponseEnum.INSERT_INTO_VECTOR_DB_SUCESS.value,
            "inserted_item_count": inserted_count
        }
    )



#second : end point to get information about vector db 
@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request:Request,project_id:str):
    
        project_model = await Project_model.create_instance(
        db_client = request.app.db_client
        )
    
        project = await project_model.get_project_or_create_one(
            project_id = project_id
        )

        if not project :
            return JSONResponse(
                status_code = status.HTTP_400_BAD_REQUEST,
                content = {
                    "siganl" : ResponseEnum.PROJECT_NOT_FOUND_ERROR.value 
                }
            )
        nlpcontroller = nlp_controller(
            vectordb_client = request.app.vectordb_client,
            embedding_client = request.app.embedding_client,
            generation_client = request.app.generation_client,
            template_parser=request.app.template_parser
        )
        collectioninfo = nlpcontroller.get_vetor_db_collection_info(project=project)
        return JSONResponse(
        content={
            "signal" : ResponseEnum.VECTOR_DB_COLLECTION_RETRIEVED.value,
            "collection_info":collectioninfo         
        }
    )




# third : end point to do sementic search 

@nlp_router.post("/index/search/{project_id}")
async def search_index(request:Request,project_id:str,search_request:Search_Request):
    project_model = await Project_model.create_instance(
    db_client = request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id = project_id
    )

    if not project :
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {
                "siganl" : ResponseEnum.PROJECT_NOT_FOUND_ERROR.value 
            }
        )
    
    nlpcontroller = nlp_controller(
        vectordb_client = request.app.vectordb_client,
        embedding_client = request.app.embedding_client,
        generation_client = request.app.generation_client,
        template_parser = Request.app.template_parser
    )

    result = nlpcontroller.search_vector_db_collection(
        project = project,
        text = search_request.text,
        limit = search_request.limit
    )
    if not result:
     return JSONResponse(
        status_code = status.HTTP_400_BAD_REQUEST,
        content = {
            "siganl" : ResponseEnum.VECTOR_DB_SEACH_ERROR.value 
        }
    )
    return JSONResponse(
        content = {
            "siganl" : ResponseEnum.VECTOR_DB_SEACH_SUCCESS.value ,
            "result" : [res.dict() for res in result ]
        }
    ) 
@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(
        request: Request,
        project_id: str,
        search_request: Search_Request
    ):
        
    project_model = await Project_model.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    nlpcontroller = nlp_controller(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    answer, full_prompt, chat_history =  nlpcontroller.answer_rag_question(
        project=project,
        query=search_request.text,
        limit=search_request.limit,
    )

    if not answer:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseEnum.RAG_ANSWER_ERROR.value
                }
        )
    
    return JSONResponse(
        content={
            "signal": ResponseEnum.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history
        }
    )