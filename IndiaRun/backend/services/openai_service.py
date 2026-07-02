import json
import os
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from backend.config import settings

class OpenAIService:
    def __init__(self):
        # pyrefly: ignore [missing-import]
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.embedding_model = settings.EMBEDDING_MODEL
        self.gpt_model = settings.GPT_MODEL

    def _read_prompt(self, filename: str) -> str:
        prompt_path = os.path.join(settings.PROMPTS_DIR, filename)
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt template not found at: {prompt_path}")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_embedding(self, text: str) -> list[float]:
        """Generate embedding vector using text-embedding-004."""
        cleaned_text = text.replace("\n", " ")
        # pyrefly: ignore [missing-import]
        result = genai.embed_content(
            model=self.embedding_model,
            contents=cleaned_text,
            task_type="retrieval_document"
        )
        return result['embedding']

    def _generate_json(self, system_instruction: str, prompt: str, temperature: float = 0.1) -> dict:
        # pyrefly: ignore [missing-import]
        model = genai.GenerativeModel(
            model_name=self.gpt_model,
            system_instruction=system_instruction
        )
        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": temperature
            }
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())

    def parse_resume(self, raw_text: str) -> dict:
        """Parse raw resume text into structured JSON candidate metadata."""
        prompt_template = self._read_prompt("parsing_prompt.txt")
        prompt = prompt_template.format(resume_text=raw_text)
        system_instruction = "You are a professional resume parsing tool that returns output in JSON format."
        return self._generate_json(system_instruction, prompt, temperature=0.1)

    def screen_candidate(self, resume_text: str, job_description: str) -> dict:
        """Screen candidate resume against job description and return JSON report."""
        prompt_template = self._read_prompt("screening_prompt.txt")
        prompt = prompt_template.format(
            job_description=job_description,
            resume_text=resume_text
        )
        system_instruction = "You are an AI recruiting consultant who screen candidates and returns analysis in JSON format."
        return self._generate_json(system_instruction, prompt, temperature=0.2)

    def chat_with_candidate(self, resume_text: str, question: str, history: list[dict]) -> str:
        """Chat with candidate resume context."""
        system_instruction = (
            "You are a talent screening assistant. You are helping a recruiter evaluate a candidate by answering questions "
            "directly and objectively based on the candidate's resume provided below.\n\n"
            f"--- CANDIDATE RESUME START ---\n{resume_text}\n--- CANDIDATE RESUME END ---\n\n"
            "Guidelines:\n"
            "1. Answer questions concisely and only reference the facts in the resume.\n"
            "2. If the user asks something not present or inferable from the resume, state that the information is not provided.\n"
            "3. Be polite, professional, and helpful."
        )

        # pyrefly: ignore [missing-import]
        model = genai.GenerativeModel(
            model_name=self.gpt_model,
            system_instruction=system_instruction
        )
        
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [msg["content"]]})
            
        contents.append({"role": "user", "parts": [question]})
        
        response = model.generate_content(
            contents,
            generation_config={"temperature": 0.2}
        )
        return response.text

    def analyze_job(self, raw_jd: str) -> dict:
        """Parse raw job description text into structured JSON metadata."""
        prompt_template = self._read_prompt("job_analysis_prompt.txt")
        prompt = prompt_template.format(job_description=raw_jd)
        system_instruction = "You are a professional job analysis tool that returns output in JSON format."
        return self._generate_json(system_instruction, prompt, temperature=0.1)

    def analyze_candidate_profile(self, candidate_json: dict) -> dict:
        """Analyze a parsed resume profile and generate structured evaluations."""
        prompt_template = self._read_prompt("candidate_analysis_prompt.txt")
        prompt = prompt_template.format(candidate_json=json.dumps(candidate_json))
        system_instruction = "You are a professional talent evaluation tool that returns output in JSON format."
        return self._generate_json(system_instruction, prompt, temperature=0.15)

    def rerank_candidate(self, job_profile: dict, candidate_profile: dict) -> dict:
        """Deeply compare a structured Job Profile and Candidate Profile to evaluate role fit."""
        prompt_template = self._read_prompt("reranking_prompt.txt")
        prompt = prompt_template.format(
            job_profile=json.dumps(job_profile),
            candidate_profile=json.dumps(candidate_profile)
        )
        system_instruction = "You are an expert executive talent assessor that returns profile comparisons in JSON format."
        return self._generate_json(system_instruction, prompt, temperature=0.1)

    def analyze_skill_gap(self, job_profile: dict, candidate_profile: dict) -> dict:
        """Execute structured technical skill gap analysis comparing Job and Candidate profiles."""
        prompt_template = self._read_prompt("skill_gap_prompt.txt")
        prompt = prompt_template.format(
            job_profile=json.dumps(job_profile),
            candidate_profile=json.dumps(candidate_profile)
        )
        system_instruction = "You are a professional technical training and gap analysis tool that returns JSON outputs."
        return self._generate_json(system_instruction, prompt, temperature=0.15)

    def generate_interview_plan(self, job_profile: dict, candidate_profile: dict) -> dict:
        """Generate structured custom interview plan comparing Job and Candidate profiles."""
        prompt_template = self._read_prompt("interview_planner_prompt.txt")
        prompt = prompt_template.format(
            job_profile=json.dumps(job_profile),
            candidate_profile=json.dumps(candidate_profile)
        )
        system_instruction = "You are a professional interview coaching and planner tool that returns JSON outputs."
        return self._generate_json(system_instruction, prompt, temperature=0.2)

    def chat_with_recruiter(self, message: str, history: list, candidates: list, job_description: str) -> str:
        """Converse with the recruiter using complete candidates list and job context."""
        system_instruction = (
            "You are TalentPool AI, an elite recruiting partner and talent advisor.\n"
            "Below is the list of candidates currently indexed in our system, along with the Job Description details (if available).\n\n"
            f"Target Job Description:\n{job_description or 'No active job description loaded.'}\n\n"
            f"Indexed Candidates Context:\n{json.dumps(candidates)}\n\n"
            "Answer the recruiter's questions professionally using recruiter terminology. When asked to compare, provide structured bulleted comparisons. If asked about missing skills, list them. If asked about trade-offs (e.g. if AWS becomes optional), re-assess candidate fit. Support questions like:\n"
            "- 'Why Candidate A?'\n"
            "- 'Compare Candidate A and B.'\n"
            "- 'Show missing skills.'\n"
            "- 'Who has stronger leadership?'\n"
            "- 'Recommend better fit if AWS becomes optional.'"
        )

        # pyrefly: ignore [missing-import]
        model = genai.GenerativeModel(
            model_name=self.gpt_model,
            system_instruction=system_instruction
        )
        
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [msg["content"]]})
            
        contents.append({"role": "user", "parts": [message]})
        
        response = model.generate_content(
            contents,
            generation_config={"temperature": 0.3}
        )
        return response.text
