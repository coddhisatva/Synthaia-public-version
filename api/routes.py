"""
API Routes

This module defines the song generation endpoint:

WebSocket Endpoint:
- WS /api/ws/generate-song - Generate complete song with real-time progress updates

The WebSocket endpoint:
1. Receives song theme and parameters from client
2. Generates complete song (lyrics + MIDI)
3. Streams progress updates for each step (1/7, 2/7, etc.)
4. Returns final result with lyrics text and MIDI file URL

Note: Static files are served via /files/ endpoint (configured in server.py)
Note: Health check is at /health (configured in server.py)
"""

import time
import subprocess
import asyncio
import os
from pathlib import Path
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.models import ProgressUpdate

# Import song generation core functions
from scripts.lyrics.idea_to_lyrics import generate_ideas_core, generate_lyrics_core
from scripts.midi.generate_melody import generate_melody_core
from scripts.midi.continue_melody import continue_melody_core
from scripts.midi.harmonize_melody import harmonize_melody_core
from scripts.midi.generate_drums import generate_drums_core
from scripts.utils.midi_utils import create_midi_from_json, extract_melody_data
from scripts.audio.render_midi import render_complete_song_wav, render_instrumental_wav

# Create router for song generation endpoints
router = APIRouter(prefix="/api", tags=["Song Generation"])


async def send_progress(websocket: WebSocket, step: int, total: int, message: str):
    """Helper function to send progress updates via WebSocket"""
    percentage = int((step / total) * 100)
    progress = ProgressUpdate(
        step=step,
        total=total,
        message=message,
        percentage=percentage
    )
    await websocket.send_json(progress.dict())
    # Force flush to ensure message is sent immediately
    await asyncio.sleep(0)
    
    # Send heartbeat after each progress update to keep connection alive
    await asyncio.sleep(0.1)
    await websocket.send_json({"type": "heartbeat"})
    await asyncio.sleep(0)


@router.websocket("/ws/generate-song")
async def websocket_generate_song(websocket: WebSocket):
    """
    WebSocket endpoint for song generation with real-time progress updates.
    
    Client connects and sends: {"theme": "summer romance"}
    Server streams progress: {"step": 1, "total": 7, "message": "Generating lyrics...", "percentage": 14}
    Final message includes result: {"step": 7, "total": 7, "message": "Complete! ✓", "percentage": 100, "status": "success", "result": {...}}
    
    Usage from frontend:
        const ws = new WebSocket('ws://localhost:8000/api/ws/generate-song');
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log(`Step ${data.step}/${data.total}: ${data.message} (${data.percentage}%)`);
        };
        ws.send(JSON.stringify({theme: "summer romance"}));
    """
    await websocket.accept()
    
    try:
        # Receive request data from client
        data = await websocket.receive_json()
        theme = data.get("theme")
        provider = data.get("provider", "").lower()
        
        if not theme:
            await websocket.send_json({
                "error": "Theme is required",
                "status": "error"
            })
            await websocket.close()
            return
        
        # Set AI provider based on user selection (or keep default from .env)
        if provider == "google":
            os.environ["PROVIDER"] = "google"
            os.environ["USE_CLOUD"] = "True"
        elif provider == "openai":
            os.environ["PROVIDER"] = "openai"
            os.environ["USE_CLOUD"] = "True"
        
        # Reload cfg to pick up new env vars
        from scripts.utils import cfg
        import importlib
        importlib.reload(cfg)
        
        # Generate unique timestamp for filenames
        timestamp = int(time.time())
        
        # Sanitize theme for filename
        safe_theme = "".join(c for c in theme if c.isalnum() or c in (' ', '-', '_'))
        safe_theme = safe_theme.replace(' ', '_').lower()[:50]
        base_name = f"{safe_theme}_{timestamp}"
        
        # Create output directories
        output_dir = Path("output")
        songs_dir = output_dir / "songs"
        midi_dir = output_dir / "midi"
        
        for d in [songs_dir, midi_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Step 1/9: Generate lyrics
        await send_progress(websocket, 1, 9, "Generating lyrics...")
        idea = generate_ideas_core(theme, count=1)
        lyrics = generate_lyrics_core(idea)
        lyrics_path = songs_dir / f"{base_name}.txt"
        lyrics_path.write_text(f"# Song Concept\n\n{idea}\n\n{'='*60}\n\n# Lyrics\n\n{lyrics}", encoding='utf-8')
        
        # Step 2/9: Generate melody
        await send_progress(websocket, 2, 9, "Creating melody...")
        melody_data = generate_melody_core(theme)
        melody_path = midi_dir / f"{base_name}_melody.mid"
        create_midi_from_json(melody_data, melody_path)
        
        # Step 3/9: Generate continuation
        await send_progress(websocket, 3, 9, "Adding continuation...")
        continuation_data = continue_melody_core(melody_path)
        continuation_path = midi_dir / f"{base_name}_continuation.mid"
        create_midi_from_json(continuation_data, continuation_path)
        
        # Step 4/9: Generate harmony
        await send_progress(websocket, 4, 9, "Generating harmony...")
        harmony_data = harmonize_melody_core(melody_path, continuation_path)
        harmony_path = midi_dir / f"{base_name}_harmony.mid"
        create_midi_from_json(harmony_data, harmony_path)
        
        # Step 5/9: Generate drums
        await send_progress(websocket, 5, 9, "Creating drum pattern...")
        melody_info = extract_melody_data(melody_path)
        tempo = melody_info['tempo']
        drums_data = generate_drums_core(tempo, "steady beat with emotional fills", measures=8)
        drums_path = midi_dir / f"{base_name}_drums.mid"
        create_midi_from_json(drums_data, drums_path)
        
        # Step 6/9: Generate vocals
        await send_progress(websocket, 6, 9, "Generating vocal melody...")
        vocals_path = midi_dir / f"{base_name}_vocals.mid"
        
        # Use subprocess with heartbeats (vocal generation is slow)
        process = subprocess.Popen([
            "python", "scripts/midi/generate_vocal_melody.py",
            str(melody_path),
            str(continuation_path),
            str(harmony_path),
            "--lyrics", str(lyrics_path),
            "-o", str(vocals_path)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        
        # Send heartbeats while subprocess runs to keep connection alive
        while process.poll() is None:
            await asyncio.sleep(1)
            try:
                await websocket.send_json({"type": "heartbeat"})
                await asyncio.sleep(0)  # Flush
            except Exception:
                # Connection closed, stop heartbeats
                break
        
        # Get final result
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            await websocket.send_json({
                "error": f"Vocal generation failed: {stderr}",
                "status": "error"
            })
            await websocket.close()
            return
        
        # Check if vocal WAV was generated (filename includes _melody prefix)
        vocal_wav_path = output_dir / "audio" / f"{base_name}_melody_vocals.wav"
        print(f"🔍 Checking for vocal WAV at: {vocal_wav_path}")
        print(f"🔍 WAV exists: {vocal_wav_path.exists()}")
        vocal_wav_url = f"/files/audio/{base_name}_melody_vocals.wav" if vocal_wav_path.exists() else None
        print(f"🔍 vocal_wav_url: {vocal_wav_url}")
        
        # Step 7/9: Arrange final song
        await send_progress(websocket, 7, 9, "Arranging final song...")
        arranged_path = midi_dir / f"{base_name}_complete.mid"
        
        # Use Popen so we can send heartbeats during long operations
        process = subprocess.Popen([
            "python", "scripts/midi/arrange_song.py",
            "-m", str(melody_path),
            "-c", str(continuation_path),
            "-h", str(harmony_path),
            "-d", str(drums_path),
            "-v", str(vocals_path),
            "-o", str(arranged_path)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        
        # Send heartbeats while subprocess runs to keep connection alive
        while process.poll() is None:
            await asyncio.sleep(1)
            try:
                await websocket.send_json({"type": "heartbeat"})
                await asyncio.sleep(0)  # Flush
            except Exception:
                # Connection closed, stop heartbeats
                break
        
        # Get final result
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            await websocket.send_json({
                "error": f"Arrangement failed: {stderr}",
                "status": "error"
            })
            await websocket.close()
            return
        
        # Step 8/9: Render complete WAV (all tracks including vocals)
        await send_progress(websocket, 8, 9, "Rendering complete audio (with vocals)...")
        audio_dir = output_dir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        complete_wav_path = audio_dir / f"{base_name}_complete.wav"
        try:
            render_complete_song_wav(arranged_path, complete_wav_path)
            complete_wav_url = f"/files/audio/{base_name}_complete.wav"
            print(f"✅ Rendered complete WAV: {complete_wav_path}")
        except Exception as e:
            print(f"⚠️ Failed to render complete WAV: {e}")
            complete_wav_url = None
        
        # Step 9/9: Render instrumental WAV (no vocals)
        await send_progress(websocket, 9, 9, "Rendering instrumental audio (no vocals)...")
        instrumental_wav_path = audio_dir / f"{base_name}_instrumental.wav"
        try:
            render_instrumental_wav(arranged_path, instrumental_wav_path)
            instrumental_wav_url = f"/files/audio/{base_name}_instrumental.wav"
            print(f"✅ Rendered instrumental WAV: {instrumental_wav_path}")
        except Exception as e:
            print(f"⚠️ Failed to render instrumental WAV: {e}")
            instrumental_wav_url = None
        
        # Send final completion message with result
        midi_url = f"/files/midi/{base_name}_complete.mid"
        vocals_midi_url = f"/files/midi/{base_name}_vocals.mid"
        
        result_data = {
            "theme": theme,
            "lyrics": lyrics,
            "midi_url": midi_url,
            "vocals_midi_url": vocals_midi_url,
            "timestamp": timestamp
        }
        
        # Add WAV URLs if they exist
        if complete_wav_url:
            result_data["complete_wav_url"] = complete_wav_url
            print(f"✅ Added complete_wav_url to result: {complete_wav_url}")
        
        if instrumental_wav_url:
            result_data["instrumental_wav_url"] = instrumental_wav_url
            print(f"✅ Added instrumental_wav_url to result: {instrumental_wav_url}")
        
        # Add vocal WAV URL if it exists (from singing synthesis)
        if vocal_wav_url:
            result_data["vocal_wav_url"] = vocal_wav_url
            print(f"✅ Added vocal_wav_url to result: {vocal_wav_url}")
        else:
            print(f"⚠️ No vocal WAV found, not adding to result")
        
        await websocket.send_json({
            "step": 9,
            "total": 9,
            "message": "Complete! ✓",
            "percentage": 100,
            "status": "success",
            "result": result_data
        })
        
        await websocket.close()
        
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({
            "error": str(e),
            "status": "error"
        })
        await websocket.close()

