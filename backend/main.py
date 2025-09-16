"""
AI Legal Document Simplifier - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv
from pathlib import Path
from app.api.routes import document_router, health_router
from app.api.auth_routes import auth_router
from app.services.document_processor import DocumentProcessor
from app.services.ai_simplifier import AISimplifier
from app.services.storage_service import StorageService
from app.services.analytics_service import AnalyticsService

# Load environment variables with tolerant encoding
def _safe_load_env_files() -> None:
    candidate_paths = [
        Path(__file__).parent / ".env",
        Path(__file__).parent.parent / ".env",
        Path.cwd() / ".env",
    ]
    for env_path in candidate_paths:
        if env_path.is_file():
            try:
                load_dotenv(dotenv_path=str(env_path), encoding="utf-8-sig", override=False)
            except UnicodeDecodeError:
                try:
                    load_dotenv(dotenv_path=str(env_path), encoding="utf-16", override=False)
                except Exception:
                    pass

_safe_load_env_files()

# Import settings AFTER loading env so values are available
from app.core.config import settings

# Normalize GOOGLE_APPLICATION_CREDENTIALS to an absolute existing path
def _ensure_gcp_credentials_path() -> None:
    cred_env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_env:
        return

    cred_path = Path(cred_env)
    if cred_path.is_file():
        return

    # Try resolving relative to backend/, project root, and cwd
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent
    candidates = [
        backend_dir / cred_env,
        project_root / cred_env,
        project_root / Path(cred_env).name,
    ]
    for candidate in candidates:
        if candidate.is_file():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(candidate.resolve())
            break

_ensure_gcp_credentials_path()

# Global services
document_processor = None
ai_simplifier = None
storage_service = None
analytics_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    global document_processor, ai_simplifier, storage_service, analytics_service
    
    # Startup
    print("🚀 Starting AI Legal Document Simplifier...")
    
    try:
        # Initialize services
        storage_service = StorageService()
        analytics_service = AnalyticsService()
        document_processor = DocumentProcessor()
        ai_simplifier = AISimplifier()
        
        # Test Google Cloud connections
        await storage_service.initialize()
        await analytics_service.initialize()
        
        print("✅ All services initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing services: {e}")
        raise
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AI Legal Document Simplifier...")


# Create FastAPI application
app = FastAPI(
    title="AI Legal Document Simplifier",
    description="An AI-powered platform that demystifies complex legal documents into simple, easy-to-understand language",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(document_router, prefix="/api/v1", tags=["documents"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Legal Document Simplifier API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "detail": str(exc) if settings.DEBUG else None
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
