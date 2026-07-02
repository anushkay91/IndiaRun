import datetime
import json
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional

class CandidateBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    experience_years: float = 0.0
    experience: Optional[str] = None
    projects: List[str] = []
    education: Optional[str] = None
    certifications: List[str] = []
    work_history: List[str] = []
    achievements: List[str] = []

class CandidateCreate(CandidateBase):
    resume_filename: str
    parsed_text: str

class CandidateResponse(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    experience_years: float = 0.0
    experience: Optional[str] = None
    projects: List[str] = []
    education: Optional[str] = None
    certifications: List[str] = []
    work_history: List[str] = []
    achievements: List[str] = []
    resume_filename: str
    created_at: datetime.datetime

    @field_validator("skills", "projects", "certifications", "work_history", "achievements", mode="before")
    @classmethod
    def parse_list_fields(cls, v):
        if isinstance(v, str):
            if not v:
                return []
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed]
            except Exception:
                pass
            return [s.strip() for s in v.split(",") if s.strip()]
        return v or []

    model_config = ConfigDict(from_attributes=True)

class SearchQuery(BaseModel):
    query: str = Field(..., description="Job description or search query for matching candidates")
    top_n: int = Field(5, description="Number of matches to return")

class SearchMatch(BaseModel):
    candidate: CandidateResponse
    score: float = Field(..., description="Semantic match score (cosine similarity)")

class SearchResponse(BaseModel):
    results: List[SearchMatch]

class ScreeningRequest(BaseModel):
    job_description: str = Field(..., description="Job description to evaluate the candidate against")

class ScreeningResponse(BaseModel):
    fit_score: int = Field(..., ge=0, le=100)
    match_summary: str
    pros: List[str]
    cons: List[str]
    interview_questions: List[str]

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to ask about the candidate")
    history: List[dict] = Field(default=[], description="Chat history containing previous messages")

class ChatResponse(BaseModel):
    reply: str

class JobAnalysisRequest(BaseModel):
    job_description: str = Field(..., description="Raw text of the job description to analyze")

class JobAnalysisResponse(BaseModel):
    role: str
    seniority: Optional[str] = None
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    responsibilities: List[str] = []
    industry: Optional[str] = None
    tools: List[str] = []
    behavioral_traits: List[str] = []
    years_experience: float = 0.0
    education: Optional[str] = None
    must_have: List[str] = []
    nice_to_have: List[str] = []
    deal_breakers: List[str] = []

class CandidateAnalysisResponse(BaseModel):
    career_summary: str
    technical_strengths: List[str] = []
    leadership: Optional[str] = None
    ownership: Optional[str] = None
    communication: Optional[str] = None
    problem_solving: Optional[str] = None
    career_growth: Optional[str] = None
    industry_experience: List[str] = []
    behavioral_traits: List[str] = []
    overall_summary: str

class HybridSearchMatch(BaseModel):
    candidate: CandidateResponse
    composite_score: float
    semantic_score: float
    skill_score: float
    experience_score: float
    industry_score: float

class HybridSearchResponse(BaseModel):
    results: List[HybridSearchMatch]

class RerankingRequest(BaseModel):
    candidate_id: int
    job_profile: JobAnalysisResponse

class RecruiterExplanation(BaseModel):
    why_this_ranking: str
    missing_skills_impact: str
    business_impact: str
    career_progression: str
    evidence_highlights: List[str]
    confidence_rationale: str

class RerankingResponse(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    strengths: List[str]
    weaknesses: List[str]
    missing_skills: List[str]
    hiring_recommendation: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    recruiter_explanation: RecruiterExplanation

class EvidenceRequest(BaseModel):
    candidate_id: int
    topics: List[str]

class EvidenceResponse(BaseModel):
    evidence: dict[str, Optional[str]]

class SkillGapRequest(BaseModel):
    candidate_id: int
    job_profile: JobAnalysisResponse

class SkillGapResponse(BaseModel):
    missing_skills: List[str]
    transferable_skills: List[str]
    learning_difficulty: str
    estimated_ramp_up: str
    hiring_risk: str

class InterviewPlanRequest(BaseModel):
    candidate_id: int
    job_profile: JobAnalysisResponse

class InterviewPlanResponse(BaseModel):
    technical_questions: List[str]
    behavioral_questions: List[str]
    leadership_questions: List[str]
    missing_skills_questions: List[str]
    follow_up_questions: List[str]

class RecruiterChatRequest(BaseModel):
    message: str
    history: List[dict]
    job_description: Optional[str] = None








