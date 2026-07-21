from typing import Optional
from pydantic import BaseModel

class Push_Request(BaseModel):
    do_reset:Optional[int] = 0