from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
import uvicorn
import json
from datetime import datetime

from . import database
from . import services
from .models import DataEntryCreate, DataEntryResponse, DataCheckResponse

# Initialize FastAPI app
app = FastAPI(
    title="Data Redundancy Removal System",
    description="API for identifying and preventing duplicate data entries",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    database.Base.metadata.create_all(bind=database.engine)

@app.post("/api/check", response_model=DataCheckResponse)
async def check_data(
    file: UploadFile = File(...),
    source: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Check if data already exists in the system
    
    - **file**: The file to check
    - **source**: Source identifier (optional)
    - **metadata**: Additional metadata as JSON string (optional)
    """
    try:
        content = await file.read()
        metadata_dict = json.loads(metadata) if metadata else {}
        
        is_duplicate, existing_entry, content_hash = services.DataValidator.validate_data(
            db, content, source=source, metadata=metadata_dict
        )
        
        return {
            "is_duplicate": is_duplicate,
            "content_hash": content_hash,
            "existing_entry": existing_entry.to_dict() if existing_entry else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/submit", response_model=DataEntryResponse)
async def submit_data(
    file: UploadFile = File(...),
    source: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    is_verified: bool = Form(True),
    confidence_score: int = Form(100),
    db: Session = Depends(get_db)
):
    """
    Submit new data to the system
    
    - **file**: The file to store
    - **source**: Source identifier (optional)
    - **metadata**: Additional metadata as JSON string (optional)
    - **is_verified**: Whether the data has been verified (default: True)
    - **confidence_score**: Confidence score (0-100) for data quality (default: 100)
    """
    try:
        content = await file.read()
        metadata_dict = json.loads(metadata) if metadata else {}
        
        entry = services.DataValidator.create_data_entry(
            db=db,
            content=content,
            content_type=file.content_type,
            source=source,
            metadata=metadata_dict,
            is_verified=is_verified,
            confidence_score=confidence_score
        )
        
        return entry.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/entries", response_model=List[DataEntryResponse])
async def list_entries(
    skip: int = 0,
    limit: int = 100,
    content_type: Optional[str] = None,
    verified: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    List all data entries with optional filtering
    """
    query = db.query(database.DataEntry)
    
    if content_type:
        query = query.filter(database.DataEntry.content_type == content_type)
    if verified is not None:
        query = query.filter(database.DataEntry.is_verified == verified)
        
    entries = query.offset(skip).limit(limit).all()
    return [entry.to_dict() for entry in entries]

@app.get("/api/entries/{entry_id}", response_model=DataEntryResponse)
async def get_entry(entry_id: int, db: Session = Depends(get_db)):
    """
    Get a specific data entry by ID
    """
    entry = db.query(database.DataEntry).filter(database.DataEntry.id == entry_id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry.to_dict()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
