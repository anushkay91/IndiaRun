import json
from sqlalchemy.orm import Session
from backend.database import Candidate
from backend import schemas
from backend.services import db_service
from backend.services.openai_service import OpenAIService
from backend.services.vector_store import vector_store

class EmbeddingService:
    def __init__(self):
        self.openai_service = OpenAIService()

    def _build_composite_text(self, candidate: Candidate) -> str:
        """Helper to build a structured text representation of candidate fields for embedding."""
        # Validate through Pydantic to handle list deserializations from SQLite
        cand_schema = schemas.CandidateResponse.model_validate(candidate)
        
        parts = []
        if cand_schema.name:
            parts.append(f"Candidate Name: {cand_schema.name}")
        if cand_schema.experience:
            parts.append(f"Resume Summary: {cand_schema.experience}")
        if cand_schema.experience_years:
            parts.append(f"Years of Experience: {cand_schema.experience_years}")
        if cand_schema.skills:
            parts.append(f"Skills: {', '.join(cand_schema.skills)}")
        if cand_schema.projects:
            parts.append(f"Projects: {', '.join(cand_schema.projects)}")
        if cand_schema.education:
            parts.append(f"Education: {cand_schema.education}")
        if cand_schema.work_history:
            parts.append(f"Work History: {', '.join(cand_schema.work_history)}")
        if cand_schema.achievements:
            parts.append(f"Achievements: {', '.join(cand_schema.achievements)}")
            
        return "\n".join(parts)

    def index_candidate(self, db: Session, candidate_id: int) -> None:
        """Embed candidate composite text, update their SQLite record, and insert into FAISS index."""
        candidate = db_service.get_candidate(db, candidate_id)
        if not candidate:
            raise ValueError(f"Candidate with ID {candidate_id} not found.")

        # 1. Build composite text
        composite_text = self._build_composite_text(candidate)

        # 2. Call OpenAI to generate embedding vector
        embedding_vector = self.openai_service.get_embedding(composite_text)

        # 3. Save serialized embedding back to the SQLite DB
        candidate.embedding = json.dumps(embedding_vector)
        db.commit()

        # 4. Sync FAISS by rebuilding from DB to maintain strict alignment of indices
        remaining_embeddings = db_service.get_all_embeddings(db)
        vector_store.rebuild(remaining_embeddings)

    def search(self, db: Session, query_text: str, top_n: int = 5) -> list[schemas.SearchMatch]:
        """Generate query vector and query FAISS for candidate matches."""
        # Generate embedding for the search query/job description
        query_embedding = self.openai_service.get_embedding(query_text)
        
        # Search the FAISS vector index
        matches = vector_store.search(query_embedding, top_n=top_n)
        
        results = []
        for candidate_id, score in matches:
            candidate = db_service.get_candidate(db, candidate_id)
            if candidate:
                results.append(
                    schemas.SearchMatch(
                        candidate=schemas.CandidateResponse.model_validate(candidate),
                        score=score
                    )
                )
        
        return results

    def update(self, db: Session, candidate_id: int) -> None:
        """Update candidate embedding in DB and FAISS (identical flow to index_candidate)."""
        self.index_candidate(db, candidate_id)

    def delete(self, db: Session, candidate_id: int) -> bool:
        """Delete candidate from SQLite and remove their embedding vector from FAISS."""
        # Delete from DB
        success = db_service.delete_candidate(db, candidate_id)
        if success:
            # Rebuild the FAISS index from the remaining database entries
            remaining = db_service.get_all_embeddings(db)
            vector_store.rebuild(remaining)
        return success

# Global instance of EmbeddingService
embedding_service = EmbeddingService()
