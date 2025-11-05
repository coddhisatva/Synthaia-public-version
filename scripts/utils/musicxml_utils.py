"""
MusicXML utilities for Synthaia.
Converts MIDI data and lyrics into MusicXML format for Sinsy singing synthesis.
"""

from pathlib import Path
from music21 import stream, note, tempo, key, meter, chord


def create_musicxml_with_lyrics(
    vocal_data: dict,
    word_mapping: list,
    output_path: Path,
) -> Path:
    """
    Convert vocal MIDI data and word mapping to MusicXML with embedded lyrics.
    
    This creates a MusicXML score suitable for Sinsy AI singing synthesis.
    Each note gets its corresponding lyric/syllable attached.
    
    Args:
        vocal_data: Dict with 'tempo', 'key', 'scale', 'notes' (from LLM)
        word_mapping: List of (word, pitch, start_time, duration) tuples
        output_path: Where to save the MusicXML file
    
    Returns:
        Path to created MusicXML file
    
    Example:
        vocal_data = {
            'tempo': 120,
            'key': 'C',
            'scale': 'major',
            'notes': [{'pitch': 60, 'duration': 0.5}, ...]
        }
        word_mapping = [('Hello', 60, 0.0, 0.5), ('world', 62, 0.5, 0.5)]
        create_musicxml_with_lyrics(vocal_data, word_mapping, Path('vocals.musicxml'))
    """
    print(f"[CREATE_MUSICXML] Starting")
    print(f"[CREATE_MUSICXML] Tempo: {vocal_data['tempo']} BPM")
    print(f"[CREATE_MUSICXML] Key: {vocal_data['key']} {vocal_data.get('scale', 'major')}")
    print(f"[CREATE_MUSICXML] Words to map: {len(word_mapping)}")
    print(f"[CREATE_MUSICXML] Output: {output_path}")
    
    # Create score structure
    score = stream.Score()
    part = stream.Part()
    
    # Add tempo marking
    part.append(tempo.MetronomeMark(number=vocal_data['tempo']))
    
    # Add key signature
    try:
        key_obj = key.Key(vocal_data['key'])
        part.append(key_obj)
    except Exception as e:
        part.append(key.Key('C'))
    
    # Add time signature (assume 4/4)
    part.append(meter.TimeSignature('4/4'))
    
    # Convert word mapping to notes with lyrics
    # Sort by start time to ensure proper order
    word_mapping_sorted = sorted(word_mapping, key=lambda x: x[2])
    
    for word, pitch, start_time, duration in word_mapping_sorted:
        # Skip rests (pitch 0 or None)
        if not pitch or pitch == 0:
            # Add rest instead
            rest_duration = _beats_to_quarter_length(duration, vocal_data['tempo'])
            r = note.Rest()
            r.quarterLength = rest_duration
            part.append(r)
            continue
        
        # Create note
        try:
            n = note.Note(pitch)
        except Exception as e:
            continue
        
        # Convert duration from seconds to quarter notes
        # Duration in beats = duration_seconds * (tempo / 60)
        n.quarterLength = _beats_to_quarter_length(duration, vocal_data['tempo'])
        
        # Attach lyric to note
        n.lyric = word
        
        part.append(n)
    
    # Add part to score
    score.append(part)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to MusicXML
    score.write('musicxml', fp=str(output_path))
    
    file_size = output_path.stat().st_size
    print(f"[CREATE_MUSICXML] File written: {file_size} bytes ({file_size/1024:.1f} KB)")
    print(f"[CREATE_MUSICXML] Complete")
    return output_path


def _beats_to_quarter_length(duration_seconds: float, tempo_bpm: int) -> float:
    """
    Convert duration in seconds to quarter note length.
    
    Args:
        duration_seconds: Duration in seconds
        tempo_bpm: Tempo in beats per minute
    
    Returns:
        Duration in quarter notes
    
    Example:
        At 120 BPM:
        - 1 beat = 0.5 seconds
        - 0.5 seconds = 1.0 quarter note
        
        At 60 BPM:
        - 1 beat = 1.0 second
        - 1.0 second = 1.0 quarter note
    """
    # Beats per second = tempo / 60
    beats_per_second = tempo_bpm / 60.0
    
    # Duration in beats = duration_seconds * beats_per_second
    duration_beats = duration_seconds * beats_per_second
    
    # In 4/4 time, 1 beat = 1 quarter note
    quarter_length = duration_beats
    
    # Ensure minimum duration (avoid zero-length notes)
    return max(quarter_length, 0.25)

