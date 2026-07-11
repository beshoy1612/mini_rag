from .Base_Controller import Base_controller
from fastapi import UploadFile
import os
class Project_Controller(Base_controller):
    def __init__(self):
        super().__init__()
 # inherit file_dir from base_controller and add project_id for each new project
    def get_project_path(self,project_id:str):
         project_dir = os.path.join(
             self.file_dir,
             project_id
         )
 
 # make folder for each project 
         if not os.path.exists(project_dir):
             os.makedirs(project_dir)

         return project_dir    