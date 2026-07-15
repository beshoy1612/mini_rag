from typing import Optional
from pydantic import BaseModel,Field
class ProcessRequest(BaseModel):
    file_id: Optional[str] = Field(
        default=None,
        description="Optional file name"
    )
    chunk_size: int = 100
    overlap_size: int = 20
    do_reset: int = 0