from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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


class ApplicationCreate(BaseModel):
    candidate_id: int
    job_id: int

class ApplicationResponse(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    score: Optional[int] = None
    status: str

    class Config:
        from_attributes = True


class InterviewSlotCreate(BaseModel):
    application_id: int
    datetime: datetime

class InterviewSlotResponse(BaseModel):
    id: int
    application_id: int
    datetime: datetime
    status: str

    class Config:
        from_attributes = True