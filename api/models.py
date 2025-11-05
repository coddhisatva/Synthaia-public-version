"""
Pydantic Models

This module defines request and response schemas for API endpoints.

Request Models:
- GenerateSongRequest: Input for song generation (theme, optional parameters)

Response Models:
- GenerateSongResponse: Output with lyrics, MIDI URLs, status
- HealthResponse: Server health status
- ErrorResponse: Error details

Progress Models:
- ProgressUpdate: WebSocket progress message (step X/7, message)

All models use Pydantic for automatic validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Server status")
    version: str = Field(..., description="API version")
    provider: str = Field(..., description="Active LLM provider (google/openai/ollama)")
    model: str = Field(..., description="Active LLM model name")


class GenerateSongRequest(BaseModel):
    """Request to generate a complete song"""
    theme: str = Field(..., min_length=3, max_length=200, description="Song theme or concept")
    temperature: Optional[float] = Field(0.8, ge=0.0, le=1.0, description="Creativity level")
    genre: Optional[str] = Field(None, description="Musical genre (e.g., 'indie rock')")
    mood: Optional[str] = Field(None, description="Emotional mood (e.g., 'melancholic')")


class GenerateSongResponse(BaseModel):
    """Response after generating a complete song"""
    status: str = Field(..., description="'success' or 'error'")
    theme: str = Field(..., description="The theme used for generation")
    lyrics: str = Field(..., description="Full song lyrics")
    midi_url: str = Field(..., description="URL to download complete MIDI file")
    timestamp: int = Field(..., description="Unix timestamp used in filenames")
    message: Optional[str] = Field(None, description="Additional message or error details")


class ProgressUpdate(BaseModel):
    """WebSocket progress update message"""
    step: int = Field(..., ge=1, le=9, description="Current step number")
    total: int = Field(9, description="Total number of steps")
    message: str = Field(..., description="Progress message")
    percentage: int = Field(..., ge=0, le=100, description="Completion percentage")


class ErrorResponse(BaseModel):
    """Error response"""
    status: str = Field("error", description="Always 'error'")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error information")

