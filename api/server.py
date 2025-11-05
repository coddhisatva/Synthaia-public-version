"""
FastAPI Server

This module initializes the FastAPI application and configures:
- CORS middleware (to allow frontend on port 3000)
- Static file serving (for generated MIDI/lyrics files)
- Route registration
- WebSocket support for real-time progress updates

Usage:
    uvicorn api.server:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from api.models import HealthResponse
from api import routes

# Initialize FastAPI app
app = FastAPI(
    title="Synthaia API",
    description="AI-powered music creation toolkit API",
    version="0.1.0",
)

# Configure CORS - allow frontend to call backend
# Get allowed origins from environment variable or use defaults
allowed_origins = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",  # Alternative localhost
    "http://localhost:5173",  # Vite default port
]

# Add production frontend URL if set
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Mount static files - serve generated output files
# Frontend can fetch files like: http://localhost:8000/files/midi/song_123.mid
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)  # Ensure output directory exists

app.mount("/files", StaticFiles(directory=str(OUTPUT_DIR)), name="files")

# Include API routes
app.include_router(routes.router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - welcome message
    """
    return {
        "message": "Welcome to Synthaia API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns server status and configuration
    """
    from scripts.utils import cfg
    import importlib
    
    # Reload cfg to get fresh .env values (in case os.environ was modified)
    importlib.reload(cfg)
    
    provider = cfg.get_active_provider()
    model = cfg.get_active_model()
    
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        provider=provider,
        model=model,
    )

