"""
Analytics service for tracking usage and performance metrics
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio

from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError
import json

from app.core.config import settings

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for tracking and analyzing usage metrics."""
    
    def __init__(self):
        self.bigquery_client = None
        
    async def initialize(self):
        """Initialize the analytics service."""
        try:
            self.bigquery_client = bigquery.Client(project=settings.GOOGLE_CLOUD_PROJECT_ID)
            logger.info("Analytics service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize analytics service: {e}")
            raise
    
    async def track_document_upload(
        self, 
        document_id: str, 
        user_id: Optional[str] = None,
        file_size: int = 0,
        file_type: str = "unknown"
    ):
        """Track document upload event."""
        try:
            await self._insert_analytics_record({
                "document_id": document_id,
                "user_id": user_id,
                "action": "document_upload",
                "timestamp": datetime.utcnow(),
                "metadata": {
                    "file_size": file_size,
                    "file_type": file_type
                },
                "file_size": file_size
            })
            logger.info(f"Tracked document upload: {document_id}")
        except Exception as e:
            logger.error(f"Error tracking document upload: {e}")
    
    async def track_document_processing(
        self,
        document_id: str,
        processing_time: float = 0,
        simplification_level: str = "standard",
        confidence_score: float = 0.0,
        user_id: Optional[str] = None
    ):
        """Track document processing event."""
        try:
            await self._insert_analytics_record({
                "document_id": document_id,
                "user_id": user_id,
                "action": "document_processing",
                "timestamp": datetime.utcnow(),
                "metadata": {
                    "simplification_level": simplification_level,
                    "confidence_score": confidence_score
                },
                "processing_time": processing_time,
                "simplification_level": simplification_level,
                "confidence_score": confidence_score
            })
            logger.info(f"Tracked document processing: {document_id}")
        except Exception as e:
            logger.error(f"Error tracking document processing: {e}")
    
    async def track_document_view(
        self,
        document_id: str,
        user_id: Optional[str] = None,
        view_duration: Optional[float] = None
    ):
        """Track document view event."""
        try:
            await self._insert_analytics_record({
                "document_id": document_id,
                "user_id": user_id,
                "action": "document_view",
                "timestamp": datetime.utcnow(),
                "metadata": {
                    "view_duration": view_duration
                }
            })
            logger.info(f"Tracked document view: {document_id}")
        except Exception as e:
            logger.error(f"Error tracking document view: {e}")
    
    async def track_document_deletion(
        self,
        document_id: str,
        user_id: Optional[str] = None
    ):
        """Track document deletion event."""
        try:
            await self._insert_analytics_record({
                "document_id": document_id,
                "user_id": user_id,
                "action": "document_deletion",
                "timestamp": datetime.utcnow(),
                "metadata": {}
            })
            logger.info(f"Tracked document deletion: {document_id}")
        except Exception as e:
            logger.error(f"Error tracking document deletion: {e}")
    
    async def track_user_feedback(
        self,
        document_id: str,
        feedback: str,
        rating: Optional[int] = None,
        user_id: Optional[str] = None
    ):
        """Track user feedback on simplified documents."""
        try:
            await self._insert_analytics_record({
                "document_id": document_id,
                "user_id": user_id,
                "action": "user_feedback",
                "timestamp": datetime.utcnow(),
                "metadata": {
                    "rating": rating
                },
                "user_feedback": feedback
            })
            logger.info(f"Tracked user feedback: {document_id}")
        except Exception as e:
            logger.error(f"Error tracking user feedback: {e}")
    
    async def _insert_analytics_record(self, record: Dict[str, Any]):
        """Insert an analytics record into BigQuery."""
        try:
            table_id = f"{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE_USAGE}"
            table = self.bigquery_client.get_table(table_id)
            
            # Serialize to strict JSON-safe row
            row = self._serialize_analytics_row(record, table)

            # Insert with retry for streaming buffer/transient issues
            for attempt in range(3):
                try:
                    errors = self.bigquery_client.insert_rows_json(table, [row])
                    if errors:
                        logger.error(f"Error inserting analytics record (attempt {attempt + 1}): {errors}")
                        if attempt == 2:
                            raise Exception(f"BigQuery insert failed after retries: {errors}")
                        await asyncio.sleep(1)
                    else:
                        return
                except Exception as e:
                    if "streaming buffer" in str(e).lower() and attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise
                
        except Exception as e:
            logger.error(f"Error inserting analytics record: {e}")
            raise

    def _serialize_analytics_row(self, record: Dict[str, Any], table: bigquery.Table) -> Dict[str, Any]:
        """Convert analytics record to a JSON-serializable dict compatible with table schema.

        Notes:
        - If the BigQuery schema defines `metadata` as JSON, pass a Python dict (insert_rows_json will encode it).
        - If it's a RECORD, also pass a dict (must match subfields if they exist).
        - Only stringify when the field is a plain STRING to avoid "not a record" errors.
        """
        # Handle metadata field depending on schema type
        metadata_value = record.get("metadata", {})
        try:
            metadata_field = next((f for f in table.schema if f.name == "metadata"), None)
            if metadata_field is not None:
                field_type = getattr(metadata_field, "field_type", None)
                if field_type in ("JSON", "RECORD"):
                    # Keep as dict; BigQuery will accept dicts for JSON/RECORD
                    if metadata_value is None:
                        metadata_value = None
                    elif not isinstance(metadata_value, dict):
                        # Best-effort: attempt to coerce string JSON to dict
                        try:
                            metadata_value = json.loads(str(metadata_value))
                        except Exception:
                            metadata_value = {"value": str(metadata_value)}
                else:
                    # For STRING or other scalar types, store as JSON string
                    metadata_value = json.dumps(metadata_value) if metadata_value is not None else None
            else:
                # Field missing? Fallback to safe string to avoid schema mismatch
                metadata_value = json.dumps(metadata_value) if metadata_value is not None else None
        except Exception:
            metadata_value = json.dumps(metadata_value) if metadata_value is not None else None

        row: Dict[str, Any] = {
            "document_id": str(record.get("document_id")) if record.get("document_id") is not None else None,
            "user_id": str(record.get("user_id")) if record.get("user_id") is not None else None,
            "action": str(record.get("action")) if record.get("action") is not None else None,
            "timestamp": record.get("timestamp").isoformat() if isinstance(record.get("timestamp"), datetime) else str(record.get("timestamp")),
            "metadata": metadata_value,
            "processing_time": float(record.get("processing_time")) if record.get("processing_time") is not None else None,
            "file_size": int(record.get("file_size")) if record.get("file_size") is not None else None,
            "simplification_level": str(record.get("simplification_level")) if record.get("simplification_level") is not None else None,
            "confidence_score": float(record.get("confidence_score")) if record.get("confidence_score") is not None else None,
            "user_feedback": str(record.get("user_feedback")) if record.get("user_feedback") is not None else None,
        }

        # Validate serializability
        json.loads(json.dumps(row, default=str))
        return row
    
    async def get_usage_statistics(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get usage statistics for a date range."""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            query = f"""
            SELECT 
                COUNT(*) as total_actions,
                COUNT(DISTINCT document_id) as unique_documents,
                COUNT(DISTINCT user_id) as unique_users,
                COUNTIF(action = 'document_upload') as uploads,
                COUNTIF(action = 'document_processing') as processing_events,
                COUNTIF(action = 'document_view') as views,
                COUNTIF(action = 'document_deletion') as deletions,
                AVG(processing_time) as avg_processing_time,
                AVG(confidence_score) as avg_confidence_score,
                COUNTIF(user_feedback IS NOT NULL) as feedback_count
            FROM `{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE_USAGE}`
            WHERE timestamp BETWEEN @start_date AND @end_date
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date),
                    bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_date)
                ]
            )
            
            query_job = self.bigquery_client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                return {
                    "period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    },
                    "total_actions": row.total_actions,
                    "unique_documents": row.unique_documents,
                    "unique_users": row.unique_users,
                    "uploads": row.uploads,
                    "processing_events": row.processing_events,
                    "views": row.views,
                    "deletions": row.deletions,
                    "average_processing_time": row.avg_processing_time,
                    "average_confidence_score": row.avg_confidence_score,
                    "feedback_count": row.feedback_count
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting usage statistics: {e}")
            return {}
    
    async def get_document_analytics(self, document_id: str) -> Dict[str, Any]:
        """Get analytics for a specific document."""
        try:
            query = f"""
            SELECT 
                document_id,
                COUNT(*) as total_events,
                COUNT(DISTINCT action) as unique_actions,
                MIN(timestamp) as first_event,
                MAX(timestamp) as last_event,
                COUNTIF(action = 'document_upload') as uploads,
                COUNTIF(action = 'document_processing') as processing_events,
                COUNTIF(action = 'document_view') as views,
                AVG(processing_time) as avg_processing_time,
                AVG(confidence_score) as avg_confidence_score,
                COUNTIF(user_feedback IS NOT NULL) as feedback_count
            FROM `{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE_USAGE}`
            WHERE document_id = @document_id
            GROUP BY document_id
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("document_id", "STRING", document_id)
                ]
            )
            
            query_job = self.bigquery_client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                return {
                    "document_id": row.document_id,
                    "total_events": row.total_events,
                    "unique_actions": row.unique_actions,
                    "first_event": row.first_event.isoformat(),
                    "last_event": row.last_event.isoformat(),
                    "uploads": row.uploads,
                    "processing_events": row.processing_events,
                    "views": row.views,
                    "average_processing_time": row.avg_processing_time,
                    "average_confidence_score": row.avg_confidence_score,
                    "feedback_count": row.feedback_count
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting document analytics: {e}")
            return {}
    
    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for a specific user."""
        try:
            query = f"""
            SELECT 
                user_id,
                COUNT(*) as total_actions,
                COUNT(DISTINCT document_id) as unique_documents,
                MIN(timestamp) as first_activity,
                MAX(timestamp) as last_activity,
                COUNTIF(action = 'document_upload') as uploads,
                COUNTIF(action = 'document_processing') as processing_events,
                COUNTIF(action = 'document_view') as views,
                COUNTIF(action = 'document_deletion') as deletions,
                AVG(processing_time) as avg_processing_time,
                COUNTIF(user_feedback IS NOT NULL) as feedback_count
            FROM `{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE_USAGE}`
            WHERE user_id = @user_id
            GROUP BY user_id
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
                ]
            )
            
            query_job = self.bigquery_client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                return {
                    "user_id": row.user_id,
                    "total_actions": row.total_actions,
                    "unique_documents": row.unique_documents,
                    "first_activity": row.first_activity.isoformat(),
                    "last_activity": row.last_activity.isoformat(),
                    "uploads": row.uploads,
                    "processing_events": row.processing_events,
                    "views": row.views,
                    "deletions": row.deletions,
                    "average_processing_time": row.avg_processing_time,
                    "feedback_count": row.feedback_count
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {e}")
            return {}
    
    async def get_performance_metrics(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get performance metrics for the system."""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            if not end_date:
                end_date = datetime.utcnow()
            
            query = f"""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as daily_actions,
                COUNT(DISTINCT document_id) as daily_documents,
                COUNT(DISTINCT user_id) as daily_users,
                AVG(processing_time) as avg_processing_time,
                AVG(confidence_score) as avg_confidence_score,
                COUNTIF(processing_time > 30) as slow_processing_count,
                COUNTIF(confidence_score < 0.7) as low_confidence_count
            FROM `{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE_USAGE}`
            WHERE timestamp BETWEEN @start_date AND @end_date
            GROUP BY DATE(timestamp)
            ORDER BY date
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date),
                    bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_date)
                ]
            )
            
            query_job = self.bigquery_client.query(query, job_config=job_config)
            results = query_job.result()
            
            daily_metrics = []
            for row in results:
                daily_metrics.append({
                    "date": row.date.isoformat(),
                    "daily_actions": row.daily_actions,
                    "daily_documents": row.daily_documents,
                    "daily_users": row.daily_users,
                    "average_processing_time": row.avg_processing_time,
                    "average_confidence_score": row.avg_confidence_score,
                    "slow_processing_count": row.slow_processing_count,
                    "low_confidence_count": row.low_confidence_count
                })
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "daily_metrics": daily_metrics
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    async def get_popular_document_types(self) -> List[Dict[str, Any]]:
        """Get statistics on popular document types."""
        try:
            query = f"""
            SELECT 
                JSON_EXTRACT_SCALAR(metadata, '$.file_type') as file_type,
                COUNT(*) as count,
                AVG(JSON_EXTRACT_SCALAR(metadata, '$.file_size')) as avg_file_size
            FROM `{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE_USAGE}`
            WHERE action = 'document_upload'
            AND JSON_EXTRACT_SCALAR(metadata, '$.file_type') IS NOT NULL
            GROUP BY file_type
            ORDER BY count DESC
            """
            
            query_job = self.bigquery_client.query(query)
            results = query_job.result()
            
            document_types = []
            for row in results:
                document_types.append({
                    "file_type": row.file_type,
                    "count": row.count,
                    "average_file_size": row.avg_file_size
                })
            
            return document_types
            
        except Exception as e:
            logger.error(f"Error getting popular document types: {e}")
            return []
    
    async def get_simplification_effectiveness(self) -> Dict[str, Any]:
        """Get metrics on simplification effectiveness."""
        try:
            query = f"""
            SELECT 
                simplification_level,
                COUNT(*) as count,
                AVG(confidence_score) as avg_confidence,
                AVG(processing_time) as avg_processing_time,
                COUNTIF(user_feedback IS NOT NULL) as feedback_count
            FROM `{settings.GOOGLE_CLOUD_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE_USAGE}`
            WHERE action = 'document_processing'
            AND simplification_level IS NOT NULL
            GROUP BY simplification_level
            ORDER BY count DESC
            """
            
            query_job = self.bigquery_client.query(query)
            results = query_job.result()
            
            effectiveness_metrics = []
            for row in results:
                effectiveness_metrics.append({
                    "simplification_level": row.simplification_level,
                    "count": row.count,
                    "average_confidence": row.avg_confidence,
                    "average_processing_time": row.avg_processing_time,
                    "feedback_count": row.feedback_count
                })
            
            return {
                "simplification_levels": effectiveness_metrics
            }
            
        except Exception as e:
            logger.error(f"Error getting simplification effectiveness: {e}")
            return {}
    
    async def track_user_registration(self, user_id: str, email: str):
        """Track user registration event."""
        try:
            await self._insert_analytics_record({
                "document_id": "system",
                "user_id": user_id,
                "action": "user_registration",
                "timestamp": datetime.utcnow(),
                "metadata": {
                    "email": email
                }
            })
            logger.info(f"Tracked user registration: {user_id}")
        except Exception as e:
            logger.error(f"Error tracking user registration: {e}")
    
    async def track_user_login(self, user_id: str, email: str):
        """Track user login event."""
        try:
            await self._insert_analytics_record({
                "document_id": "system",
                "user_id": user_id,
                "action": "user_login",
                "timestamp": datetime.utcnow(),
                "metadata": {
                    "email": email
                }
            })
            logger.info(f"Tracked user login: {user_id}")
        except Exception as e:
            logger.error(f"Error tracking user login: {e}")
    
    async def track_user_logout(self, user_id: str):
        """Track user logout event."""
        try:
            await self._insert_analytics_record({
                "document_id": "system",
                "user_id": user_id,
                "action": "user_logout",
                "timestamp": datetime.utcnow(),
                "metadata": {}
            })
            logger.info(f"Tracked user logout: {user_id}")
        except Exception as e:
            logger.error(f"Error tracking user logout: {e}")