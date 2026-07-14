from fastapi import FastAPI, APIRouter,Depends,UploadFile,status,Request
from fastapi.responses import JSONResponse
import os
from helper_function.config import get_settings ,settings
from controllers import Data_Controller,Project_Controller,Process_Controller
from models import ResponseEnum
import aiofiles
from .schemes.data import ProcessRequest
from models.Project_model import Project_model
from models.dp_schemes import Data_chunk , Files
from models.chunk_model import chunk_model
from models.Files_model import Files_model
from bson import ObjectId

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(request:Request, project_id:str,file:UploadFile,
                      app_settings : settings = Depends(get_settings)):


    project_model = await Project_model.create_instance(
        db_client = request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id = project_id
    )

    is_valid,signal = Data_Controller().validate_file(file=file)

    if not is_valid:
       return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "signal": signal
        }   

    )
    
    # not used yet
    project_path = Project_Controller().get_project_path(project_id = project_id)

    file_path,file_id = Data_Controller().generate_unique_file_path(
            file_name=file.filename ,
            project_id= project_id
            )
    
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while True:
                chunk = await file.read(app_settings.FILE_CHUNK_SIZE)
                if not chunk:
                    break
                await f.write(chunk)

    except Exception as e:    
         return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
            "signal": ResponseEnum.FILE_UPLOAD_FAILED
            }
         )

    #store Files(assets) into database
    files_model = await Files_model.create_instance(
        db_client= request.app.db_client
    )
    file_resource = Files(
        file_project_id = project_id,
        file_type="file",
        file_name=file_id,
        file_size=os.path.getsize(file_path)
    )
    file_record = await files_model.create_file(files = file_resource)

    return JSONResponse(
        content={
            "signal": ResponseEnum.FILE_UPLOAD_SUCCESS.value,
            "file_id":str(file_record.id),
            "project_id":str(project_id)
            }  
        )  


      
@data_router.post("/process/{project_id}")
async def process_endpoint(request:Request,project_id:str , ProcessRequest:ProcessRequest):

    file_id = ProcessRequest.file_id
    chunk_size = ProcessRequest.chunk_size
    overlap_size = ProcessRequest.overlap_size

    project_model = await Project_model.create_instance(
        db_client = request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id = project_id
    )

    process_control = Process_Controller(project_id=project_id)
    file_content  = process_control.get_file_content(file_id=file_id)
    
    file_chunks = process_control.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size
        )

    
    if file_chunks is None or len(file_chunks)==0:
          return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                    "signal": ResponseEnum.PROCESSING_FAILED
                    }
        )

    file_chunk_record = [
        Data_chunk(
            chunk_text = chunk.page_content,
            chunk_metadata = chunk.metadata,
            chunk_order = i+1,
            chunk_project_id = project.id,
            )
            for i, chunk in enumerate(file_chunks)
        ]

    chunkmod = await chunk_model.create_instance(
        db_client = request.app.db_client
    )

    no_records = await chunkmod.insert_many_chunks(chunks = file_chunk_record)
    return JSONResponse(
        content={
            "signal": ResponseEnum.PROCESSING_SUCCESS.value,
            "inserted_chunks":no_records
        }
    )
        