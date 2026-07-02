import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import schemas
from backend.services import db_service
from backend.services.openai_service import OpenAIService
from backend.services.embedding_service import embedding_service
from backend.services.evidence_extractor import evidence_extractor
from backend.config import settings
from utils.parser import extract_text

router = APIRouter(prefix="/candidates", tags=["Candidates"])
openai_service = OpenAIService()

@router.post("/upload", response_model=schemas.CandidateResponse)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a resume, parse its content using GPT, index it in FAISS, and store it in SQLite."""
    # Ensure raw data folder exists
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    
    # Save the file locally
    file_path = os.path.join(settings.DATA_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    try:
        # 1. Extract text from PDF/Docx
        resume_text = extract_text(file_path)
        if not resume_text:
            raise HTTPException(status_code=400, detail="Unable to extract text from the resume. The file may be empty or corrupted.")

        # 2. Parse text with OpenAI GPT API
        parsed_data = openai_service.parse_resume(resume_text)
        
        # Validate or set default name/email if GPT failed to find them
        name = parsed_data.get("name") or os.path.splitext(file.filename)[0]
        email = parsed_data.get("email")
        phone = parsed_data.get("phone")
        skills = parsed_data.get("skills") or []
        experience_years = parsed_data.get("experience_years") or 0.0
        experience = parsed_data.get("experience")
        projects = parsed_data.get("projects") or []
        education = parsed_data.get("education")
        certifications = parsed_data.get("certifications") or []
        work_history = parsed_data.get("work_history") or []
        achievements = parsed_data.get("achievements") or []

        # 3. Check for duplicates (by email if available)
        if email:
            existing_candidate = db_service.get_candidate_by_email(db, email)
            if existing_candidate:
                # Delete existing candidate and rebuild index
                embedding_service.delete(db, existing_candidate.id)

        # 4. Save candidate in SQLite (without embedding vector initially)
        candidate_create = schemas.CandidateCreate(
            name=name,
            email=email,
            phone=phone,
            skills=skills,
            experience_years=experience_years,
            experience=experience,
            projects=projects,
            education=education,
            certifications=certifications,
            work_history=work_history,
            achievements=achievements,
            resume_filename=file.filename,
            parsed_text=resume_text
        )
        
        db_candidate = db_service.create_candidate(db, candidate_create)

        # 5. Index candidate composite document and sync FAISS
        embedding_service.index_candidate(db, db_candidate.id)

        # Refresh candidate with generated embedding
        db.refresh(db_candidate)
        return db_candidate

    except Exception as e:
        # Clean up saved file if process failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process and index resume: {str(e)}")

@router.get("/", response_model=list[schemas.CandidateResponse])
def list_candidates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve all candidates from database."""
    return db_service.get_candidates(db, skip=skip, limit=limit)

@router.get("/{candidate_id}", response_model=schemas.CandidateResponse)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve a single candidate by ID."""
    candidate = db_service.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.delete("/{candidate_id}")
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """Delete candidate and automatically rebuild the FAISS vector index."""
    candidate = db_service.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    # Delete resume file if it exists
    file_path = os.path.join(settings.DATA_DIR, candidate.resume_filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass # Keep going if file deletion fails

    # Delete from DB and rebuild FAISS index via EmbeddingService
    success = embedding_service.delete(db, candidate_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete candidate")
    
    return {"message": "Candidate deleted successfully and vector store index updated."}

@router.post("/analyze/{candidate_id}", response_model=schemas.CandidateAnalysisResponse)
def analyze_candidate_profile(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """Deep candidate competency assessment based on their parsed resume profile."""
    candidate = db_service.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    try:
        # Format the database record into standard schemas dictionary
        cand_dict = schemas.CandidateResponse.model_validate(candidate).model_dump()
        
        # Strip out non-resume attributes before passing to GPT
        cand_dict.pop("id", None)
        cand_dict.pop("created_at", None)
        cand_dict.pop("resume_filename", None)
        
        analysis = openai_service.analyze_candidate_profile(cand_dict)
        return schemas.CandidateAnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze candidate competency profile: {str(e)}")

@router.post("/evidence", response_model=schemas.EvidenceResponse)
def extract_candidate_evidence(
    request_in: schemas.EvidenceRequest,
    db: Session = Depends(get_db)
):
    """Forensic verification agent that extracts raw resume quotes supporting score topics."""
    candidate = db_service.get_candidate(db, request_in.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    try:
        evidence = evidence_extractor.extract_evidence(
            db, 
            candidate_id=request_in.candidate_id, 
            topics=request_in.topics
        )
        return schemas.EvidenceResponse(evidence=evidence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract candidate verification evidence: {str(e)}")

