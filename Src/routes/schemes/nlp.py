from typing import Optional
from pydantic import BaseModel

class Push_Request(BaseModel):
    do_reset:Optional[int] = 0

class Search_Request(BaseModel):
    text: str
    limit:Optional[int] = 5