"""Database models and setup for Research Agent System."""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from pathlib import Path

# Database setup
BASE_DIR = Path(__file__).parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'research_agent.db'}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    full_name = Column(String, nullable=True)
    provider = Column(String, nullable=False, default="local")  # local, google, facebook
    provider_id = Column(String, nullable=True)  # OAuth provider user ID
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)
    
    # Relationships
    research_history = relationship("ResearchHistory", back_populates="user")


class ResearchHistory(Base):
    """Research history model to store user research results."""
    __tablename__ = "research_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)
    requirements = Column(Text, nullable=True)
    draft = Column(Text, nullable=False)
    improved_draft = Column(Text, nullable=False)
    changes_summary = Column(Text, nullable=True)
    sources_count = Column(Integer, default=0)
    queries_count = Column(Integer, default=0)
    md_filename = Column(String, nullable=True)
    docx_filename = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="research_history")


# Create tables
def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

