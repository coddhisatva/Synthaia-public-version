# Audio Rendering Setup

This guide covers setting up audio rendering capabilities (MIDI → WAV conversion).

## Prerequisites

### 1. Install FluidSynth

FluidSynth is a software synthesizer that converts MIDI to audio.

**macOS:**
```bash
brew install fluidsynth
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install fluidsynth
```

**Windows:**
Download from: https://github.com/FluidSynth/fluidsynth/releases

### 2. Install Python Dependencies

```bash
pip install -e ".[audio]"
```

This installs:
- `pyfluidsynth` - Python wrapper for FluidSynth
- `soundfile` - Audio file I/O
- `librosa` - Audio processing
- `torch`/`torchaudio` - For advanced audio features (optional)

## Verify Installation

```bash
# Check FluidSynth is installed
fluidsynth --version

# Should output something like: FluidSynth runtime version 2.x.x
```

## Next Steps

After installation, you'll need a soundfont (.sf2 file) to render audio. See the main README for soundfont setup instructions.

