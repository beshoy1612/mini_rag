#library to help us in interface and decorator method 
from abc import ABC,abstractmethod
#to get architicture(structure) of class without logic 
class LLMInterface(ABC):
   # IN ANY PROVIDER We HAVE 2 DIFFERENT MODEL one for embedding AND another for GENERATION 
    # (abstractmethod)decorator to force implement this function if we inherit from this class  
    @abstractmethod
    def set_generation_model(self,model_id: str):
        pass

    @abstractmethod
    def set_embedding_model(self,model_id: str,embedding_size: int):
        pass

    #temperature ===> is the range of creativity in model [0,1] or [0,2] 0--> fact 1--> creative
    @abstractmethod
    def generate_text(self,prompt: str,max_output_tokens: int,
                      chat_history: list = [],temperature: float = None):
        pass
    # document_type most of provider deal with document_type in 
    # different ways if it question from user or realy document not from user
    @abstractmethod
    def embed_text(self,text: str,document_type: str= None): 
        pass

     #to make prompt in generate text has deatiled format for each llms 
     # before use generate text function على حسب ال llm provider 
     # classify prompt if it from user or sys_message 
    @abstractmethod
    def construct_prompt(self,prompt: str,role: str):
        pass







