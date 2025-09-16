"""
API routes for the AI Legal Document Simplifier
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks, status
from fastapi.responses import JSONResponse
from typing import List, Optional
import uuid
from datetime import datetime
import logging

from app.models.schemas import (
    DocumentUploadResponse, DocumentProcessingRequest, SimplifiedDocument,
    DocumentMetadata, ErrorResponse, HealthCheckResponse, BatchProcessingRequest,
    BatchProcessingResponse, ProcessingStatus, DocumentType, QARequest, QAResponse
)
from app.services.document_processor import DocumentProcessor
from app.services.ai_simplifier import AISimplifier
from app.services.storage_service import StorageService
from app.services.analytics_service import AnalyticsService
from app.core.config import settings

# Create router instances
health_router = APIRouter()
document_router = APIRouter()

# Service dependencies (will be injected)
async def get_document_processor() -> DocumentProcessor:
    return DocumentProcessor()

async def get_ai_simplifier() -> AISimplifier:
    return AISimplifier()

async def get_storage_service() -> StorageService:
    service = StorageService()
    await service.initialize()
    return service

async def get_analytics_service() -> AnalyticsService:
    service = AnalyticsService()
    await service.initialize()
    return service


@health_router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint to verify service status."""
    try:
        # Check service dependencies
        services_status = {
            "api": "healthy",
            "storage": "healthy",
            "ai_service": "healthy",
            "analytics": "healthy"
        }
        
        # Check Google Cloud services health
        try:
            from app.services.storage_service import StorageService
            from app.services.ai_simplifier import AISimplifier
            
            storage_service = StorageService()
            await storage_service.initialize()
            
            ai_simplifier = AISimplifier()
            
            services_status.update({
                "storage": "healthy",
                "ai_service": "healthy"
            })
        except Exception as e:
            services_status.update({
                "storage": "unhealthy",
                "ai_service": "unhealthy"
            })
            logging.warning(f"Service health check failed: {e}")
        
        return HealthCheckResponse(
            status="healthy",
            version=settings.VERSION,
            services=services_status
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@document_router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: Optional[str] = None,
    storage_service: StorageService = Depends(get_storage_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Upload a legal document for processing."""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Check file type
        if file.content_type not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not supported"
            )
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Determine document type
        file_extension = file.filename.split('.')[-1].lower()
        document_type_map = {
            'pdf': DocumentType.PDF,
            'doc': DocumentType.DOC,
            'docx': DocumentType.DOCX,
            'jpg': DocumentType.IMAGE,
            'jpeg': DocumentType.IMAGE,
            'png': DocumentType.IMAGE,
            'tiff': DocumentType.IMAGE,
            'txt': DocumentType.TEXT
        }
        document_type = document_type_map.get(file_extension, DocumentType.TEXT)
        
        # Upload to cloud storage
        storage_path = await storage_service.upload_document(
            document_id=document_id,
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        # Extract document metadata for better processing
        document_processor = DocumentProcessor()
        doc_metadata = await document_processor.get_document_metadata(file_content, document_type)
        
        # Create document metadata
        document_metadata = DocumentMetadata(
            document_id=document_id,
            filename=file.filename,
            file_type=document_type,
            file_size=len(file_content),
            upload_timestamp=datetime.utcnow(),
            status=ProcessingStatus.UPLOADED,
            user_id=user_id,
            storage_path=storage_path,
            extraction_method=doc_metadata.get("extraction_method"),
            ocr_confidence=doc_metadata.get("ocr_confidence"),
            language_detected=doc_metadata.get("language_detected")
        )
        
        # Store metadata
        await storage_service.store_metadata(document_metadata)
        
        # Track analytics
        background_tasks.add_task(
            analytics_service.track_document_upload,
            document_id=document_id,
            user_id=user_id,
            file_size=len(file_content),
            file_type=document_type.value
        )
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            file_type=document_type,
            file_size=len(file_content),
            upload_timestamp=document_metadata.upload_timestamp,
            status=ProcessingStatus.UPLOADED,
            message="Document uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}"
        )


@document_router.post("/documents/{document_id}/process", response_model=SimplifiedDocument)
async def process_document(
    document_id: str,
    request: DocumentProcessingRequest,
    background_tasks: BackgroundTasks,
    document_processor: DocumentProcessor = Depends(get_document_processor),
    ai_simplifier: AISimplifier = Depends(get_ai_simplifier),
    storage_service: StorageService = Depends(get_storage_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Process and simplify a legal document."""
    try:
        # Get document metadata
        metadata = await storage_service.get_document_metadata(document_id)
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Update status to processing (non-fatal if BigQuery update fails)
        metadata.status = ProcessingStatus.PROCESSING
        try:
            await storage_service.update_metadata(metadata)
        except Exception as e:
            logging.warning(f"Failed to update metadata to PROCESSING for {document_id}: {e}")
        
        # Extract text from document
        extracted_text = await document_processor.extract_text(
            document_id=document_id,
            file_type=metadata.file_type,
            storage_path=metadata.storage_path
        )
        
        if not extracted_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not extract text from document"
            )
        
        # Simplify using AI
        simplified_content = await ai_simplifier.simplify_document(
            text=extracted_text,
            simplification_level=request.simplification_level,
            target_audience=request.target_audience
        )
        
        # Create simplified document response
        simplified_doc = SimplifiedDocument(
            document_id=document_id,
            original_filename=metadata.filename,
            summary=simplified_content.get("summary", ""),
            key_points=simplified_content.get("key_points", []),
            important_terms=simplified_content.get("important_terms", {}),
            deadlines_obligations=simplified_content.get("deadlines_obligations", []),
            warnings=simplified_content.get("warnings", []),
            next_steps=simplified_content.get("next_steps", []),
            processing_timestamp=datetime.utcnow(),
            simplification_level=request.simplification_level,
            confidence_score=simplified_content.get("confidence_score", 0.8),
            original_text=extracted_text if request.include_original else None,
            word_count_original=len(extracted_text.split()),
            word_count_simplified=len(simplified_content.get("summary", "").split()),
            reading_level=simplified_content.get("reading_level", "intermediate")
        )
        
        # Update metadata (non-fatal if BigQuery update fails)
        metadata.status = ProcessingStatus.COMPLETED
        metadata.processing_timestamp = datetime.utcnow()
        try:
            await storage_service.update_metadata(metadata)
        except Exception as e:
            logging.warning(f"Failed to update metadata to COMPLETED for {document_id}: {e}")
        
        # Store simplified document
        await storage_service.store_simplified_document(simplified_doc)
        
        # Track analytics
        background_tasks.add_task(
            analytics_service.track_document_processing,
            document_id=document_id,
            processing_time=0,  # TODO: Calculate actual processing time
            simplification_level=request.simplification_level,
            confidence_score=simplified_doc.confidence_score
        )
        
        return simplified_doc
        
    except HTTPException:
        raise
    except Exception as e:
        # Update status to failed
        try:
            metadata = await storage_service.get_document_metadata(document_id)
            if metadata:
                metadata.status = ProcessingStatus.FAILED
                await storage_service.update_metadata(metadata)
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@document_router.get("/documents/{document_id}", response_model=SimplifiedDocument)
async def get_simplified_document(
    document_id: str,
    storage_service: StorageService = Depends(get_storage_service)
):
    """Retrieve a previously processed document."""
    try:
        simplified_doc = await storage_service.get_simplified_document(document_id)
        if not simplified_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simplified document not found"
            )
        
        return simplified_doc
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document: {str(e)}"
        )


@document_router.get("/documents/{document_id}/metadata", response_model=DocumentMetadata)
async def get_document_metadata(
    document_id: str,
    storage_service: StorageService = Depends(get_storage_service)
):
    """Get document metadata."""
    try:
        metadata = await storage_service.get_document_metadata(document_id)
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document metadata not found"
            )
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving metadata: {str(e)}"
        )


@document_router.post("/documents/batch/process", response_model=BatchProcessingResponse)
async def batch_process_documents(
    request: BatchProcessingRequest,
    background_tasks: BackgroundTasks,
    document_processor: DocumentProcessor = Depends(get_document_processor),
    ai_simplifier: AISimplifier = Depends(get_ai_simplifier),
    storage_service: StorageService = Depends(get_storage_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Process multiple documents in batch."""
    try:
        batch_id = str(uuid.uuid4())
        results = []
        errors = []
        
        for document_id in request.document_ids:
            try:
                # Create individual processing request
                individual_request = DocumentProcessingRequest(
                    document_id=document_id,
                    simplification_level=request.simplification_level,
                    include_original=request.include_original,
                    target_audience=request.target_audience
                )
                
                # Process document
                simplified_doc = await process_document(
                    document_id=document_id,
                    request=individual_request,
                    background_tasks=background_tasks,
                    document_processor=document_processor,
                    ai_simplifier=ai_simplifier,
                    storage_service=storage_service,
                    analytics_service=analytics_service
                )
                
                results.append(simplified_doc)
                
            except Exception as e:
                errors.append(ErrorResponse(
                    error="processing_error",
                    message=f"Failed to process document {document_id}",
                    detail=str(e)
                ))
        
        return BatchProcessingResponse(
            batch_id=batch_id,
            total_documents=len(request.document_ids),
            processed_documents=len(results),
            failed_documents=len(errors),
            results=results,
            errors=errors,
            processing_time=0  # TODO: Calculate actual processing time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch processing: {str(e)}"
        )


@document_router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    storage_service: StorageService = Depends(get_storage_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Delete a document and its associated data."""
    try:
        # Get metadata first
        metadata = await storage_service.get_document_metadata(document_id)
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete from storage
        await storage_service.delete_document(document_id)
        
        # Track deletion
        await analytics_service.track_document_deletion(document_id)
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )


@document_router.post("/documents/{document_id}/qa", response_model=QAResponse)
async def ask_document_question(
    document_id: str,
    request: QARequest,
    document_processor: DocumentProcessor = Depends(get_document_processor),
    ai_simplifier: AISimplifier = Depends(get_ai_simplifier),
    storage_service: StorageService = Depends(get_storage_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Answer a user question based on the uploaded document content."""
    try:
        # Validate document
        metadata = await storage_service.get_document_metadata(document_id)
        if not metadata:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        # Extract text from storage
        extracted_text = await document_processor.extract_text(
            document_id=document_id,
            file_type=metadata.file_type,
            storage_path=metadata.storage_path
        )
        if not extracted_text:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Could not extract text from document")

        # Get answer
        qa = await ai_simplifier.answer_question(extracted_text, request.question, request.target_audience)

        # Track analytics (non-blocking)
        try:
            await analytics_service._insert_analytics_record({
                "document_id": document_id,
                "user_id": None,
                "action": "document_qa",
                "timestamp": datetime.utcnow(),
                "metadata": {"question": request.question},
                "confidence_score": qa.get("confidence_score")
            })
        except Exception as e:
            logging.warning(f"Failed to track QA analytics for {document_id}: {e}")

        return QAResponse(
            document_id=document_id,
            question=request.question,
            answer=qa.get("answer", ""),
            confidence_score=qa.get("confidence_score", 0.5)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error answering question: {str(e)}")
