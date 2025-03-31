from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, HttpUrl

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    url: HttpUrl
    is_active: bool = True

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = None
    url: Optional[HttpUrl] = None

class ProjectInDBBase(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    owner_id: int

    class Config:
        orm_mode = True

class Project(ProjectInDBBase):
    pass

class ProjectResponse(ProjectInDBBase):
    pass

class ProjectList(BaseModel):
    total: int
    items: List[ProjectResponse] 