from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, func, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data_redundancy.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class DataEntry(Base):
    """Database model for storing unique data entries"""
    __tablename__ = "data_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    content_hash = Column(String(128), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50))
    is_verified = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional metadata columns for better classification
    source = Column(String(100))
    confidence_score = Column(Integer, default=100)  # 0-100 scale
    
    # Create an index on frequently queried fields
    __table_args__ = (
        Index('idx_content_type_verified', 'content_type', 'is_verified'),
    )

# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
