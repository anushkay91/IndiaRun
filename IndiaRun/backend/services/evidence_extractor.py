import json
import os
from sqlalchemy.orm import Session
from backend.services import db_service
from backend.services.openai_service import OpenAIService
from backend.config import settings

class EvidenceExtractor:
    def __init__(self):
        self.openai_service = OpenAIService()

    def _read_prompt(self, filename: str) -> str:
        prompt_path = os.path.join(settings.PROMPTS_DIR, filename)
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt template not found at: {prompt_path}")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def extract_evidence(self, db: Session, candidate_id: int, topics: list[str]) -> dict:
        """Scan candidate resume text and extract direct quotes matching each of the specified topics."""
        candidate = db_service.get_candidate(db, candidate_id)
        if not candidate:
            raise ValueError(f"Candidate with ID {candidate_id} not found.")

        # 1. Load evidence prompt template
        prompt_template = self._read_prompt("evidence_prompt.txt")
        prompt = prompt_template.format(
            topics=json.dumps(topics),
            resume_text=candidate.parsed_text
        )

        # 2. Call OpenAI / Gemini JSON generation service
        system_instruction = "You are a professional resume audit tool that returns extracted text quotes in JSON format."
        return self.openai_service._generate_json(
            system_instruction=system_instruction,
            prompt=prompt,
            temperature=0.0
        )

# Global instance of EvidenceExtractor
evidence_extractor = EvidenceExtractor()
