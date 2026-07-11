from .Base_Controller import Base_controller
from.Project_Controller import Project_Controller
from models import ResponseEnum
from fastapi import FastAPI, APIRouter,Depends,UploadFile
import re
import os

 # validate & get_clean_file_name & unique file name 
class Data_Controller(Base_controller):
    def __init__(self):
        super().__init__()
        self.size = 1048576 # convert mb to Byte

    def validate_file(self, file:UploadFile):
       # app setting from base_controller 
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPE:
            return False, ResponseEnum.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size:
            return False,ResponseEnum.FILE_SIZE_EXCEEDED.value
        
        return True,ResponseEnum.FILE_VALIDATE_SUCCESSFULLY.value
    
 # to store files without error if we have same file name 
    def generate_unique_file_path(self,file_name:str, project_id:str):
        # call generate_random_string from base_controller 
        random_file_name_key = self.generate_random_string()
        project_path  = Project_Controller().get_project_path(project_id=project_id)
        clean_file_name = self.get_clean_file_name(
            orig_filename=file_name
        )

        new_file_path = os.path.join(
            project_path,
            random_file_name_key + "_"+ clean_file_name

        )
        
        while os.path.exists(new_file_path):

            random_file_name_key = self.generate_random_string()
            new_file_path = os.path.join(
                        project_path,
                        random_file_name_key + "_"+ clean_file_name
                    )
            
        return new_file_path , random_file_name_key + "_"+ clean_file_name   

    def get_clean_file_name(self ,orig_filename:str):

        #remove any special characters  except .,_
        clean_file_name = re.sub(r'[^\w.]','',orig_filename.strip())  

        #replace spaces with underscore
        clean_file_name = clean_file_name .replace(" ","_")

        return clean_file_name 

