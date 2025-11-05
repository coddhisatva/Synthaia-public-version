#!/usr/bin/env python3
"""
Render MIDI to WAV for testing.

Usage:
    python test_wav_export.py take_back_the_edge_1761869798
    
This will:
1. Find output/midi/take_back_the_edge_1761869798_complete.mid
2. Render complete WAV (all tracks) to output/audio/
3. Render instrumental WAV (no vocals) to output/audio/
4. Keep both files so you can listen!
"""

import sys
from pathlib import Path
from scripts.audio.render_midi import render_complete_song_wav, render_instrumental_wav

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_wav_export.py <song_base_name>")
        print()
        print("Example: python test_wav_export.py take_back_the_edge_1761869798")
        print()
        print("This will find:")
        print("  output/midi/take_back_the_edge_1761869798_complete.mid")
        print("And create:")
        print("  output/audio/take_back_the_edge_1761869798_complete.wav")
        print("  output/audio/take_back_the_edge_1761869798_instrumental.wav")
        sys.exit(1)
    
    base_name = sys.argv[1]
    
    # Paths
    midi_dir = Path("output/midi")
    audio_dir = Path("output/audio")
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    midi_file = midi_dir / f"{base_name}_complete.mid"
    complete_wav = audio_dir / f"{base_name}_complete.wav"
    instrumental_wav = audio_dir / f"{base_name}_instrumental.wav"
    
    # Check if MIDI exists
    if not midi_file.exists():
        print(f"❌ ERROR: MIDI file not found: {midi_file}")
        print()
        print("Available songs in output/midi/:")
        complete_files = sorted(midi_dir.glob("*_complete.mid"))
        if complete_files:
            for f in complete_files[:10]:  # Show first 10
                base = f.stem.replace("_complete", "")
                print(f"  - {base}")
            if len(complete_files) > 10:
                print(f"  ... and {len(complete_files) - 10} more")
        else:
            print("  (none found - generate a song first!)")
        sys.exit(1)
    
    print("="*60)
    print("🎵 WAV EXPORT TEST")
    print("="*60)
    print(f"Song: {base_name}")
    print(f"MIDI: {midi_file.name}")
    print()
    
    # Render complete WAV
    print("Step 1/2: Rendering complete WAV (with vocals)...")
    print("  This may take 10-30 seconds...")
    try:
        render_complete_song_wav(midi_file, complete_wav)
        size_mb = complete_wav.stat().st_size / (1024 * 1024)
        print(f"  ✅ Complete WAV: {complete_wav.name} ({size_mb:.2f} MB)")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        sys.exit(1)
    
    print()
    
    # Render instrumental WAV
    print("Step 2/2: Rendering instrumental WAV (no vocals)...")
    print("  This may take 10-30 seconds...")
    try:
        render_instrumental_wav(midi_file, instrumental_wav)
        size_mb = instrumental_wav.stat().st_size / (1024 * 1024)
        print(f"  ✅ Instrumental WAV: {instrumental_wav.name} ({size_mb:.2f} MB)")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        sys.exit(1)
    
    print()
    print("="*60)
    print("✅ SUCCESS!")
    print("="*60)
    print(f"Complete WAV:     {complete_wav}")
    print(f"Instrumental WAV: {instrumental_wav}")
    print()
    print("🎧 Open them in your audio player and listen!")

if __name__ == "__main__":
    main()
