"""
Synth V GUI Automation for macOS
Automates importing MIDI with lyrics and rendering to WAV
"""

import subprocess
import time
from pathlib import Path
import os


def render_vocals_with_synthv(
    midi_path: Path,
    output_wav_path: Path,
    voice: str = "SOLARIA II",
    timeout: int = 120
) -> Path:
    """
    Automate Synth V to import MIDI with lyrics and render to WAV.
    
    Args:
        midi_path: Path to MIDI file with embedded lyrics
        output_wav_path: Where to save the rendered WAV
        voice: Voice database to use (default: SOLARIA II)
        timeout: Maximum seconds to wait for render
    
    Returns:
        Path to rendered WAV file
    """
    print(f"[SYNTHV_AUTOMATION] Starting")
    print(f"[SYNTHV_AUTOMATION] MIDI input: {midi_path}")
    print(f"[SYNTHV_AUTOMATION] WAV output: {output_wav_path}")
    print(f"[SYNTHV_AUTOMATION] Voice: {voice}")
    
    # Ensure paths are absolute
    midi_path = midi_path.resolve()
    output_wav_path = output_wav_path.resolve()
    output_wav_path.parent.mkdir(parents=True, exist_ok=True)
    
    # AppleScript to automate Synth V
    applescript = f'''
    tell application "Synthesizer V Studio 2 Pro"
        activate
        delay 2
        
        -- Import MIDI file
        tell application "System Events"
            -- File menu -> Import
            keystroke "i" using {{command down}}
            delay 1
            
            -- Type file path in open dialog
            keystroke "{str(midi_path)}"
            delay 0.5
            keystroke "g" using {{command down, shift down}}
            delay 0.5
            keystroke "{str(midi_path)}"
            delay 0.5
            keystroke return
            delay 3
            
            -- Wait for import to complete
            delay 2
            
            -- TODO: Set voice to {voice}
            -- This might require clicking specific UI elements
            -- For now, assume voice is already selected
            
            -- Render to WAV
            -- File menu -> Render
            keystroke "r" using {{command down, shift down}}
            delay 2
            
            -- Set output path in save dialog
            keystroke "g" using {{command down, shift down}}
            delay 0.5
            keystroke "{str(output_wav_path.parent)}"
            delay 0.5
            keystroke return
            delay 1
            
            -- Set filename
            keystroke "a" using {{command down}}
            keystroke "{output_wav_path.name}"
            delay 0.5
            keystroke return
            
            -- Wait for render to complete
            delay 10
        end tell
        
        -- Close without saving
        tell application "System Events"
            keystroke "w" using {{command down}}
            delay 0.5
            keystroke "d" using {{command down}}  -- Don't save
        end tell
        
        quit
    end tell
    '''
    
    try:
        print("[SYNTHV_AUTOMATION] Launching Synth V...")
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            print(f"[SYNTHV_AUTOMATION] AppleScript error: {result.stderr}")
            raise Exception(f"Automation failed: {result.stderr}")
        
        # Wait a bit more for file to be written
        time.sleep(2)
        
        # Check if WAV was created
        if not output_wav_path.exists():
            raise Exception(f"WAV file not found at: {output_wav_path}")
        
        wav_size = output_wav_path.stat().st_size
        print(f"[SYNTHV_AUTOMATION] Success! WAV size: {wav_size} bytes")
        print(f"[SYNTHV_AUTOMATION] Complete: {output_wav_path}")
        
        return output_wav_path
        
    except subprocess.TimeoutExpired:
        raise Exception(f"Synth V automation timed out after {timeout} seconds")
    except Exception as e:
        raise Exception(f"Synth V automation failed: {e}")


if __name__ == "__main__":
    # Test the automation
    test_midi = Path("output/midi/test_with_lyrics.mid")
    test_wav = Path("output/audio/test_synthv_automation.wav")
    
    if not test_midi.exists():
        print(f"Error: Test MIDI not found: {test_midi}")
        print("Run test_midi_lyrics.py first to create it")
        exit(1)
    
    print("Testing Synth V automation...")
    print("NOTE: Do not touch keyboard/mouse during automation!")
    print()
    
    try:
        wav_path = render_vocals_with_synthv(test_midi, test_wav)
        print(f"\n✓ Success! Play the file: {wav_path}")
    except Exception as e:
        print(f"\n✗ Error: {e}")

