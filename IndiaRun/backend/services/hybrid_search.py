from sqlalchemy.orm import Session
from backend.database import Candidate
from backend import schemas
from backend.services import db_service
from backend.services.openai_service import OpenAIService
from backend.services.embedding_service import embedding_service
from backend.services.vector_store import vector_store

class HybridSearchService:
    def __init__(self):
        self.openai_service = OpenAIService()

    def search_hybrid(self, db: Session, job_description_text: str, top_n: int = 20) -> list[schemas.HybridSearchMatch]:
        """Perform a hybrid search combining Semantic, Skills, Experience, and Industry Match scoring."""
        # 1. Parse the Job Description using the Job Understanding Agent
        job_profile = self.openai_service.analyze_job(job_description_text)
        
        req_skills = job_profile.get("required_skills") or []
        req_experience = job_profile.get("years_experience") or 0.0
        req_industry = (job_profile.get("industry") or "").lower().strip()

        # 2. Query FAISS for all candidates to get the base semantic scores
        total_indexed = vector_store.total_vectors
        if total_indexed == 0:
            return []

        # Generate query embedding vector
        query_embedding = self.openai_service.get_embedding(job_description_text)
        semantic_matches = vector_store.search(query_embedding, top_n=max(100, total_indexed))
        
        matches_dict = {cid: score for cid, score in semantic_matches}

        # 3. Retrieve candidates and compute hybrid scores
        results = []
        for candidate_id, semantic_score in matches_dict.items():
            candidate = db_service.get_candidate(db, candidate_id)
            if not candidate:
                continue

            # Convert DB candidate to schemas to get list formats
            cand_resp = schemas.CandidateResponse.model_validate(candidate)
            
            # --- COMPONENT 1: Semantic Score ---
            # FAISS scores are normalized cosine similarities, clamp to [0.0, 1.0]
            sem_score = max(0.0, min(1.0, semantic_score))

            # --- COMPONENT 2: Skill Overlap Score ---
            cand_skills_lower = {s.lower().strip() for s in cand_resp.skills if s.strip()}
            job_skills_lower = {s.lower().strip() for s in req_skills if s.strip()}
            
            if not job_skills_lower:
                skill_score = 1.0
            else:
                matched_skills_count = 0
                for req_skill in job_skills_lower:
                    # Check for direct overlap or substring containment
                    if any(req_skill in cand or cand in req_skill for cand in cand_skills_lower):
                        matched_skills_count += 1
                skill_score = matched_skills_count / len(job_skills_lower)

            # --- COMPONENT 3: Experience Alignment Score ---
            cand_exp = cand_resp.experience_years or 0.0
            if req_experience <= 0.0:
                exp_score = 1.0
            elif cand_exp >= req_experience:
                exp_score = 1.0
            else:
                exp_score = cand_exp / req_experience  # Linear ratio

            # --- COMPONENT 4: Industry Match Score ---
            if not req_industry:
                ind_score = 1.0
            else:
                # Check candidate parsed resume text or summary text for industry keywords
                resume_text_lower = candidate.parsed_text.lower()
                summary_lower = (candidate.experience or "").lower()
                
                if req_industry in resume_text_lower or req_industry in summary_lower:
                    ind_score = 1.0
                else:
                    # Partial match: split words and check
                    words = [w for w in req_industry.split() if len(w) > 3]
                    if words and any(w in resume_text_lower for w in words):
                        ind_score = 0.5
                    else:
                        ind_score = 0.0

            # --- COMPOSITE SCORE ---
            # Weighted combination: 40% Semantic, 30% Skills, 20% Experience, 10% Industry
            composite_score = (0.4 * sem_score) + (0.3 * skill_score) + (0.2 * exp_score) + (0.1 * ind_score)

            results.append(
                schemas.HybridSearchMatch(
                    candidate=cand_resp,
                    composite_score=round(composite_score, 4),
                    semantic_score=round(sem_score, 4),
                    skill_score=round(skill_score, 4),
                    experience_score=round(exp_score, 4),
                    industry_score=round(ind_score, 4)
                )
            )

        # 4. Sort by composite score descending and slice to top_n (20)
        results.sort(key=lambda x: x.composite_score, reverse=True)
        return results[:top_n]

# Global instance of HybridSearchService
hybrid_search_service = HybridSearchService()
