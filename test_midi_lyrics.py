"""
Test script for MIDI with embedded lyrics functionality.

This creates a simple MIDI file with a few notes and lyrics to test
that the Synth V VST can read the embedded lyric meta-events.
"""

from pathlib import Path
from scripts.utils.midi_utils import create_midi_from_json

# Create a simple test melody
test_melody = {
    "tempo": 120,
    "key": "C",
    "scale": "major",
    "notes": [
        {"pitch": 60, "duration": 1.0},  # C4, 1 beat
        {"pitch": 62, "duration": 1.0},  # D4, 1 beat
        {"pitch": 64, "duration": 1.0},  # E4, 1 beat
        {"pitch": 65, "duration": 2.0},  # F4, 2 beats
    ]
}

# Create word mapping (word, pitch, start_time_seconds, duration_seconds)
# At 120 BPM, 1 beat = 0.5 seconds
test_lyrics = [
    ("Hel-", 60, 0.0, 0.5),   # First syllable
    ("lo", 62, 0.5, 0.5),     # Second syllable
    ("my", 64, 1.0, 0.5),     # Third word
    ("friend", 65, 1.5, 1.0), # Fourth word (longer)
]

# Output path
output_path = Path("output/midi/test_with_lyrics.mid")

print("Creating test MIDI with embedded lyrics...")
print(f"Notes: {len(test_melody['notes'])}")
print(f"Lyrics: {len(test_lyrics)}")
print()

create_midi_from_json(test_melody, output_path, word_mapping=test_lyrics)

print(f"✓ Created: {output_path}")
print()
print("Next steps:")
print("1. Open REAPER")
print("2. Add Synth V VST to a track")
print("3. Drag this MIDI file onto the track")
print("4. Check if Synth V shows the lyrics: 'Hel-lo my friend'")
print("5. Set voice to SOLARIA II")
print("6. Play/render to test")

