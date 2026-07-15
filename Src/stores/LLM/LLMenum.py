from enum import Enum
class LLMenum(Enum):
    #store any name of provider we will use 
    OPENAI = "OPENAI"
    COHERE = "COHERE"
class OpenAiEnum(Enum):
    SYSTEM = "system" 
    USER = "user"
    ASSISTANT = "assistant"

class CoHereEnum(Enum):
    SYSTEM = "SYSTEM" 
    USER = "USER"
    ASSISTANT = "CHATBOT"
    DOCUMENT = "search_document"
    QUERY = "search_query"

class DocumentTypeEnum(Enum):
    DOCUMENT = "document" 
    QUERY = "query"   