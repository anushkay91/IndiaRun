from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import schemas
from backend.services import db_service
from backend.services.embedding_service import embedding_service
from backend.services.openai_service import OpenAIService
from backend.services.hybrid_search import hybrid_search_service

router = APIRouter(prefix="/search", tags=["Search & Screen"])
openai_service = OpenAIService()

@router.post("/match", response_model=schemas.SearchResponse)
def match_candidates(
    search_input: schemas.SearchQuery,
    db: Session = Depends(get_db)
):
    """Semantic search candidate resumes matching a job description or query."""
    try:
        results = embedding_service.search(db, query_text=search_input.query, top_n=search_input.top_n)
        return schemas.SearchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to match candidates: {str(e)}")

@router.post("/screen/{candidate_id}", response_model=schemas.ScreeningResponse)
def screen_candidate(
    candidate_id: int,
    request_in: schemas.ScreeningRequest,
    db: Session = Depends(get_db)
):
    """Screen candidate resume against job description using GPT."""
    candidate = db_service.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    try:
        screening_report = openai_service.screen_candidate(
            resume_text=candidate.parsed_text,
            job_description=request_in.job_description
        )
        return schemas.ScreeningResponse(**screening_report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to screen candidate: {str(e)}")

@router.post("/chat/{candidate_id}", response_model=schemas.ChatResponse)
def chat_candidate(
    candidate_id: int,
    chat_in: schemas.ChatRequest,
    db: Session = Depends(get_db)
):
    """Ask candidate-specific questions in an interactive chat session using resume context."""
    candidate = db_service.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    try:
        reply = openai_service.chat_with_candidate(
            resume_text=candidate.parsed_text,
            question=chat_in.message,
            history=chat_in.history
        )
        return schemas.ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")

@router.post("/hybrid", response_model=schemas.HybridSearchResponse)
def hybrid_search_candidates(
    search_input: schemas.SearchQuery,
    db: Session = Depends(get_db)
):
    """Hybrid search combining semantic matching, skill overlap, experience matching, and industry match."""
    try:
        results = hybrid_search_service.search_hybrid(
            db, 
            job_description_text=search_input.query, 
            top_n=search_input.top_n
        )
        return schemas.HybridSearchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform hybrid search: {str(e)}")

@router.post("/rerank", response_model=schemas.RerankingResponse)
def rerank_candidate_profile(
    request_in: schemas.RerankingRequest,
    db: Session = Depends(get_db)
):
    """Stage-2 deep re-ranking and fit analysis comparing a parsed Job Profile and Candidate Profile."""
    candidate = db_service.get_candidate(db, request_in.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    try:
        # Convert candidate details to clean JSON dictionary
        cand_dict = schemas.CandidateResponse.model_validate(candidate).model_dump()
        
        # Remove database-specific fields
        cand_dict.pop("id", None)
        cand_dict.pop("created_at", None)
        cand_dict.pop("resume_filename", None)
        
        # Call re-ranking service
        comparison = openai_service.rerank_candidate(
            job_profile=request_in.job_profile.model_dump(),
            candidate_profile=cand_dict
        )
        return schemas.RerankingResponse(**comparison)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute re-ranking fit analysis: {str(e)}")

@router.post("/skill-gap", response_model=schemas.SkillGapResponse)
def analyze_skill_gap(
    request_in: schemas.SkillGapRequest,
    db: Session = Depends(get_db)
):
    """Execute technical skill gap analysis comparing a candidate and a Job Profile."""
    candidate = db_service.get_candidate(db, request_in.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    try:
        # Convert candidate details to clean JSON dictionary
        cand_dict = schemas.CandidateResponse.model_validate(candidate).model_dump()
        
        # Remove database-specific fields
        cand_dict.pop("id", None)
        cand_dict.pop("created_at", None)
        cand_dict.pop("resume_filename", None)
        
        # Call Skill Gap service
        gap_analysis = openai_service.analyze_skill_gap(
            job_profile=request_in.job_profile.model_dump(),
            candidate_profile=cand_dict
        )
        return schemas.SkillGapResponse(**gap_analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute technical skill gap analysis: {str(e)}")

@router.post("/interview-plan", response_model=schemas.InterviewPlanResponse)
def generate_interview_planner(
    request_in: schemas.InterviewPlanRequest,
    db: Session = Depends(get_db)
):
    """Generate tailored interview planner question sets comparing a candidate and a Job Profile."""
    candidate = db_service.get_candidate(db, request_in.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    try:
        # Convert candidate details to clean JSON dictionary
        cand_dict = schemas.CandidateResponse.model_validate(candidate).model_dump()
        
        # Remove database-specific fields
        cand_dict.pop("id", None)
        cand_dict.pop("created_at", None)
        cand_dict.pop("resume_filename", None)
        
        # Call Interview Planner service
        interview_plan = openai_service.generate_interview_plan(
            job_profile=request_in.job_profile.model_dump(),
            candidate_profile=cand_dict
        )
        return schemas.InterviewPlanResponse(**interview_plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate custom interview plan: {str(e)}")

@router.post("/chat-recruiter", response_model=schemas.ChatResponse)
def chat_recruiter_assistant(
    chat_in: schemas.RecruiterChatRequest,
    db: Session = Depends(get_db)
):
    """Converse with the recruiter assistant about the candidate pool and job descriptions."""
    try:
        # Load all candidates context from DB
        candidates = db_service.get_all_candidates(db)
        
        candidates_summary = []
        for cand in candidates:
            # Parse candidate to schema and extract fields
            cand_resp = schemas.CandidateResponse.model_validate(cand)
            candidates_summary.append({
                "name": cand_resp.name,
                "email": cand_resp.email,
                "experience_years": cand_resp.experience_years,
                "skills": cand_resp.skills,
                "education": cand_resp.education,
                "experience": cand_resp.experience,
                "certifications": cand_resp.certifications,
                "achievements": cand_resp.achievements
            })
            
        # Call OpenAI Chat Recruiter service
        reply = openai_service.chat_with_recruiter(
            message=chat_in.message,
            history=chat_in.history,
            candidates=candidates_summary,
            job_description=chat_in.job_description
        )
        return schemas.ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recruiter response: {str(e)}")




