import os
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "AI Recruiter API"
    API_V1_STR: str = "/api"
    
    # Gemini Settings
    GEMINI_API_KEY: str
    EMBEDDING_MODEL: str = "models/gemini-embedding-2"
    GPT_MODEL: str = "models/gemini-2.5-flash"
    
    # Paths (Absolute paths based on workspace root)
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Storage settings
    @property
    def STORAGE_DIR(self) -> str:
        path = os.path.join(self.BASE_DIR, "storage")
        os.makedirs(path, exist_ok=True)
        return path
    
    @property
    def DATA_DIR(self) -> str:
        path = os.path.join(self.BASE_DIR, "data")
        os.makedirs(path, exist_ok=True)
        return path
    
    @property
    def PROMPTS_DIR(self) -> str:
        path = os.path.join(self.BASE_DIR, "prompts")
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def DATABASE_URL(self) -> str:
        db_path = os.path.join(self.STORAGE_DIR, "recruiter.db")
        return f"sqlite:///{db_path}"
    
    @property
    def FAISS_INDEX_PATH(self) -> str:
        return os.path.join(self.STORAGE_DIR, "faiss_index.bin")
        
    @property
    def VECTOR_IDS_PATH(self) -> str:
        return os.path.join(self.STORAGE_DIR, "vector_ids.json")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
