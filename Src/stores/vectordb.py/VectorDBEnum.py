from enum import Enum
# qdrant is a vector database no (service or engine) database just local server
# qdrant is a file base (memory) database
class VectorDBEnum(Enum):
    QDRANT = "QDRANT"

class DistanceMethodEnum(Enum):
    COSINE = "COSINE"
    DOT = "DOT"   