"""
Audio rendering configuration and settings.
"""

from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SOUNDFONTS_DIR = PROJECT_ROOT / "soundfonts"
OUTPUT_AUDIO_DIR = PROJECT_ROOT / "output" / "audio"

# Audio settings
DEFAULT_SAMPLE_RATE = 44100  # CD quality
DEFAULT_BIT_DEPTH = 16

# Quality presets
QUALITY_PRESETS = {
    "low": {
        "sample_rate": 22050,
        "gain": 0.8,
        "description": "Low quality (smaller files, faster rendering)"
    },
    "medium": {
        "sample_rate": 44100,
        "gain": 1.0,
        "description": "CD quality (default, balanced)"
    },
    "high": {
        "sample_rate": 48000,
        "gain": 1.0,
        "description": "Studio quality (larger files, better quality)"
    },
    "ultra": {
        "sample_rate": 96000,
        "gain": 1.2,
        "description": "Professional quality (very large files)"
    }
}

# General MIDI instrument mappings for our tracks
# Channel assignments match our MIDI arrangement
# NOTE: Channel 9 is drums by GM standard - don't set program change for it
INSTRUMENT_MAP = {
    0: 0,   # Channel 0 (Melody/Continuation) -> Acoustic Grand Piano
    1: 24,  # Channel 1 (Harmony) -> Acoustic Guitar (nylon)
    2: 52,  # Channel 2 (Vocals) -> Choir Aahs (placeholder for vocals)
    # Channel 9 omitted - it's automatically drums in GM
}

# GM Instrument names for reference
GM_INSTRUMENTS = {
    0: "Acoustic Grand Piano",
    24: "Acoustic Guitar (nylon)",
    25: "Acoustic Guitar (steel)",
    26: "Electric Guitar (jazz)",
    27: "Electric Guitar (clean)",
    28: "Electric Guitar (muted)",
    29: "Overdriven Guitar",
    30: "Distortion Guitar",
    52: "Choir Aahs",
    53: "Voice Oohs",
}

def get_default_soundfont() -> Path:
    """
    Find and return the first available soundfont in the soundfonts directory.
    
    Returns:
        Path to soundfont file
    
    Raises:
        FileNotFoundError: If no soundfont is found
    """
    if not SOUNDFONTS_DIR.exists():
        raise FileNotFoundError(f"Soundfonts directory not found: {SOUNDFONTS_DIR}")
    
    # Look for common soundfont files
    for pattern in ["*.sf2", "*.sf3"]:
        soundfonts = list(SOUNDFONTS_DIR.glob(pattern))
        if soundfonts:
            return soundfonts[0]
    
    raise FileNotFoundError(
        f"No soundfont (.sf2 or .sf3) found in {SOUNDFONTS_DIR}\n"
        f"Please download a soundfont. See soundfonts/README.md for instructions."
    )

