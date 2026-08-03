from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models import models
import schemas
from pypdf import PdfReader
import os

app = FastAPI()

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

    # Save the uploaded file temporarily
    file_path = f"uploaded_resumes/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Extract text from the PDF
    reader = PdfReader(file_path)
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text() or ""

    # Save extracted text to the candidate record
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