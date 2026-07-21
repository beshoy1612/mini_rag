from fastapi import FastAPI, APIRouter,Depends,UploadFile,status,Request
from fastapi.responses import JSONResponse
from routes.schemes.nlp import Push_Request
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
        generation_client = request.app.generation_client
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



        
 