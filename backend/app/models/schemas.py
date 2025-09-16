"""
Pydantic models for request/response schemas
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    IMAGE = "image"
    TEXT = "text"


class ProcessingStatus(str, Enum):
    """Document processing status."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    file_type: DocumentType = Field(..., description="Document type")
    file_size: int = Field(..., description="File size in bytes")
    upload_timestamp: datetime = Field(..., description="Upload timestamp")
    status: ProcessingStatus = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")


class DocumentProcessingRequest(BaseModel):
    """Request model for document processing."""
    document_id: str = Field(..., description="Document ID to process")
    simplification_level: str = Field(
        default="standard",
        description="Level of simplification (basic, standard, detailed)"
    )
    include_original: bool = Field(
        default=False,
        description="Include original text in response"
    )
    target_audience: str = Field(
        default="general_public",
        description="Target audience for simplification"
    )


class SimplifiedDocument(BaseModel):
    """Model for simplified document content."""
    document_id: str = Field(..., description="Document identifier")
    original_filename: str = Field(..., description="Original filename")
    
    # Simplified content
    summary: str = Field(..., description="Main summary of the document")
    key_points: List[str] = Field(..., description="Key points in bullet format")
    important_terms: Dict[str, str] = Field(..., description="Important terms and definitions")
    deadlines_obligations: List[str] = Field(..., description="Important deadlines and obligations")
    warnings: List[str] = Field(..., description="Warnings and critical information")
    next_steps: List[str] = Field(..., description="Suggested next steps")
    
    # Metadata
    processing_timestamp: datetime = Field(..., description="Processing timestamp")
    simplification_level: str = Field(..., description="Applied simplification level")
    confidence_score: float = Field(..., ge=0, le=1, description="AI confidence score")
    
    # Optional original content
    original_text: Optional[str] = Field(None, description="Original document text")
    
    # Analytics
    word_count_original: int = Field(..., description="Original word count")
    word_count_simplified: int = Field(..., description="Simplified word count")
    reading_level: str = Field(..., description="Estimated reading level")


class DocumentMetadata(BaseModel):
    """Document metadata model."""
    document_id: str = Field(..., description="Document identifier")
    filename: str = Field(..., description="Original filename")
    file_type: DocumentType = Field(..., description="Document type")
    file_size: int = Field(..., description="File size in bytes")
    upload_timestamp: datetime = Field(..., description="Upload timestamp")
    processing_timestamp: Optional[datetime] = Field(None, description="Processing timestamp")
    status: ProcessingStatus = Field(..., description="Current status")
    user_id: Optional[str] = Field(None, description="User identifier")
    
    # Processing metadata
    extraction_method: Optional[str] = Field(None, description="Text extraction method used")
    ocr_confidence: Optional[float] = Field(None, description="OCR confidence score if applicable")
    language_detected: Optional[str] = Field(None, description="Detected document language")
    
    # Storage information
    storage_path: str = Field(..., description="Cloud storage path")
    processed_path: Optional[str] = Field(None, description="Processed document storage path")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(..., description="Application version")
    services: Dict[str, str] = Field(..., description="Status of individual services")


class AnalyticsData(BaseModel):
    """Analytics data model."""
    document_id: str = Field(..., description="Document identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    action: str = Field(..., description="Action performed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Action timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Performance metrics
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    simplification_level: Optional[str] = Field(None, description="Simplification level used")
    
    # Quality metrics
    confidence_score: Optional[float] = Field(None, description="AI confidence score")
    user_feedback: Optional[str] = Field(None, description="User feedback if provided")


class BatchProcessingRequest(BaseModel):
    """Request model for batch document processing."""
    document_ids: List[str] = Field(..., description="List of document IDs to process")
    simplification_level: str = Field(
        default="standard",
        description="Level of simplification to apply to all documents"
    )
    target_audience: str = Field(
        default="general_public",
        description="Target audience for simplification"
    )
    include_original: bool = Field(
        default=False,
        description="Include original text in responses"
    )


class BatchProcessingResponse(BaseModel):
    """Response model for batch processing."""
    batch_id: str = Field(..., description="Batch processing identifier")
    total_documents: int = Field(..., description="Total number of documents")
    processed_documents: int = Field(..., description="Number of successfully processed documents")
    failed_documents: int = Field(..., description="Number of failed documents")
    results: List[SimplifiedDocument] = Field(..., description="Processing results")
    errors: List[ErrorResponse] = Field(default_factory=list, description="Processing errors")
    processing_time: float = Field(..., description="Total processing time in seconds")


class QARequest(BaseModel):
    """Request model for asking a question about a document."""
    document_id: str = Field(..., description="Document ID to ask about")
    question: str = Field(..., description="User question")
    target_audience: str = Field(default="general_public", description="Audience guidance")


class QAResponse(BaseModel):
    """Response model for Q&A over a document."""
    document_id: str = Field(..., description="Document ID")
    question: str = Field(..., description="User question")
    answer: str = Field(..., description="AI answer in simple terms")
    confidence_score: float = Field(..., ge=0, le=1, description="Answer confidence")
