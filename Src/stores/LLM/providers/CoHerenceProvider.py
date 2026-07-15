from ..LLMInterface import LLMInterface
from LLMenum import CoHereEnum,DocumentTypeEnum
import cohere
import logging

class CoHereProvider(LLMInterface):

    def __init__(self,api_key: str,
        default_input_max_character: int = 1000,
        default_output_max_character: int = 1000,
        default_generation_temprature: float =0.1):

        self.api_key = api_key
        self.default_input_max_character = default_input_max_character
        self.default_output_max_character = default_output_max_character
        self.default_generation_temprature = default_generation_temprature

        self.generation_model_id = None
        self.embedding_model_id = None
        #we need to store model_id and the dieminsion of model_id 
        #we need it in vector_db when we store it
        # so ----->
        self.embedding_size = None

        # intilaize client to deal with COHERE ai 
        self.client = cohere.Client(api_key = self.api_key)

        self.logger = logging.getLogger(__name__)


    def set_generation_model(self,model_id: str):
        self.generation_model_id = model_id



    def set_embedding_model(self,model_id: str,embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size



    def process_text(self,text: str):
      return text[:self.default_input_max_character].strip()



    def generate_text(self,prompt: str,max_output_tokens: int,
                          chat_history: list = [],temperature: float = None):

        if not self.client:
            self.logger.error("OpenAi client was not found")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAi was not found")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_output_max_character
        temperature = temperature if temperature else self.default_generation_temprature
    
        response = self.client.chat(
            model = self.generation_model_id,
            chat_history = chat_history,
            message = self.process_text(prompt) ,
            temperature = temperature,
            max_tokens = self.default_output_max_character
                            )
        if not response or not response.text:
            self.logger.error("Error while generating text with Cohere")
            return None

        return response.text


    # in cohere document type is important because model must know what is the type of input text
    def embed_text(self,text: str,document_type: str= None): 

        if not self.client:
            self.logger.error("Cohere client was not found")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("embedding model for Cohere was not found")
            return None

        input_type = CoHereEnum.DOCUMENT
        
        if document_type == DocumentTypeEnum.QUERY:
            input_type = CoHereEnum.QUERY

        response = self.client.embeddings.create(
            model = self.embedding_model_id,
            text = [self.process_text(text)],
            input_type = input_type,
            embedding_types = ['float']
        )

        if not response or not response.embeddings or response.embeddings.float:
            self.logger.error("Error while embedding text with Cohere")
            return None
        
        return response.embeddings.float[0]



    def construct_prompt(self,prompt: str,role: str):
        return{
            "role" : role,
            "text" : self.process_text(prompt) 
        }
    