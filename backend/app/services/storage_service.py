"""
Google Cloud Storage service for document and metadata management
"""

import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
from io import BytesIO

from google.cloud import storage
from google.cloud import bigquery
from google.cloud.exceptions import NotFound, GoogleCloudError

from app.models.schemas import DocumentMetadata, SimplifiedDocument, ProcessingStatus
from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing document storage and metadata in Google Cloud."""
    
    def __init__(self):
        self.storage_client = None
        self.bigquery_client = None
        self.bucket = None
        self.dataset = None
        
    async def initialize(self):
        """Initialize Google Cloud clients and resources."""
        try:
            if not settings.CLOUD_STORAGE_BUCKET:
                raise ValueError("CLOUD_STORAGE_BUCKET is not set. Please set it in your environment.")
            # Initialize Cloud Storage client
            self.storage_client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT_ID)
            self.bucket = self.storage_client.bucket(settings.CLOUD_STORAGE_BUCKET)
            
            # Initialize BigQuery client
            self.bigquery_client = bigquery.Client(project=settings.GOOGLE_CLOUD_PROJECT_ID)
            self.dataset = self.bigquery_client.dataset(settings.BIGQUERY_DATASET)
            
            # Ensure bucket exists
            await self._ensure_bucket_exists()
            
            # Ensure BigQuery dataset and tables exist
            await self._ensure_bigquery_tables_exist()
            
            logger.info("Storage service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize storage service: {e}")
            raise
    
    async def _ensure_bucket_exists(self):
        """Ensure the Cloud Storage bucket exists."""
        try:
            if not self.bucket.exists():
                self.bucket = self.storage_client.create_bucket(
                    settings.CLOUD_STORAGE_BUCKET,
                    location="us-central1"
                )
                logger.info(f"Created bucket: {settings.CLOUD_STORAGE_BUCKET}")
            else:
                logger.info(f"Bucket exists: {settings.CLOUD_STORAGE_BUCKET}")
        except Exception as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise
    
    async def _ensure_bigquery_tables_exist(self):
        """Ensure BigQuery dataset and tables exist."""
        try:
            # Create dataset if it doesn't exist
            try:
                # Use DatasetReference directly
                self.bigquery_client.get_dataset(self.dataset)
            except NotFound:
                self.bigquery_client.create_dataset(self.dataset)
                logger.info(f"Created BigQuery dataset: {settings.BIGQUERY_DATASET}")
            
            # Create usage analytics table
            usage_table_id = f"{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE_USAGE}"
            usage_schema = [
                bigquery.SchemaField("document_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("user_id", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("action", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
                bigquery.SchemaField("processing_time", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("file_size", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("simplification_level", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("confidence_score", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("user_feedback", "STRING", mode="NULLABLE"),
            ]
            
            try:
                self.bigquery_client.get_table(usage_table_id)
            except NotFound:
                table = bigquery.Table(usage_table_id, schema=usage_schema)
                self.bigquery_client.create_table(table)
                logger.info(f"Created BigQuery table: {settings.BIGQUERY_TABLE_USAGE}")
            
            # Create document metadata table
            metadata_table_id = f"{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE_DOCUMENTS}"
            metadata_schema = [
                bigquery.SchemaField("document_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("filename", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("file_type", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("file_size", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("upload_timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("processing_timestamp", "TIMESTAMP", mode="NULLABLE"),
                bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("user_id", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("extraction_method", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("ocr_confidence", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("language_detected", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("storage_path", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("processed_path", "STRING", mode="NULLABLE"),
            ]
            
            try:
                self.bigquery_client.get_table(metadata_table_id)
            except NotFound:
                table = bigquery.Table(metadata_table_id, schema=metadata_schema)
                self.bigquery_client.create_table(table)
                logger.info(f"Created BigQuery table: {settings.BIGQUERY_TABLE_DOCUMENTS}")
            
            # Create processing results table for structured analytics
            results_table_id = f"{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.processing_results"
            results_schema = [
                bigquery.SchemaField("document_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("processing_timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("simplification_level", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("confidence_score", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("word_count_original", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("word_count_simplified", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("reading_level", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("processing_time_seconds", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("extraction_method", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("language_detected", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("has_warnings", "BOOLEAN", mode="REQUIRED"),
                bigquery.SchemaField("has_deadlines", "BOOLEAN", mode="REQUIRED"),
                bigquery.SchemaField("key_points_count", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("important_terms_count", "INTEGER", mode="REQUIRED"),
            ]
            
            try:
                self.bigquery_client.get_table(results_table_id)
            except NotFound:
                table = bigquery.Table(results_table_id, schema=results_schema)
                self.bigquery_client.create_table(table)
                logger.info(f"Created BigQuery table: processing_results")
                
        except Exception as e:
            logger.error(f"Error ensuring BigQuery tables exist: {e}")
            raise
    
    async def upload_document(
        self, 
        document_id: str, 
        file_content: bytes, 
        filename: str, 
        content_type: str
    ) -> str:
        """Upload a document to Cloud Storage."""
        try:
            # Create blob path
            blob_path = f"{settings.UPLOAD_FOLDER}/{document_id}/{filename}"
            blob = self.bucket.blob(blob_path)
            
            # Upload file content
            blob.upload_from_string(
                file_content,
                content_type=content_type
            )
            
            logger.info(f"Uploaded document {document_id} to {blob_path}")
            return blob_path
            
        except Exception as e:
            logger.error(f"Error uploading document {document_id}: {e}")
            raise
    
    async def download_document(self, storage_path: str) -> Optional[bytes]:
        """Download a document from Cloud Storage."""
        try:
            blob = self.bucket.blob(storage_path)
            if not blob.exists():
                logger.error(f"Document not found at path: {storage_path}")
                return None
            
            content = blob.download_as_bytes()
            logger.info(f"Downloaded document from {storage_path}")
            return content
            
        except Exception as e:
            logger.error(f"Error downloading document from {storage_path}: {e}")
            return None
    
    def _serialize_metadata_to_bq_row(self, metadata: DocumentMetadata) -> Dict[str, Any]:
        """Convert DocumentMetadata into a strict JSON-serializable dict for BigQuery."""
        try:
            row: Dict[str, Any] = {
                "document_id": str(metadata.document_id),
                "filename": str(metadata.filename),
                "file_type": str(metadata.file_type.value),
                "file_size": int(metadata.file_size),
                "upload_timestamp": metadata.upload_timestamp.isoformat(),
                "processing_timestamp": metadata.processing_timestamp.isoformat() if metadata.processing_timestamp else None,
                "status": str(metadata.status.value),
                "user_id": str(metadata.user_id) if metadata.user_id else None,
                "extraction_method": str(metadata.extraction_method) if metadata.extraction_method else None,
                "ocr_confidence": float(metadata.ocr_confidence) if metadata.ocr_confidence is not None else None,
                "language_detected": str(metadata.language_detected) if metadata.language_detected else None,
                "storage_path": str(metadata.storage_path),
                "processed_path": str(metadata.processed_path) if metadata.processed_path else None,
            }
            # Validate JSON serializability early to avoid runtime insert errors
            json.loads(json.dumps(row, default=str))
            return row
        except Exception as e:
            logger.error(f"Failed to serialize metadata for BigQuery: {e}")
            raise

    async def store_metadata(self, metadata: DocumentMetadata):
        """Store document metadata in BigQuery."""
        try:
            table_id = f"{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE_DOCUMENTS}"
            table = self.bigquery_client.get_table(table_id)
            
            # Convert metadata to a strict JSON row
            row = self._serialize_metadata_to_bq_row(metadata)
            
            # Insert row with retry logic for streaming buffer issues
            for attempt in range(3):
                try:
                    errors = self.bigquery_client.insert_rows_json(table, [row])
                    if errors:
                        logger.error(f"Error inserting metadata (attempt {attempt + 1}): {errors}")
                        if attempt == 2:  # Last attempt
                            raise Exception(f"BigQuery insert failed after retries: {errors}")
                        await asyncio.sleep(1)  # Wait before retry
                    else:
                        logger.info(f"Stored metadata for document {metadata.document_id}")
                        return
                except Exception as e:
                    if "streaming buffer" in str(e).lower() and attempt < 2:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    raise
            
        except Exception as e:
            logger.error(f"Error storing metadata for document {metadata.document_id}: {e}")
            raise
    
    async def get_document_metadata(self, document_id: str) -> Optional[DocumentMetadata]:
        """Retrieve document metadata from BigQuery."""
        try:
            query = f"""
            SELECT *
            FROM `{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE_DOCUMENTS}`
            WHERE document_id = @document_id
            LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("document_id", "STRING", document_id)
                ]
            )
            
            query_job = self.bigquery_client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                return DocumentMetadata(
                    document_id=row.document_id,
                    filename=row.filename,
                    file_type=row.file_type,
                    file_size=row.file_size,
                    upload_timestamp=row.upload_timestamp,
                    processing_timestamp=row.processing_timestamp,
                    status=row.status,
                    user_id=row.user_id,
                    extraction_method=row.extraction_method,
                    ocr_confidence=row.ocr_confidence,
                    language_detected=row.language_detected,
                    storage_path=row.storage_path,
                    processed_path=row.processed_path,
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving metadata for document {document_id}: {e}")
            return None
    
    async def update_metadata(self, metadata: DocumentMetadata):
        """Update document metadata in BigQuery."""
        try:
            query = f"""
            UPDATE `{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE_DOCUMENTS}`
            SET 
                processing_timestamp = @processing_timestamp,
                status = @status,
                extraction_method = @extraction_method,
                ocr_confidence = @ocr_confidence,
                language_detected = @language_detected,
                processed_path = @processed_path
            WHERE document_id = @document_id
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("document_id", "STRING", metadata.document_id),
                    bigquery.ScalarQueryParameter("processing_timestamp", "TIMESTAMP", metadata.processing_timestamp),
                    bigquery.ScalarQueryParameter("status", "STRING", metadata.status.value),
                    bigquery.ScalarQueryParameter("extraction_method", "STRING", metadata.extraction_method),
                    bigquery.ScalarQueryParameter("ocr_confidence", "FLOAT", metadata.ocr_confidence),
                    bigquery.ScalarQueryParameter("language_detected", "STRING", metadata.language_detected),
                    bigquery.ScalarQueryParameter("processed_path", "STRING", metadata.processed_path),
                ]
            )

            # Retry to avoid streaming buffer error
            for attempt in range(5):
                try:
                    query_job = self.bigquery_client.query(query, job_config=job_config)
                    query_job.result()
                    logger.info(f"Updated metadata for document {metadata.document_id}")
                    return
                except GoogleCloudError as gce:
                    message = str(gce)
                    if "streaming buffer" in message.lower():
                        await asyncio.sleep(min(2 ** attempt, 10))
                        continue
                    raise
            raise Exception("BigQuery update failed due to streaming buffer contention after retries")

        except Exception as e:
            logger.error(f"Error updating metadata for document {metadata.document_id}: {e}")
            raise
    
    async def store_simplified_document(self, simplified_doc: SimplifiedDocument):
        """Store simplified document in Cloud Storage."""
        try:
            # Create processed document path
            processed_path = f"{settings.PROCESSED_FOLDER}/{simplified_doc.document_id}/simplified.json"
            blob = self.bucket.blob(processed_path)
            
            # Convert to JSON
            doc_data = simplified_doc.dict()
            json_content = json.dumps(doc_data, indent=2, default=str)
            
            # Upload to Cloud Storage
            blob.upload_from_string(
                json_content,
                content_type="application/json"
            )
            
            # Store processing results in BigQuery for analytics
            await self._store_processing_results(simplified_doc)
            
            logger.info(f"Stored simplified document {simplified_doc.document_id} at {processed_path}")
            return processed_path
            
        except Exception as e:
            logger.error(f"Error storing simplified document {simplified_doc.document_id}: {e}")
            raise
    
    async def _store_processing_results(self, simplified_doc: SimplifiedDocument):
        """Store processing results in BigQuery for analytics."""
        try:
            table_id = f"{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.processing_results"
            table = self.bigquery_client.get_table(table_id)
            
            # Create structured row for analytics
            row = {
                "document_id": str(simplified_doc.document_id),
                "processing_timestamp": simplified_doc.processing_timestamp.isoformat(),
                "simplification_level": str(simplified_doc.simplification_level),
                "confidence_score": float(simplified_doc.confidence_score),
                "word_count_original": int(simplified_doc.word_count_original),
                "word_count_simplified": int(simplified_doc.word_count_simplified),
                "reading_level": str(simplified_doc.reading_level),
                "processing_time_seconds": None,  # Will be updated by analytics service
                "extraction_method": None,  # Will be updated from metadata
                "language_detected": None,  # Will be updated from metadata
                "has_warnings": bool(len(simplified_doc.warnings) > 0),
                "has_deadlines": bool(len(simplified_doc.deadlines_obligations) > 0),
                "key_points_count": int(len(simplified_doc.key_points)),
                "important_terms_count": int(len(simplified_doc.important_terms)),
            }
            
            # Insert row with retry logic
            for attempt in range(3):
                try:
                    errors = self.bigquery_client.insert_rows_json(table, [row])
                    if errors:
                        logger.error(f"Error inserting processing results (attempt {attempt + 1}): {errors}")
                        if attempt == 2:
                            raise Exception(f"BigQuery insert failed after retries: {errors}")
                        await asyncio.sleep(1)
                    else:
                        logger.info(f"Stored processing results for document {simplified_doc.document_id}")
                        return
                except Exception as e:
                    if "streaming buffer" in str(e).lower() and attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise
                    
        except Exception as e:
            logger.error(f"Error storing processing results for document {simplified_doc.document_id}: {e}")
            # Don't raise here as this is for analytics, not critical functionality
    
    async def get_simplified_document(self, document_id: str) -> Optional[SimplifiedDocument]:
        """Retrieve simplified document from Cloud Storage."""
        try:
            # Try to find the simplified document
            processed_path = f"{settings.PROCESSED_FOLDER}/{document_id}/simplified.json"
            blob = self.bucket.blob(processed_path)
            
            if not blob.exists():
                logger.warning(f"Simplified document not found for {document_id}")
                return None
            
            # Download and parse JSON
            json_content = blob.download_as_text()
            doc_data = json.loads(json_content)
            
            # Convert back to SimplifiedDocument
            return SimplifiedDocument(**doc_data)
            
        except Exception as e:
            logger.error(f"Error retrieving simplified document {document_id}: {e}")
            return None
    
    async def delete_document(self, document_id: str):
        """Delete a document and all its associated data."""
        try:
            # Get metadata first
            metadata = await self.get_document_metadata(document_id)
            if not metadata:
                logger.warning(f"Document {document_id} not found for deletion")
                return
            
            # Delete from Cloud Storage
            # Delete original document
            if metadata.storage_path:
                blob = self.bucket.blob(metadata.storage_path)
                if blob.exists():
                    blob.delete()
            
            # Delete processed document
            processed_path = f"{settings.PROCESSED_FOLDER}/{document_id}/simplified.json"
            blob = self.bucket.blob(processed_path)
            if blob.exists():
                blob.delete()
            
            # Delete from BigQuery metadata table
            query = f"""
            DELETE FROM `{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE_DOCUMENTS}`
            WHERE document_id = @document_id
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("document_id", "STRING", document_id)
                ]
            )
            
            query_job = self.bigquery_client.query(query, job_config=job_config)
            query_job.result()
            
            logger.info(f"Deleted document {document_id} and all associated data")
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise
    
    async def list_user_documents(self, user_id: str, limit: int = 50) -> List[DocumentMetadata]:
        """List documents for a specific user."""
        try:
            query = f"""
            SELECT *
            FROM `{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE_DOCUMENTS}`
            WHERE user_id = @user_id
            ORDER BY upload_timestamp DESC
            LIMIT @limit
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("limit", "INTEGER", limit)
                ]
            )
            
            query_job = self.bigquery_client.query(query, job_config=job_config)
            results = query_job.result()
            
            documents = []
            for row in results:
                documents.append(DocumentMetadata(
                    document_id=row.document_id,
                    filename=row.filename,
                    file_type=row.file_type,
                    file_size=row.file_size,
                    upload_timestamp=row.upload_timestamp,
                    processing_timestamp=row.processing_timestamp,
                    status=row.status,
                    user_id=row.user_id,
                    extraction_method=row.extraction_method,
                    ocr_confidence=row.ocr_confidence,
                    language_detected=row.language_detected,
                    storage_path=row.storage_path,
                    processed_path=row.processed_path,
                ))
            
            return documents
            
        except Exception as e:
            logger.error(f"Error listing documents for user {user_id}: {e}")
            return []
    
    async def get_storage_usage_stats(self) -> Dict[str, Any]:
        """Get storage usage statistics."""
        try:
            # Get document count
            query = f"""
            SELECT 
                COUNT(*) as total_documents,
                SUM(file_size) as total_size,
                AVG(file_size) as avg_file_size,
                COUNT(DISTINCT user_id) as unique_users
            FROM `{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE_DOCUMENTS}`
            """
            
            query_job = self.bigquery_client.query(query)
            results = query_job.result()
            
            for row in results:
                return {
                    "total_documents": row.total_documents,
                    "total_size_bytes": row.total_size,
                    "average_file_size_bytes": row.avg_file_size,
                    "unique_users": row.unique_users
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting storage usage stats: {e}")
            return {}
