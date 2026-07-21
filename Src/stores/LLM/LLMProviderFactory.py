from .LLMenum import LLMenum
from .providers import OpenAiProvider,CoHereProvider
class LLMProviderFactory():
    def __init__(self,config: dict):
        self.config = config

    def create(self , provider: str):
        if provider == LLMenum.OPENAI.value:
            return OpenAiProvider(
                api_key = self.config.OPENAI_API_KEY,
                api_url = self.config.OPENAI_API_URL,
                default_input_max_character  = self.config.default_input_max_character,
                default_output_max_character =  self.config.default_output_max_character,
                default_generation_temprature = self.config.default_generation_temprature 
            )
        
        if provider == LLMenum.COHERE.value:    
            return CoHereProvider(
                api_key = self.config.COHERE_API_KEY,
                default_input_max_character  = self.config.default_input_max_character,
                default_output_max_character =  self.config.default_output_max_character,
                default_generation_temprature = self.config.default_generation_temprature 
            )        