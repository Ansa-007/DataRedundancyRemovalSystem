from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

class DataEntryBase(BaseModel):
    """Base model for data entries"""
    content: str
    content_type: str
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    is_verified: bool = True
    confidence_score: int = Field(..., ge=0, le=100)

class DataEntryCreate(DataEntryBase):
    """Model for creating new data entries"""
    pass

class DataEntryResponse(DataEntryBase):
    """Response model for data entries"""
    id: int
    content_hash: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DataCheckResponse(BaseModel):
    """Response model for duplicate check"""
    is_duplicate: bool
    content_hash: str
    existing_entry: Optional[DataEntryResponse] = None

    class Config:
        orm_mode = True

class DataEntryUpdate(BaseModel):
    """Model for updating data entries"""
    is_verified: Optional[bool] = None
    confidence_score: Optional[int] = Field(None, ge=0, le=100)
    metadata: Optional[Dict[str, Any]] = None

    @validator('metadata')
    def validate_metadata(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError("metadata must be a dictionary")
        return v
