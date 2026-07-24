from pydantic import BaseModel
from typing import Optional

class CandidateCreate(BaseModel):
    name: str
    email: str
    resume_text: Optional[str] = None
    skills: Optional[str] = None

class CandidateResponse(CandidateCreate):
    id: int

    class Config:
        from_attributes = True


class JobCreate(BaseModel):
    title: str
    description: str
    required_skills: Optional[str] = None

class JobResponse(JobCreate):
    id: int

    class Config:
        from_attributes = True