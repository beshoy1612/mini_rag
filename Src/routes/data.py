from fastapi import FastAPI, APIRouter,Depends,UploadFile,status
from fastapi.responses import JSONResponse
import os
from helper_function.config import get_settings ,settings
from controllers import Data_Controller,Project_Controller
from models import ResponseEnum
import aiofiles
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"]
)
@data_router.post("/upload/{project_id}")
async def upload_data(project_id:str,file:UploadFile,
                      app_settings : settings = Depends(get_settings)):
    
    is_valid,signal = Data_Controller().validate_file(file=file)

    if not is_valid:
       return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "signal": signal
        }   

    )
    
    project_path = Project_Controller().get_project_path(project_id = project_id)

    file_path = Data_Controller().generate_unique_file_name(
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
      
    return JSONResponse(
        content={
            "signal": ResponseEnum.FILE_UPLOAD_SUCCESS.value
            }  
        )  

       