"""
Shared MIDI utility functions for reading, writing, and processing MIDI files.
"""

from pathlib import Path
from mido import MidiFile, MidiTrack, Message, MetaMessage


def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt template from the prompts directory.
    
    Args:
        prompt_name: Name of the prompt file (without .md extension)
    
    Returns:
        Prompt text content
    """
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "midi" / f"{prompt_name}.md"
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    return prompt_path.read_text()


def extract_melody_data(midi_file_path: Path) -> dict:
    """
    Extract melody information from a MIDI file.
    
    Args:
        midi_file_path: Path to the MIDI file
    
    Returns:
        Dictionary with tempo, notes list, and ticks_per_beat
    """
    midi = MidiFile(str(midi_file_path))
    
    # Extract tempo (default 120 BPM)
    tempo = 120
    for track in midi.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = int(60_000_000 / msg.tempo)
                break
    
    # Extract notes
    notes = []
    current_time = 0
    ticks_per_beat = midi.ticks_per_beat
    
    for track in midi.tracks:
        note_on_times = {}
        
        for msg in track:
            current_time += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                note_on_times[msg.note] = current_time
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in note_on_times:
                    start_time = note_on_times[msg.note]
                    duration_ticks = current_time - start_time
                    duration_beats = duration_ticks / ticks_per_beat
                    
                    notes.append({
                        "pitch": msg.note,
                        "duration": round(duration_beats, 2),
                        "start_time": start_time / ticks_per_beat
                    })
                    del note_on_times[msg.note]
    
    return {
        "tempo": tempo,
        "notes": notes,
        "ticks_per_beat": ticks_per_beat
    }


def create_midi_from_json(melody_data: dict, output_path: Path, velocity: int = 64, word_mapping: list = None) -> None:
    """
    Convert JSON melody data to MIDI file, optionally with embedded lyrics.
    
    Args:
        melody_data: Dict with tempo, key, scale, and notes
        output_path: Where to save the MIDI file
        velocity: MIDI velocity (volume) for notes (default: 64)
        word_mapping: Optional list of (word, pitch, start_time_seconds, duration_seconds) tuples
                     for embedding lyrics as MIDI meta-events
    """
    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)
    
    # Set tempo (convert BPM to microseconds per beat)
    tempo = melody_data.get("tempo", 120)
    microseconds_per_beat = int(60_000_000 / tempo)
    track.append(MetaMessage('set_tempo', tempo=microseconds_per_beat))
    
    # Set time signature (4/4)
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))
    
    ticks_per_beat = midi.ticks_per_beat
    
    # If we have lyrics, build events with absolute times then sort
    if word_mapping:
        events = []
        current_tick = 0
        
        # Add notes from melody_data
        for note_data in melody_data.get("notes", []):
            pitch = note_data.get("pitch", 60)
            duration = note_data.get("duration", 1.0)
            duration_ticks = int(duration * ticks_per_beat)
            
            if pitch == 0:
                # Rest - just advance time
                current_tick += duration_ticks
            else:
                # Note on
                events.append((current_tick, Message('note_on', note=pitch, velocity=velocity)))
                # Note off
                events.append((current_tick + duration_ticks, Message('note_off', note=pitch, velocity=velocity)))
                current_tick += duration_ticks
        
        # Add lyrics from word_mapping
        for word, pitch, start_time_seconds, duration_seconds in word_mapping:
            # Convert start time from seconds to ticks
            # Ticks = seconds * (tempo BPM / 60 seconds/min) * ticks_per_beat
            start_tick = int((start_time_seconds * tempo / 60.0) * ticks_per_beat)
            
            # Add lyric event at the start of the note
            # MIDI uses latin-1, so replace Unicode punctuation with ASCII equivalents
            clean_word = (word
                .replace('\u2019', "'")   # Right single quote (')
                .replace('\u2018', "'")   # Left single quote (')
                .replace('\u201c', '"')   # Left double quote (")
                .replace('\u201d', '"')   # Right double quote (")
                .replace('\u201e', '"')   # Double low-9 quote („)
                .replace('\u201f', '"')   # Double high-reversed-9 quote (‟)
                .replace('\u2014', '-')   # Em dash (—)
                .replace('\u2013', '-')   # En dash (–)
                .replace('\u2012', '-')   # Figure dash (‒)
                .replace('\u2015', '-')   # Horizontal bar (―)
                .replace('\u2026', '...') # Ellipsis (…)
                .replace('\u2022', '*')   # Bullet (•)
                .replace('\u00a0', ' ')   # Non-breaking space
                .replace('\u2002', ' ')   # En space
                .replace('\u2003', ' ')   # Em space
                .replace('\u2009', ' ')   # Thin space
                .replace('\u00ab', '"')   # Left guillemet («)
                .replace('\u00bb', '"')   # Right guillemet (»)
                .replace('\u2032', "'")   # Prime (′)
                .replace('\u2033', '"')   # Double prime (″)
                .replace('\u02bc', "'")   # Modifier letter apostrophe (ʼ)
            )
            # Remove any remaining non-latin-1 characters
            clean_word = clean_word.encode('latin-1', errors='ignore').decode('latin-1')
            events.append((start_tick, MetaMessage('lyrics', text=clean_word)))
        
        # Sort all events by absolute time
        events.sort(key=lambda x: x[0])
        
        # Convert to delta times and append to track
        last_tick = 0
        for abs_tick, msg in events:
            delta_tick = abs_tick - last_tick
            msg.time = delta_tick
            track.append(msg)
            last_tick = abs_tick
    else:
        # Original code path (no lyrics)
        for note_data in melody_data.get("notes", []):
            pitch = note_data.get("pitch", 60)
            duration = note_data.get("duration", 1.0)
            
            # Convert duration in beats to ticks
            ticks = int(duration * ticks_per_beat)
            
            if pitch == 0:
                # Rest - just wait
                track.append(Message('note_on', note=60, velocity=0, time=ticks))
            else:
                # Note on
                track.append(Message('note_on', note=pitch, velocity=velocity, time=0))
                # Note off
                track.append(Message('note_off', note=pitch, velocity=velocity, time=ticks))
    
    # End of track
    track.append(MetaMessage('end_of_track'))
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    midi.save(str(output_path))

