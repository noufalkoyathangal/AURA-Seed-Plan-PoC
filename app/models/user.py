from pydantic import BaseModel
from typing import List

class User(BaseModel):
    id: str
    name: str
    email: str
    permissions: List[str]
    role: str = "planner"
