from typing import Optional
from pydantic import BaseModel

class Push_Request(BaseModel):
    do_restc:Optional[int] = 0