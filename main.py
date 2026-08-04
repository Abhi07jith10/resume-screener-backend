from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models import models
import schemas
from pypdf import PdfReader
from llm_service import score_resume
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Resume Screener API is running"}


# ---------- Candidates ----------

@app.post("/candidates/", response_model=schemas.CandidateResponse)
def create_candidate(candidate: schemas.CandidateCreate, db: Session = Depends(get_db)):
    db_candidate = models.Candidate(**candidate.dict())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate


@app.get("/candidates/", response_model=list[schemas.CandidateResponse])
def list_candidates(db: Session = Depends(get_db)):
    return db.query(models.Candidate).all()


# ---------- Resume Upload ----------

@app.post("/candidates/{candidate_id}/upload-resume/")
def upload_resume(candidate_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    file_path = f"uploaded_resumes/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    reader = PdfReader(file_path)
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text() or ""

    candidate.resume_text = extracted_text
    db.commit()
    db.refresh(candidate)

    return {"candidate_id": candidate.id, "extracted_text_preview": extracted_text[:300]}


# ---------- Jobs ----------

@app.post("/jobs/", response_model=schemas.JobResponse)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    db_job = models.Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@app.get("/jobs/", response_model=list[schemas.JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(models.Job).all()


# ---------- Resume Scoring (standalone, kept for testing) ----------

@app.post("/score/{candidate_id}/{job_id}")
def score_candidate_for_job(candidate_id: int, job_id: int, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    job = db.query(models.Job).filter(models.Job.id == job_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not candidate.resume_text:
        raise HTTPException(status_code=400, detail="Candidate has no resume text. Upload a resume first.")

    result = score_resume(candidate.resume_text, job.description)

    return {
        "candidate_id": candidate.id,
        "job_id": job.id,
        "score_result": result
    }


# ---------- Applications ----------

@app.post("/applications/", response_model=schemas.ApplicationResponse)
def create_application(application: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == application.candidate_id).first()
    job = db.query(models.Job).filter(models.Job.id == application.job_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not candidate.resume_text:
        raise HTTPException(status_code=400, detail="Candidate has no resume text. Upload a resume first.")

    # Run LLM scoring
    result = score_resume(candidate.resume_text, job.description)

    # Create the application record with the score
    db_application = models.Application(
        candidate_id=candidate.id,
        job_id=job.id,
        score=result.get("score", 0),
        status="reviewed"
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    return db_application


@app.get("/applications/", response_model=list[schemas.ApplicationResponse])
def list_applications(db: Session = Depends(get_db)):
    return db.query(models.Application).all()


# ---------- Interview Slots ----------

@app.post("/interview-slots/", response_model=schemas.InterviewSlotResponse)
def create_interview_slot(slot: schemas.InterviewSlotCreate, db: Session = Depends(get_db)):
    application = db.query(models.Application).filter(models.Application.id == slot.application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    db_slot = models.InterviewSlot(
        application_id=slot.application_id,
        datetime=slot.datetime,
        status="proposed"
    )
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot


@app.get("/interview-slots/", response_model=list[schemas.InterviewSlotResponse])
def list_interview_slots(db: Session = Depends(get_db)):
    return db.query(models.InterviewSlot).all()