from .Base_Controller import Base_controller
from models import ResponseEnum
from fastapi import FastAPI, APIRouter,Depends,UploadFile

class Data_Controller(Base_controller):
    def __init__(self):
        super().__init__()
        self.size = 1048576 # convert mb to Byte

    def validate_file(self, file:UploadFile):
       
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPE:
            return False, ResponseEnum.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size:
            return False,ResponseEnum.FILE_SIZE_EXCEEDED.value
        
        return True,ResponseEnum.FILE_VALIDATE_SUCCESSFULLY.value
    

