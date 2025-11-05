"""
Test PySinsy vocal generation with a simple example.
"""

from pathlib import Path
from scripts.midi.generate_vocal_melody import generate_vocal_audio

# Create simple test data
vocal_data = {
    "tempo": 120,
    "key": "C",
    "scale": "major",
    "notes": [
        {"pitch": 60, "duration": 1.0},  # C4
        {"pitch": 62, "duration": 1.0},  # D4
        {"pitch": 64, "duration": 1.0},  # E4
        {"pitch": 65, "duration": 2.0},  # F4
    ]
}

# Word mapping (word, pitch, start_time_seconds, duration_seconds)
# At 120 BPM, 1 beat = 0.5 seconds
word_mapping = [
    ("Hello", 60, 0.0, 0.5),
    ("my", 62, 0.5, 0.5),
    ("dear", 64, 1.0, 0.5),
    ("friend", 65, 1.5, 1.0),
]

# Output path
output_path = Path("output/audio/test_pysinsy_vocals.wav")

print("Testing PySinsy vocal generation...")
print(f"Notes: {len(vocal_data['notes'])}")
print(f"Lyrics: {' '.join([w[0] for w in word_mapping])}")
print()

try:
    wav_path = generate_vocal_audio(vocal_data, word_mapping, output_path)
    print(f"\n✓ Success! Generated: {wav_path}")
    print("\nPlay the file to hear PySinsy singing!")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

