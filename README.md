# Synthaia 🎶🤖

**Synthaia** is an AI-powered music creation toolkit that generates complete songs from a simple text prompt. It combines Large Language Models (LLMs) with MIDI generation to create lyrics, melodies, harmonies, drums, and vocal lines—all from a single theme.

Live Site: (todo)
__________________________________________________________
![Synthaia Interface](screenshots/Synthaia%20Cover%201.png)
__________________________________________________________
![Synthaia Song Generation](screenshots/Synthaia%20Cover%202.png)
__________________________________________________________

# Loom Video Demo
Click here to watch a **loom video demo** of Synthaia: https://www.loom.com/share/2025e0a9c7924355bc6c226fdeaeba94

## 🌟 What It Does

Give Synthaia a theme like "summer vibes" and it will:
1. **Generate Song Lyrics** - Full verses, chorus, and bridge

Then, using the first verse, it will:

2. **Create Instrumental Melody** - Piano-based main melody (4 measures)
3. **Add Continuation** - Extended melodic development (4 measures)
4. **Generate Harmony** - Counter-melody that complements the main theme
5. **Create Drum Pattern** - 8-measure drum track with fills
6. **Generate Vocal Melody** - Singable vocal line with embedded lyrics in MIDI
7. **Arrange Everything** - Combine all parts into a multi-track MIDI file
8. **Render Complete Audio** - Mix all 4 tracks to WAV (with vocals)
9. **Render Instrumental Audio** - Mix 3 tracks to WAV (no vocals)

Then you can:
- **Play It Back** - In-browser MIDI player with individual track controls
- **Download MIDI Files** - 4-track complete MIDI + vocals-only MIDI for DAW import
- **Download Audio Files** - Complete WAV (all tracks) + Instrumental WAV (no vocals)
- **Get Singing Vocals** - Use the vocals MIDI in Synthesizer V, ACE Studio, or Vocaloid to render AI-sung vocals (more on this below)

# STATUS OF VOCALS

The current big limitation of this that we don't immediately provide AI generated vocals.

The intended final output should include:
- Melody (present)
- Harmony (countermelody) (present)
- Drums (present)
- Vocals (*partial*)

Currently, the vocal track provided is just a midi instrumental track, like the melody and harmony tracks. 

We wanted to provide actual AI-sung, high-quality vocals. To do this, we needed to embed our lyrics into midi (check), or for some solutions, turn that into musicxml format (check), and then submit that to another program, such as Synthesizer V, Ace Studio, Vocaloid, or another solution, to convert that instrumental into AI-sung vocals, which we wanted to provide in our final output.

Unfortunately, the only current solutions that we could find are GUI based. We could not find any APIs or CLIs which we could integrate to provide this functionality natively. 
- (Other options we tried included Sinsy (jp only), Reaper CLI + Synth V VST (VST bugs), TTS (not singing quality), and some others).

We've provided the vocal midi with lyrics embedded, so it is easy for a user to use their own DAW workflow to add the AI vocals.

Our loom video above showcases how to do this.

Contact me if you figure out how to implement this: conoregan151@gmail.com

## Using

This tool is meant to be used as a web application (link near top of ReadMe, and in Repo Settings / About section). However, if desired, one can download this codebase themselves.

## Developer Section

The rest of this repo you will probably only find useful if you are building upon the repo, or want to find out how it works.

### Web Application (Recommended)

1. **Start the Backend:**
```bash
# Install Python dependencies
pip install -e .

# Configure API keys
cp .env.example .env
# Edit .env and add:
#   GOOGLE_API_KEY (for Gemini LLM - from aistudio.google.com)
# Or use OPENAI_API_KEY instead of Gemini

# Start FastAPI server
uvicorn api.server:app --reload --port 8000
```

2. **Start the Frontend:**
```bash
cd frontend
npm install
npm run dev
```

3. **Open your browser** to `http://localhost:5173`
4. **Enter a theme** (e.g., "rainy day introspection")
5. **Click "Create Song"** and watch it generate in real-time!
6. **Play it back** with the built-in MIDI player

### CLI Tools (For Advanced Users)

All CLI commands still work! See the "CLI Usage" section below.

## 🛠 Tech Stack

### Backend
- **Python 3.13** - Core language
- **FastAPI** - REST API and WebSocket server
- **LangChain** - LLM integration framework
- **Google Gemini 2.5 Flash** - Primary LLM (configurable)
- **OpenAI GPT-4o Mini** - Alternative LLM option
- **mido** - MIDI file creation and manipulation with lyric embedding
- **music21** - Music theory and analysis
- **FluidSynth** - MIDI to audio synthesis (WAV export)
- **Soundfonts** - High-quality instrument samples (MuseScore General SF3)

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Tone.js** - Web Audio API framework
- **@tonejs/midi** - MIDI parsing
- **soundfont-player** - Melodic instrument sample playback
- **WebAudioFont** - High-quality drum samples

### Communication
- **WebSocket** - Real-time progress updates during generation
- **REST API** - Health checks and file serving

## 🎹 Features

### Web Application
- ✅ **One-Click Song Generation** - Single button creates everything
- ✅ **Real-Time Progress** - See each step as it happens (1/9 through 9/9 with visual progress bar)
- ✅ **Advanced MIDI Player** - Play, pause, stop with professional controls
  - 🎹 **Instrument Selection** - Choose from 8+ instruments per track including vocal-like sounds (Choir, Voice Oohs, etc.)
  - 🥁 **Dual Drum Engines** - Switch between WebAudioFont (high-quality) and Soundfont drums
  - 🎚️ **Per-Track Volume Controls** - Independent gain sliders (0-150%) for each instrument
  - 🔇 **Individual Track Mute** - Toggle any track on/off during playback
  - 🎼 **Named Tracks** - Clear labels (Melody, Harmony, Vocals, Drums)
- ✅ **Multi-Track Display** - MIDI tracks (Melody, Harmony, Vocals, Drums) with individual controls
- ✅ **Smart Song History** - Last 10 songs saved with click-to-load and clear history (no duplicates)
  - 💾 **Auto-Save on Exit** - Current song automatically saved to history when you refresh, close tab, or navigate away
- ✅ **Lyrics Viewer** - Collapsible lyrics display with clean formatting (structural markers filtered)
- ✅ **Model Selection** - Switch between Gemini 2.5 Flash and GPT-4o Mini
- ✅ **Cancel Generation** - Stop mid-process if needed
- ✅ **Download Options**:
  - 📥 **Complete MIDI** - All 4 tracks for DAW import
  - 📥 **Vocals-only MIDI** - With embedded lyrics for singing synthesis software
  - 🔊 **Complete Audio WAV** - All tracks mixed (Melody + Harmony + Vocals + Drums)
  - 🎵 **Instrumental Audio WAV** - No vocals (Melody + Harmony + Drums only)
- ✅ **Unicode Support** - Smart quotes, emoji, and special characters handled properly

### CLI Tools (Scriptable)
- ✅ **Modular Pipeline** - Run each step independently
- ✅ **Batch Processing** - Generate multiple variations
- ✅ **Custom Parameters** - Fine-tune tempo, genre, mood
- ✅ **File-Based Workflow** - Chain commands with saved outputs

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Synthaia.git
cd Synthaia

# Backend Setup
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .

# Frontend Setup
cd frontend
npm install
cd ..

# Configure API Keys
cp .env.example .env
# Edit .env and add:
#   GOOGLE_API_KEY=your_gemini_key_here (from Google AI Studio - for Gemini LLM)
#   OPENAI_API_KEY=your_openai_key_here (optional, for GPT-4o Mini)
```

## CLI Usage (Advanced)

All the underlying Python scripts are still available for command-line usage, automation, and custom workflows.

### Lyrics: Generate Song Ideas

Generate creative song ideas and concepts based on a theme.

**Basic Usage:**
```bash
python scripts/lyrics/idea_seed_llm.py "your theme here"
```

**Arguments:**
- `theme` (required) - The theme or concept for song ideas

**Options:**
- `--count`, `-c` - Number of ideas to generate (default: 1, range: 1-10)
- `--temp`, `-t` - Creativity level (default: 0.8, range: 0.0-1.0)
- `--output`, `-o` - Save to file instead of printing to console

**Examples:**
```bash
# Generate 1 idea about summer romance
python scripts/lyrics/idea_seed_llm.py "summer romance"

# Generate 5 ideas with high creativity
python scripts/lyrics/idea_seed_llm.py "urban loneliness" --count 5 --temp 0.9

# Save idea to organized output folder
python scripts/lyrics/idea_seed_llm.py "heartbreak" -o output/ideas/heartbreak.txt
```

---

### Lyrics: Generate Song Lyrics

Generate complete song lyrics (verses, chorus, bridge) from a concept or idea.

**Basic Usage:**
```bash
python scripts/lyrics/generate_song_lyrics.py "your concept here"
```

**Arguments:**
- `concept` - The song concept, idea, or theme (optional if using --input)

**Options:**
- `--input`, `-i` - Read concept from file (e.g., from idea generator output)
- `--genre`, `-g` - Musical genre (e.g., 'indie rock', 'pop', 'hip-hop')
- `--mood`, `-m` - Emotional mood (e.g., 'melancholic', 'upbeat', 'intimate')
- `--temp`, `-t` - Creativity level (default: 0.8, range: 0.0-1.0)
- `--output`, `-o` - Save to file instead of printing to console

**Examples:**
```bash
# Generate from a direct concept
python scripts/lyrics/generate_song_lyrics.py "A story about leaving home"

# Generate from saved idea file (uses first idea only)
python scripts/lyrics/generate_song_lyrics.py --input output/ideas/heartbreak.txt -o output/songs/heartbreak.txt

# Add genre and mood context
python scripts/lyrics/generate_song_lyrics.py "Lost love in a digital age" --genre "indie pop" --mood "melancholic"
```

**Workflow - Chain the tools:**
```bash
# Step 1: Generate an idea
python scripts/lyrics/idea_seed_llm.py "nostalgia" -o output/ideas/nostalgia.txt

# Step 2: Generate full lyrics from that idea
python scripts/lyrics/generate_song_lyrics.py --input output/ideas/nostalgia.txt -o output/songs/nostalgia.txt
```

---

### Lyrics: Full Song (Idea + Lyrics in One Command)

Generate a complete song from theme to final lyrics in a single command.
This combines idea generation and lyrics writing into one workflow.

**Basic Usage:**
```bash
python scripts/lyrics/idea_to_lyrics.py "your theme here"
```

**Arguments:**
- `theme` (required) - The theme or concept for the song

**Options:**
- `--genre`, `-g` - Musical genre (e.g., 'indie rock', 'pop', 'hip-hop')
- `--mood`, `-m` - Emotional mood (e.g., 'melancholic', 'upbeat', 'intimate')
- `--temp`, `-t` - Creativity level (default: 0.8, range: 0.0-1.0)
- `--output`, `-o` - Save to file instead of printing to console
- `--save-idea` - Also save the generated idea to output/ideas/

**Examples:**
```bash
# Generate complete song from theme
python scripts/lyrics/idea_to_lyrics.py "summer romance"

# With genre and save to file
python scripts/lyrics/idea_to_lyrics.py "heartbreak" --genre "indie pop" -o output/songs/heartbreak.txt

# Save both idea and final song
python scripts/lyrics/idea_to_lyrics.py "nostalgia" --save-idea -o output/songs/nostalgia.txt
```

**What it does:**
1. Generates a song idea/concept from your theme
2. Immediately writes complete lyrics based on that idea
3. Outputs both the concept and lyrics (in file or console)

---

### MIDI: Generate Melody from Text

Generate a MIDI melody based on a text description. The AI interprets the mood, energy, and imagery to create an expressive melody.

**Basic Usage:**
```bash
python scripts/midi/generate_melody.py "your description here"
```

**Arguments:**
- `description` (required) - Text describing the melody vibe or feeling

**Options:**
- `--temp`, `-t` - Creativity level (default: 0.8, range: 0.0-1.0)
- `--output`, `-o` - Output MIDI file path (auto-generated if not specified)

**Examples:**
```bash
# Generate from description (auto-saves to output/midi/)
python scripts/midi/generate_melody.py "bunnies running through the field"

# Save to specific location
python scripts/midi/generate_melody.py "dark stormy night" -o output/midi/storm.mid

# More creative interpretation
python scripts/midi/generate_melody.py "peaceful morning sunrise" --temp 0.9
```

**What it does:**
1. Interprets your text to understand mood and energy
2. Generates musical parameters (tempo, key, note sequence)
3. Creates a MIDI file you can open in any DAW or music software

---

### MIDI: Continue/Complete Melody

Generate a musical continuation for an existing MIDI file. Creates a second melody that completes the musical idea when played back-to-back.

**Basic Usage:**
```bash
python scripts/midi/continue_melody.py input.mid
```

**Arguments:**
- `input_midi` (required) - Path to input MIDI file

**Options:**
- `--temp`, `-t` - Creativity level (default: 0.8, range: 0.0-1.0)
- `--output`, `-o` - Output MIDI file path (auto-generated if not specified)

**Examples:**
```bash
# Generate continuation (saves as input_continuation.mid)
python scripts/midi/continue_melody.py output/midi/melody.mid

# Save to specific location
python scripts/midi/continue_melody.py melody.mid -o melody_part2.mid

# More creative continuation
python scripts/midi/continue_melody.py original.mid --temp 0.9
```

**What it does:**
1. Analyzes the input MIDI (tempo, key, melodic pattern)
2. Generates a continuation that matches the style
3. Creates a new MIDI file that completes the musical phrase
4. Play both files back-to-back in your DAW for a complete idea

---

### MIDI: Harmonize/Counter-Melody

Generate a harmony or counter-melody that plays simultaneously with your original melody. Takes two MIDI files (e.g., original + continuation) and creates a parallel harmony track.

**Basic Usage:**
```bash
python scripts/midi/harmonize_melody.py part1.mid part2.mid
```

**Arguments:**
- `part1` (required) - First MIDI file (original melody)
- `part2` (required) - Second MIDI file (continuation)

**Options:**
- `--temp`, `-t` - Creativity level (default: 0.8, range: 0.0-1.0)
- `--output`, `-o` - Output MIDI file path (auto-generated if not specified)

**Examples:**
```bash
# Generate harmony (saves as part1_harmony.mid)
python scripts/midi/harmonize_melody.py melody.mid continuation.mid

# Save to specific location
python scripts/midi/harmonize_melody.py part1.mid part2.mid -o guitar_harmony.mid

# More creative harmonization
python scripts/midi/harmonize_melody.py original.mid next.mid --temp 0.9
```

**What it does:**
1. Combines both input MIDI files into one sequence
2. Generates a parallel harmony that follows closely at first
3. Gradually diverges into a counter-melody towards the end
4. Creates a MIDI file the same length as both parts combined

**In your DAW:**
- Track 1 (Piano): Original melody (part1 + part2 played sequentially)
- Track 2 (Guitar/Synth): Harmony track (plays simultaneously with Track 1)

---

### MIDI: Generate Drum Pattern

Generate a drum pattern that matches your song's tempo and vibe. Perfect for adding rhythm to your melodies.

**Basic Usage:**
```bash
python scripts/midi/generate_drums.py melody.mid "energetic rock beat"
```

**Arguments:**
- `reference_midi` (required) - MIDI file to extract tempo from
- `description` (required) - Text description of drum vibe/pattern

**Options:**
- `--measures`, `-m` - Number of measures (default: 8)
- `--temp`, `-t` - Creativity level (default: 0.8, range: 0.0-1.0)
- `--output`, `-o` - Output MIDI file path (auto-generated if not specified)

**Examples:**
```bash
# Generate 8 measures of drums matching melody tempo
python scripts/midi/generate_drums.py melody.mid "energetic rock beat"

# Custom description with specific dynamics
python scripts/midi/generate_drums.py melody.mid "start epic and smashing, then go into intense fast fill, end hard on toms and floor" -o drums.mid

# 16 measures of hip hop
python scripts/midi/generate_drums.py track.mid "simple hip hop groove" --measures 16
```

**What it does:**
1. Extracts tempo from your reference MIDI file
2. Generates drum pattern with proper MIDI note numbers (kick=36, snare=38, etc.)
3. Creates dynamics and fills based on your description
4. Outputs MIDI on channel 10 (standard drum channel)

**In GarageBand:**
1. Create Software Instrument track
2. Choose a drum kit
3. Drag in the drum MIDI file
4. Drums sync perfectly with your melody!

---

### MIDI: Generate Vocal Melody

Generate a singable vocal melody that complements your instrumental tracks and lyrics. Creates MIDI with embedded lyric meta-events for use in singing synthesis software.

**Basic Usage:**
```bash
python scripts/midi/generate_vocal_melody.py melody.mid continuation.mid harmony.mid --lyrics song.txt
```

**Arguments:**
- `melody` (required) - Original melody MIDI file
- `continuation` (required) - Continuation MIDI file
- `harmony` (required) - Harmony/counter-melody MIDI file

**Options:**
- `--lyrics`, `-l` (required) - Path to lyrics text file
- `--temp`, `-t` - Creativity level (default: 0.8, range: 0.0-1.0)
- `--output`, `-o` - Output MIDI file path (auto-generated if not specified)

**Examples:**
```bash
# Generate vocal melody from all tracks
python scripts/midi/generate_vocal_melody.py melody.mid continuation.mid harmony.mid --lyrics output/songs/emo_bandit.txt

# Save to specific location
python scripts/midi/generate_vocal_melody.py part1.mid part2.mid harmony.mid -l lyrics.txt -o vocals.mid

# More creative vocal line
python scripts/midi/generate_vocal_melody.py original.mid next.mid counter.mid -l song.txt --temp 0.9
```

**What it does:**
1. Reads all 3 instrumental MIDI files to understand the arrangement
2. Extracts the first verse (4 lines) from your lyrics
3. Generates a singable vocal melody (C3-C5 range) that:
   - Complements the instrumental tracks
   - Follows the lyrical phrasing naturally (one note per word/syllable)
   - Has appropriate breathing points
   - Uses expressive melodic contours
4. Maps each word to its corresponding MIDI note
5. Embeds lyrics as MIDI meta-events (Type 0x05) synchronized with notes
6. Outputs vocal melody MIDI ready for import into singing synthesis software

**Turning MIDI into Singing Vocals:**

The generated MIDI includes embedded lyrics and can be imported into singing synthesis software:
- **Synthesizer V** (https://dreamtonics.com/synthesizerv/) - Recommended, has free trial
- **ACE Studio** (https://acestudio.ai/) - Another solid option
- **Vocaloid** - Professional option (commercial licensing required)

Simply open the vocals MIDI file in these programs, select a voice, and render to audio.

**Output files:**
- `{song}_vocals.mid` - MIDI vocal melody with embedded lyrics

---

### MIDI: Arrange Multi-Track Song

Combine all your MIDI files into a single multi-track arrangement with proper timing and channel assignments.

**Basic Usage:**
```bash
python scripts/midi/arrange_song.py --melody melody.mid --continuation cont.mid
```

**Arguments:**
- `--melody`, `-m` (required) - Melody MIDI file (plays measures 1-2)
- `--continuation`, `-c` (required) - Continuation MIDI file (plays measures 3-4)

**Options:**
- `--harmony`, `-h` - Harmony MIDI file (starts at measure 5)
- `--drums`, `-d` - Drums MIDI file (plays throughout)
- `--vocals`, `-v` - Vocals MIDI file (plays throughout)
- `--output`, `-o` - Output file path (default: output/midi/arranged_song.mid)

**Examples:**
```bash
# Basic arrangement with melody and continuation
python scripts/midi/arrange_song.py -m melody.mid -c continuation.mid

# Full arrangement with all tracks
python scripts/midi/arrange_song.py \
  -m melody.mid \
  -c continuation.mid \
  -h harmony.mid \
  -d drums.mid \
  -v vocals.mid \
  -o output/midi/complete_song.mid

# With custom output location
python scripts/midi/arrange_song.py -m m.mid -c c.mid -d d.mid -o my_song.mid
```

**What it does:**
1. Combines all tracks into one MIDI file with multiple channels
2. Creates structured arrangement:
   - Measures 1-2: Melody only
   - Measures 3-4: Continuation
   - Measures 5-8: Melody + Continuation loop with Harmony
   - Drums and Vocals: Throughout all measures
3. Assigns MIDI channels:
   - Channel 0: Melody/Piano
   - Channel 1: Harmony/Guitar
   - Channel 2: Vocals
   - Channel 9: Drums (standard)
4. Outputs single MIDI file ready for DAW import

**In your DAW:**
- Import the arranged MIDI file
- All tracks appear automatically
- Assign instruments to each channel
- Mix and master!

---

## Complete Song Generation Pipeline

### Create Full Song (Automated Workflow)

Generate a complete song from a single theme—from lyrics to fully arranged multi-track MIDI—in one command.

**Basic Usage:**
```bash
python scripts/create_full_song.py "your theme here"
```

**Arguments:**
- `theme` (required) - The theme or concept for the song

**Options:**
- `--output`, `-o` - Base name for all output files (default: auto-generated from theme)

**Examples:**
```bash
# Generate complete song with auto-generated filenames
python scripts/create_full_song.py "this woman is my therapy"

# Use custom filename base
python scripts/create_full_song.py "summer nights" -o summer_song
```

**What it does (full automation):**
1. **Generates lyrics** - Creates complete song lyrics from your theme
2. **Creates melody** - Generates initial MIDI melody
3. **Adds continuation** - Creates a second melody section
4. **Harmonizes** - Generates harmony/counter-melody (octave lower)
5. **Adds drums** - Creates 8-measure drum pattern matching tempo
6. **Generates vocals** - Creates singable vocal melody with embedded lyrics in MIDI
7. **Arranges everything** - Combines all tracks into one MIDI file

**Output files:**
```
output/songs/{theme}_lyrics.txt       # Complete song lyrics
output/midi/{theme}_melody.mid        # Original melody
output/midi/{theme}_continuation.mid  # Melody continuation
output/midi/{theme}_harmony.mid       # Harmony/counter-melody
output/midi/{theme}_drums.mid         # Drum pattern
output/midi/{theme}_vocals.mid        # Vocal melody with embedded lyrics
output/midi/{theme}_complete.mid      # ⭐ Final multi-track arrangement
output/audio/{theme}_complete.wav     # ✨ All 4 tracks mixed audio
output/audio/{theme}_instrumental.wav # ✨ Instrumental only (no vocals)
```

**In your DAW:**
Open `{theme}_complete.mid` in GarageBand, Logic, Ableton, or any DAW and you'll have:
- Track 0: Melody/Piano (measures 1-2, then loops)
- Track 1: Harmony/Guitar (enters at measure 5)
- Track 2: Vocals (throughout) - with embedded lyrics
- Track 3: Drums (throughout)

Import `{theme}_vocals.mid` into Synthesizer V or similar software to render singing vocals, then mix with the rest of the tracks!

---

## Audio Rendering (Fully Working! ✅)

### MIDI to WAV Conversion

We've implemented complete MIDI to WAV audio rendering using FluidSynth and soundfonts. Songs are now automatically exported as playable audio files!

**Current Status:**
- ✅ FluidSynth integration working
- ✅ MIDI files render to WAV format
- ✅ Instrument mapping fully implemented
- ✅ All channels render correctly (Piano, Guitar, Choir, Drums)
- ✅ **Two audio versions**: Complete (with vocals) and Instrumental (no vocals)
- ✅ **Automated in web workflow** - Download buttons appear automatically
- ✅ **High quality**: 44.1kHz CD-quality audio

**What You Get:**
- **Complete WAV** - All 4 tracks mixed together (Melody + Harmony + Vocals + Drums)
- **Instrumental WAV** - 3 tracks without vocals (Melody + Harmony + Drums)
- Both files ready to use in any audio player or DAW

**How It Works:**
1. Generate a song via web app or CLI
2. After MIDI arrangement completes, two WAV files are automatically rendered
3. Download via "Download with Vocal midi" or "Download without Vocal midi" buttons
4. Use immediately or import into DAW for further mixing

**Files created:**
```
scripts/audio/render_midi.py          # Main rendering script (+ new wrapper functions)
scripts/audio/audio_config.py         # Configuration and instrument maps
scripts/audio/instrument_mapper.py    # Program change injection
AUDIO_SETUP.md                        # Setup instructions
soundfonts/                           # Soundfont storage
WAV_EXPORT_IMPLEMENTATION.md          # Implementation details
test_wav_export.py                    # Test suite
```

**Output Files:**
```
output/audio/
  - {song}_complete.wav               # All 4 tracks (with vocals)
  - {song}_instrumental.wav           # 3 tracks (no vocals)
```

**Known Limitations:**
- Vocals are synthesized as choir/synth sounds (not sung by AI voice)
  - For true singing vocals, use external software (Synthesizer V, ACE Studio)
  - Download the vocals MIDI to render separately
- Instrument quality depends on soundfont (MuseScore General is good, not professional)
- Basic level mixing only (no reverb, EQ, compression)

**Still Want Manual Control?** Import MIDI files into your DAW (GarageBand, Logic, Ableton) for custom instrument selection, effects, and professional mixing.

**Alternative Playback:** The web application also includes browser-based MIDI playback using Tone.js, soundfont-player, and WebAudioFont for instant preview without downloading.

---

## Testing & Utilities

### Test LLM Connection

Test if your AI provider is configured correctly.

```bash
python scripts/utils/llm_client.py
```

This will:
- Display your current provider and model
- Test the connection
- Generate a sample song title to verify everything works

Use this to verify your setup is working before running other commands.

---

## Architecture & Design Pattern

### Dual-Interface Philosophy

**Every tool in Synthaia follows a dual-interface pattern:**

1. **CLI Interface** - For humans using the command line
2. **Python API** - For programmatic access and tool chaining

This design allows:
- ✅ Each tool works standalone via command line
- ✅ Tools can be chained together programmatically
- ✅ No code duplication across workflows
- ✅ One source of truth for each tool's logic

### Implementation Pattern

Each script exposes:

```python
# Core function (Python API)
def tool_name_core(args) -> result:
    """Pure business logic, returns data"""
    return result

# CLI command (Human interface)  
@app.command()
def cli_command(args):
    """Calls core + adds CLI formatting"""
    result = tool_name_core(args)
    # Handle output, pretty printing, file saving
```

### Future Tool Chaining

This pattern enables complex workflows like:

```python
theme → idea → lyrics → MIDI → vocals (MIDI) → [external: singing synthesis] → mix
```

Each tool can be used independently **or** chained together programmatically while maintaining a single source of truth for the logic.

---

## API Reference

For developers integrating with the backend:

### WebSocket Endpoint

**`ws://localhost:8000/api/ws/generate-song`**

Send a JSON message with:
```json
{
  "theme": "your song theme",
  "provider": "google" // or "openai"
}
```

Receive real-time progress updates:
```json
{
  "step": 3,
  "total": 7,
  "message": "Adding continuation...",
  "percentage": 43
}
```

Final result includes:
```json
{
  "status": "success",
  "result": {
    "theme": "your theme",
    "lyrics": "full lyrics text...",
    "midi_url": "/files/midi/song_123456.mid",
    "timestamp": 1234567890
  }
}
```

### REST Endpoints

- **`GET /health`** - Health check, returns active provider and model
- **`GET /files/midi/{filename}`** - Download generated MIDI files
- **`GET /files/songs/{filename}`** - Download generated lyrics files

## Configuration

Edit `.env` to configure:

```bash
# AI Provider
USE_CLOUD=True
PROVIDER=google

# API Keys
GOOGLE_API_KEY=your_key_here

# Model
GOOGLE_MODEL=gemini-2.5-flash

# Cost Controls
MAX_TOKENS_PER_DAY=10000
MAX_TOKENS_PER_REQUEST=2000
```

## Project Structure

```
Synthaia/
├── api/                     # FastAPI Backend
│   ├── server.py           # Main FastAPI app + CORS
│   ├── routes.py           # WebSocket and REST endpoints
│   └── models.py           # Pydantic data models
├── frontend/               # React Web Application
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── Layout/
│   │   │   ├── MidiPlayer.jsx
│   │   │   ├── ConnectionTest.jsx
│   │   │   ├── ProgressIndicator.jsx
│   │   │   └── ErrorAlert.jsx
│   │   ├── services/
│   │   │   └── websocket.js  # WebSocket client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── scripts/
│   ├── lyrics/             # Song idea and lyrics generation
│   │   ├── idea_seed_llm.py
│   │   ├── generate_song_lyrics.py
│   │   └── idea_to_lyrics.py
│   ├── midi/               # MIDI generation and manipulation
│   │   ├── generate_melody.py
│   │   ├── continue_melody.py
│   │   ├── harmonize_melody.py
│   │   ├── generate_drums.py
│   │   ├── generate_vocal_melody.py
│   │   └── arrange_song.py
│   ├── utils/              # Core utilities
│   │   ├── cfg.py          # Configuration management
│   │   ├── llm_client.py   # LLM provider abstraction
│   │   └── midi_utils.py   # Shared MIDI utilities
│   └── create_full_song.py # Complete automated pipeline (CLI)
├── prompts/                # LLM system prompts
│   ├── lyrics/
│   └── midi/
├── output/                 # Generated files (gitignored)
│   ├── ideas/
│   ├── songs/
│   ├── midi/
│   └── audio/
├── .env                    # Configuration (not in git)
└── README.md
```

## Development Status

**✅ Core Generation (Fully Working):**
- ✅ LLM client (Gemini 2.5 Flash, GPT-4o Mini support)
- ✅ Song idea generator (CLI + Python API)
- ✅ Full lyrics generator (CLI + Python API)
- ✅ MIDI melody generator from text description
- ✅ MIDI melody continuation/completion
- ✅ MIDI harmonization/counter-melody with timing sync
- ✅ MIDI drum pattern generator (8-measure, auto-extension)
- ✅ MIDI vocal melody generator
- ✅ MIDI multi-track arranger (4 tracks: Piano, Organ, Vocals, Drums)
- ✅ Complete automated CLI pipeline

**✅ Web Application (Fully Working):**
- ✅ React + Vite frontend with Tailwind CSS
- ✅ FastAPI backend with WebSocket support
- ✅ Real-time progress streaming (9-step updates with visual progress bar)
- ✅ Advanced in-browser MIDI player (Tone.js + soundfont-player + WebAudioFont)
  - ✅ Instrument selection per track (8+ instruments including Piano, Synth, Bass, Guitar)
  - ✅ Dual drum engines (WebAudioFont high-quality vs Soundfont)
  - ✅ Per-track volume controls (0-150% gain sliders)
  - ✅ Dynamic instrument switching during playback
  - ✅ Named tracks (Melody, Harmony, Vocals, Drums)
  - ✅ Multiple vocal-like instrument options (Choir, Voice Oohs, etc.)
- ✅ Multi-track playback with individual mute controls
- ✅ Smart song history (localStorage, last 10 songs with no duplicates)
- ✅ AI model selection dropdown (Gemini vs GPT-4o Mini)
- ✅ Cancel generation mid-process
- ✅ Collapsible lyrics viewer with filtered structural markers
- ✅ **WAV audio downloads** (complete + instrumental versions)
- ✅ MIDI file downloads (complete multi-track + vocals-only)
- ✅ Health check and backend status monitoring

**✅ AI Vocal Generation:**
- ✅ MIDI vocal melody generation with lyrics alignment
- ✅ Automatic word-to-note mapping
- ✅ MIDI lyric meta-events (Type 0x05) embedded in vocal track
- ✅ Structural marker filtering (verses, choruses) from lyrics
- ✅ Lyrics parser strips LLM commentary to ensure clean output
- ✅ Retry logic for flaky LLM responses
- ✅ Vocals-only MIDI export with embedded lyrics for external singing synthesis

**⚠️ Known Limitations:**
- ⚠️ Drum patterns occasionally generate half-length (prompt strengthened, but LLM compliance varies)
- ⚠️ **No automated singing synthesis** - vocals in WAV are choir/synth sounds, not sung
  - For AI singing, download vocals MIDI and render in Synthesizer V/ACE Studio
  - Then mix with instrumental WAV in your DAW

**🎯 Future Goal: Automated Singing Synthesis**

Currently, vocal tracks are generated as MIDI with embedded lyrics. To get AI-sung vocals, users must:
1. Download the vocals-only MIDI file
2. Import into singing synthesis software (Synthesizer V, ACE Studio, Vocaloid)
3. Select a voice and render to audio
4. Mix with the rest of the tracks in a DAW

**Why not automated?** None of the available singing synthesis software provide public APIs or CLIs suitable for web automation. We've explored:
- **Synthesizer V** - No API, VST state management too complex, GUI automation not viable for servers
- **Vocaloid** - API requires commercial licensing from Yamaha
- **PySinsy** - Only supports Japanese (no English dictionaries)
- **ACE Studio** - No public API
- **Google Cloud TTS** - Speech synthesis (not singing), poor quality

**We're looking for:** If you know of (or create!) an English singing synthesis API/CLI, please reach out at conoregan151@gmail.com

**🚧 Planned Features:**
- Piano roll visualization for MIDI player
- Automated singing synthesis (pending available API/CLI)
- Complete song WAV export (all 4 tracks mixed)
- MIDI transformation tools (arpeggiate, humanize, transpose)
- Bass line generator
- Audio mixing and mastering (apply reverb, EQ, compression)
- Additional lyric tools (rhyme helper, verse rewriter)
- Export to popular DAW formats (Ableton, Logic, FL Studio)
- MIDI effect chains (arpeggiators, chord generators, humanizers)