from enum import Enum
class LLMenum(Enum):
    #store any name of provider we will use 
    OPENAI = "OPENAI"
    COHERE = "COHERE"
class OpenAiEnum(Enum):
    SYSTEM = "SYSTEM" 
    USER = "USER"
    ASSISTANT = "ASSISTANT"