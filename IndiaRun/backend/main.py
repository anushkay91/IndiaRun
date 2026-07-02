from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import init_db, SessionLocal
from backend.routers import candidates, search, jobs
from backend.services import db_service
from backend.services.vector_store import vector_store

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize SQLite Database Tables
    init_db()
    
    # 2. Populate/rebuild FAISS vector store index on startup
    db = SessionLocal()
    try:
        candidate_embeddings = db_service.get_all_embeddings(db)
        vector_store.rebuild(candidate_embeddings)
        print(f"FAISS index successfully initialized with {vector_store.total_vectors} candidate profiles.")
    except Exception as e:
        print(f"Warning: Failed to load FAISS index on startup: {str(e)}")
    finally:
        db.close()
        
    yield
    # Shutdown logic (if any) goes here

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    description="Backend API for candidate resume parsing, indexing, semantic matching, and AI screening.",
    version="1.0.0"
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(candidates.router, prefix=settings.API_V1_STR)
app.include_router(search.router, prefix=settings.API_V1_STR)
app.include_router(jobs.router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "app": settings.PROJECT_NAME,
        "status": "online",
        "indexed_candidates": vector_store.total_vectors
    }
