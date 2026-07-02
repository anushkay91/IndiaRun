import datetime
from sqlalchemy import create_engine, String, Text, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from backend.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), unique=True, index=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)  # Comma-separated list
    experience_years: Mapped[float] = mapped_column(Float, default=0.0)
    experience: Mapped[str | None] = mapped_column(Text, nullable=True)
    projects: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON or newline-separated list
    education: Mapped[str | None] = mapped_column(Text, nullable=True)
    certifications: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON or newline-separated list
    work_history: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON or newline-separated list
    achievements: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON or newline-separated list
    resume_filename: Mapped[str] = mapped_column(String(255))
    parsed_text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)  # Store embedding as JSON float array
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, 
        default=datetime.datetime.utcnow
    )

def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """DB session generator dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
