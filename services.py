import hashlib
import magic
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from . import database
import blake3
import json
from datetime import datetime

class DataValidationError(Exception):
    """Custom exception for data validation errors"""
    pass

class DataValidator:
    """Handles data validation and deduplication"""
    
    @staticmethod
    def generate_hash(content: bytes) -> str:
        """Generate a BLAKE3 hash of the content"""
        return blake3.blake3(content).hexdigest()
    
    @staticmethod
    def detect_content_type(content: bytes) -> str:
        """Detect the content type using python-magic"""
        mime = magic.Magic(mime=True)
        return mime.from_buffer(content)
    
    @classmethod
    def validate_data(
        cls,
        db: Session,
        content: bytes,
        content_type: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[database.DataEntry], str]:
        """
        Validate data and check for duplicates
        
        Returns:
            tuple: (is_duplicate, existing_entry, content_hash)
        """
        # Generate content hash
        content_hash = cls.generate_hash(content)
        
        # Check if content already exists
        existing_entry = (
            db.query(database.DataEntry)
            .filter(database.DataEntry.content_hash == content_hash)
            .first()
        )
        
        if existing_entry:
            return True, existing_entry, content_hash
            
        # If no existing entry, detect content type if not provided
        if content_type is None:
            content_type = cls.detect_content_type(content)
        
        return False, None, content_hash
    
    @classmethod
    def create_data_entry(
        cls,
        db: Session,
        content: bytes,
        content_type: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_verified: bool = True,
        confidence_score: int = 100
    ) -> database.DataEntry:
        """Create a new data entry if it doesn't exist"""
        is_duplicate, existing_entry, content_hash = cls.validate_data(
            db, content, content_type, source, metadata
        )
        
        if is_duplicate and existing_entry:
            return existing_entry
            
        # If we get here, it's a new entry
        if content_type is None:
            content_type = cls.detect_content_type(content)
            
        # Prepare content for storage (convert to string if it's JSON-able)
        try:
            content_str = content.decode('utf-8')
            try:
                # If it's JSON, store it as pretty-printed JSON
                json_content = json.loads(content_str)
                content_str = json.dumps(json_content, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                pass
        except UnicodeDecodeError:
            # If it's binary data, store as base64
            import base64
            content_str = base64.b64encode(content).decode('utf-8')
            
        # Create new entry
        new_entry = database.DataEntry(
            content_hash=content_hash,
            content=content_str,
            content_type=content_type,
            is_verified=is_verified,
            source=source,
            confidence_score=min(max(confidence_score, 0), 100)  # Ensure score is between 0-100
        )
        
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        
        return new_entry
