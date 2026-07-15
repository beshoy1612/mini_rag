from ..LLMInterface import LLMInterface
from LLMenum import OpenAiEnum
from openai import OpenAI
import logging

# not inherit it just implement structure or scheme 
# of interface but is the same syntax of inherit in python
class OpenAiProvider(LLMInterface):
    #api_url let us use many provider with open ai 
    def __init__(self,api_key: str,api_url: str = None,
                 default_input_max_character: int = 1000,
                 default_output_max_character: int = 1000,
                 default_generation_temprature: float =0.1):
        
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_character = default_input_max_character
        self.default_output_max_character = default_output_max_character
        self.default_generation_temprature = default_generation_temprature

        self.generation_model_id = None
        self.embedding_model_id = None
        #we need to store model_id and the dieminsion of model_id 
        #we need it in vector_db when we store it
        # so ----->
        self.embedding_size = None

        # intilaize client to deal with open ai 
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url
        )

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self,model_id: str):
        self.generation_model_id = model_id


    def set_embedding_model(self,model_id: str,embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size



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
        chat_history.append (
            self.construct_prompt(prompt=prompt,role=OpenAiEnum.USER.value)
        )
        response = self.client.embeddings.create(
            model = self.generation_model_id,
            messages = chat_history,
            max_tokens = max_output_tokens,
            temperature = temperature
        )

        if not response or not response.choices or not len(response.choices) or not response.choices[0].message:
            self.logger.error("Error while generating text with OpenAi")
            return None
        return response.choices[0].message["content"]


        
    def embed_text(self,text: str,document_type: str = None): 

        if not self.client:
            self.logger.error("OpenAi client was not found")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("embedding model for OpenAi was not found")
            return None
        
        response = self.client.embeddings.create(
            model = self.embedding_model_id,
            input = text
        )

        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text with OpenAi")
            return None
        
        return response.data[0].embedding

    def process_text(self,text: str):
        return text[:self.default_input_max_character].strip()

    def construct_prompt(self,prompt: str,role: str):
        return{
            "role" : role,
            "content" : self.process_text(prompt) 
        }

    