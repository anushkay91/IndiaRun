import json
from sqlalchemy.orm import Session
from backend.database import Candidate
from backend import schemas

def get_candidate(db: Session, candidate_id: int) -> Candidate | None:
    """Retrieve a candidate by ID."""
    return db.query(Candidate).filter(Candidate.id == candidate_id).first()

def get_candidate_by_email(db: Session, email: str) -> Candidate | None:
    """Retrieve a candidate by email address."""
    return db.query(Candidate).filter(Candidate.email == email).first()

def get_candidates(db: Session, skip: int = 0, limit: int = 100) -> list[Candidate]:
    """Retrieve a paginated list of candidates."""
    return db.query(Candidate).order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()

def create_candidate(
    db: Session, 
    candidate_in: schemas.CandidateCreate, 
    embedding_vector: list[float] = None
) -> Candidate:
    """Create a new candidate in the database."""
    # Convert lists to JSON or comma-separated strings for SQLite storage
    skills_str = ",".join(candidate_in.skills) if candidate_in.skills else ""
    projects_str = json.dumps(candidate_in.projects) if candidate_in.projects else "[]"
    certifications_str = json.dumps(candidate_in.certifications) if candidate_in.certifications else "[]"
    work_history_str = json.dumps(candidate_in.work_history) if candidate_in.work_history else "[]"
    achievements_str = json.dumps(candidate_in.achievements) if candidate_in.achievements else "[]"
    
    # Convert embedding vector to JSON string if provided
    embedding_str = json.dumps(embedding_vector) if embedding_vector is not None else None
    
    db_candidate = Candidate(
        name=candidate_in.name,
        email=candidate_in.email,
        phone=candidate_in.phone,
        skills=skills_str,
        experience_years=candidate_in.experience_years,
        experience=candidate_in.experience,
        projects=projects_str,
        education=candidate_in.education,
        certifications=certifications_str,
        work_history=work_history_str,
        achievements=achievements_str,
        resume_filename=candidate_in.resume_filename,
        parsed_text=candidate_in.parsed_text,
        embedding=embedding_str
    )
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

def delete_candidate(db: Session, candidate_id: int) -> bool:
    """Delete a candidate from the database."""
    db_candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if db_candidate:
        db.delete(db_candidate)
        db.commit()
        return True
    return False

def get_all_embeddings(db: Session) -> list[tuple[int, list[float]]]:
    """Retrieve all candidates' IDs and their embeddings to rebuild the vector store index."""
    candidates = db.query(Candidate.id, Candidate.embedding).all()
    results = []
    for cid, emb_str in candidates:
        if emb_str:
            try:
                emb = json.loads(emb_str)
                results.append((cid, emb))
            except Exception:
                continue
    return results
