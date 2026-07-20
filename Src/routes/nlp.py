from fastapi import FastAPI, APIRouter,Depends,UploadFile,status,Request
from fastapi.responses import JSONResponse
from routes.schemes.nlp import Push_Request
from models import Project_model
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

    
