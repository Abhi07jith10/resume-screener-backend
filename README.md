# Resume Screener - Backend

A backend application for an AI-powered Resume Screener built using FastAPI, PostgreSQL, and SQLAlchemy. The system provides REST APIs to manage candidates and job postings, forming the foundation for AI-based resume screening and recruitment workflows.

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Uvicorn

## Progress

### Phase 1: Setup & Foundation

- Set up Python virtual environment
- Installed FastAPI, Uvicorn, SQLAlchemy, and Psycopg2
- Created the project structure
- Built and tested the initial FastAPI application
- Initialized the Git repository
- Designed the database schema
- Created SQLAlchemy models
- Configured and executed Alembic migrations
- Connected the application to PostgreSQL

### Phase 2: Core Backend

#### Day 3 – CRUD APIs

- Implemented Candidate CRUD APIs
- Implemented Job CRUD APIs
- Tested all endpoints using Postman

## Database Schema

### Candidates
- id
- name
- email
- resume_text
- skills

### Jobs
- id
- title
- description
- required_skills

### Applications
- id
- candidate_id
- job_id
- score
- status

### InterviewSlots
- id
- application_id
- datetime
- status

## Running the Project

```bash
pip install -r requirements.txt

uvicorn main:app --reload
```

## Current Status

Completed:
- Project setup
- PostgreSQL integration
- Database design
- SQLAlchemy models
- Alembic migrations
- Candidate CRUD APIs
- Job CRUD APIs

Upcoming:
- Applications CRUD APIs
- Interview Slot Management
- AI Resume Matching
- Authentication & Authorization
