"""
Configuration settings for the AI Legal Document Simplifier
"""

import os
from typing import List, Optional
try:
    from pydantic_settings import BaseSettings
    from pydantic import validator
except ImportError:
    from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    APP_NAME: str = "AI Legal Document Simplifier"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://your-frontend-domain.com"
    ]
    
    # Google Cloud settings (optional for local development)
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # Vertex AI settings
    VERTEX_AI_LOCATION: str = "us-central1"
    VERTEX_AI_MODEL_NAME: str = "gemini-pro"
    
    # Gemini API settings (required for AI processing)
    GEMINI_API_KEY: Optional[str] = None
    
    # Cloud Storage settings (optional for local development)
    CLOUD_STORAGE_BUCKET: Optional[str] = None
    UPLOAD_FOLDER: str = "uploads"
    PROCESSED_FOLDER: str = "processed"
    
    # BigQuery settings
    BIGQUERY_DATASET: str = "legal_documents"
    BIGQUERY_TABLE_USAGE: str = "usage_analytics"
    BIGQUERY_TABLE_DOCUMENTS: str = "document_metadata"
    
    # File processing settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/jpeg",
        "image/png",
        "image/tiff",
        "text/plain"
    ]
    
    # AI processing settings
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.3
    SIMPLIFICATION_PROMPT: str = """
    You are a legal expert and communication specialist. Your task is to simplify complex legal documents into clear, easy-to-understand language for the general public.
    
    Please analyze the following legal document and provide:
    1. A simple, plain-language summary of the main points
    2. Key terms explained in everyday language
    3. Important deadlines, obligations, or rights
    4. Any warnings or critical information
    5. Suggested next steps for the reader
    
    Maintain legal accuracy while making the content accessible to non-lawyers. Use bullet points, headings, and clear formatting.
    
    Document to simplify:
    """
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        # Avoid direct file decoding issues; rely on load_dotenv in app entrypoint
        env_file = None
        case_sensitive = True


# Create settings instance
settings = Settings()
