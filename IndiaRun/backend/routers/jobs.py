from fastapi import APIRouter, HTTPException
from backend import schemas
from backend.services.openai_service import OpenAIService

router = APIRouter(prefix="/jobs", tags=["Job Description Analyzer"])
openai_service = OpenAIService()

@router.post("/analyze", response_model=schemas.JobAnalysisResponse)
def analyze_job_description(request_in: schemas.JobAnalysisRequest):
    """Analyze a raw job description and return a structured JSON profile using GPT."""
    if not request_in.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description text cannot be empty.")
    
    try:
        analysis = openai_service.analyze_job(request_in.job_description)
        return schemas.JobAnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze job description: {str(e)}")
