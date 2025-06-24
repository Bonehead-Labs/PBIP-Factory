from pydantic import BaseModel
from typing import Dict, Any

class DataRow(BaseModel):
    __root__: Dict[str, Any] 