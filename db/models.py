from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import hashlib
import io

@dataclass
class CVFileMetadata:
    """Data model for CV file metadata stored in MongoDB."""
    
    filename: str
    file_size: int
    file_hash: str
    upload_date: datetime
    content_type: str
    analysis_results: Optional[Dict[str, Any]] = None
    job_description: Optional[str] = None
    match_score: Optional[int] = None
    missing_skills: Optional[list] = None
    profile_summary: Optional[str] = None
    questions: Optional[list] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the dataclass to a dictionary for MongoDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CVFileMetadata':
        """Create CVFileMetadata instance from MongoDB document."""
        return cls(**data)
    
    @staticmethod
    def calculate_file_hash(file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content for duplicate detection."""
        return hashlib.sha256(file_content).hexdigest()
    
    @classmethod
    def create_from_upload(cls, 
                          uploaded_file, 
                          file_content: bytes,
                          job_description: Optional[str] = None) -> 'CVFileMetadata':
        """Create CVFileMetadata from Streamlit uploaded file."""
        return cls(
            filename=uploaded_file.name,
            file_size=len(file_content),
            file_hash=cls.calculate_file_hash(file_content),
            upload_date=datetime.utcnow(),
            content_type=uploaded_file.type,
            job_description=job_description
        )
    
    def update_analysis_results(self, 
                              analysis_result: Dict[str, Any]) -> None:
        """Update the metadata with analysis results."""
        self.analysis_results = analysis_result
        self.match_score = analysis_result.get('score')
        self.missing_skills = analysis_result.get('missing_skills')
        self.profile_summary = analysis_result.get('summary')
        self.questions = analysis_result.get('questions')

@dataclass
class CVSearchQuery:
    """Data model for searching CV files."""
    
    filename: Optional[str] = None
    min_match_score: Optional[int] = None
    max_match_score: Optional[int] = None
    job_description: Optional[str] = None
    upload_date_from: Optional[datetime] = None
    upload_date_to: Optional[datetime] = None
    has_analysis: Optional[bool] = None
    
    def to_mongo_filter(self) -> Dict[str, Any]:
        """Convert search query to MongoDB filter."""
        filter_dict = {}
        
        if self.filename:
            filter_dict["filename"] = {"$regex": self.filename, "$options": "i"}
        
        if self.min_match_score is not None or self.max_match_score is not None:
            score_filter = {}
            if self.min_match_score is not None:
                score_filter["$gte"] = self.min_match_score
            if self.max_match_score is not None:
                score_filter["$lte"] = self.max_match_score
            filter_dict["match_score"] = score_filter
        
        if self.job_description:
            filter_dict["job_description"] = {"$regex": self.job_description, "$options": "i"}
        
        if self.upload_date_from or self.upload_date_to:
            date_filter = {}
            if self.upload_date_from:
                date_filter["$gte"] = self.upload_date_from
            if self.upload_date_to:
                date_filter["$lte"] = self.upload_date_to
            filter_dict["upload_date"] = date_filter
        
        if self.has_analysis is not None:
            if self.has_analysis:
                filter_dict["analysis_results"] = {"$ne": None}
            else:
                filter_dict["analysis_results"] = None
        
        return filter_dict
