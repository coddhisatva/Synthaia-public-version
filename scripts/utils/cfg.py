"""
Configuration management for Synthaia.
Loads settings from .env file and provides them to all scripts.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

# AI Provider Settings
USE_CLOUD = os.getenv("USE_CLOUD", "False").lower() == "true"
PROVIDER = os.getenv("PROVIDER", "ollama")

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CLOUD_TTS_API_KEY = os.getenv("GOOGLE_CLOUD_TTS_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Model Configuration
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "llama3.1:8b")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
CLOUD_MODEL = os.getenv("CLOUD_MODEL", "gpt-4")

# Cost Controls
MAX_TOKENS_PER_DAY = int(os.getenv("MAX_TOKENS_PER_DAY", "10000"))
MAX_TOKENS_PER_REQUEST = int(os.getenv("MAX_TOKENS_PER_REQUEST", "2000"))

# Audio Configuration
DEFAULT_SOUNDFONT_PATH = os.getenv(
    "DEFAULT_SOUNDFONT_PATH", 
    "/usr/share/sounds/sf2/FluidR3_GM.sf2"
)
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "44100"))

# Synthesizer V + REAPER Configuration (AI Singing Synthesis)
SYNTHV_VOICE = os.getenv("SYNTHV_VOICE", "SOLARIA II")  # Default voice database
REAPER_EXECUTABLE = os.getenv("REAPER_EXECUTABLE", "/Applications/REAPER.app/Contents/MacOS/REAPER")
SYNTHV_VST_PATH = os.getenv("SYNTHV_VST_PATH", "/Library/Audio/Plug-Ins/VST3/Synthesizer V Studio 2 Pro.vst3")

# Derived settings
def get_active_model() -> str:
    """Returns the active model name based on USE_CLOUD setting."""
    if USE_CLOUD:
        if PROVIDER == "google":
            return GOOGLE_MODEL
        elif PROVIDER == "openai":
            return CLOUD_MODEL
        else:
            return CLOUD_MODEL
    return LOCAL_MODEL

def get_active_provider() -> str:
    """Returns the active provider based on USE_CLOUD setting."""
    if USE_CLOUD:
        if PROVIDER == "google" and GOOGLE_API_KEY:
            return "google"
        elif PROVIDER == "openai" and OPENAI_API_KEY:
            return "openai"
        elif PROVIDER == "anthropic" and ANTHROPIC_API_KEY:
            return "anthropic"
        elif GOOGLE_API_KEY:
            return "google"
        elif OPENAI_API_KEY:
            return "openai"
        elif ANTHROPIC_API_KEY:
            return "anthropic"
        else:
            raise ValueError("USE_CLOUD=True but no API key found")
    return PROVIDER

