from helper_function.config import get_settings,settings
import os
import  random
import string

class Base_controller:

    def __init__(self):
        
        self.app_settings = get_settings()  
        # to get source path of base_controller (src)
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        # get directory to save file in it 
        # save directory = join of (base(Src) + assets/files)
        self.file_dir = os.path.join(
            self.base_dir,
            "assets/files"
        )
        self.database_dir = os.path.join(
            self.base_dir,
            "assets/database"
        )

    def generate_random_string(self,length:int=12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k = length))

    def get_database_path(self,db_name:str):

        database_path = os.path.join(
            self.database_dir,db_name
        )
        if not os.path.exists(database_path):
            os.makedirs(database_path)

        return database_path   