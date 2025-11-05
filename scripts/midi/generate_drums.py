"""
Generate a MIDI drum pattern based on text description.

Usage:
    python scripts/midi/generate_drums.py melody.mid "energetic rock beat"
    python scripts/midi/generate_drums.py melody.mid "start epic, end with tom fill" -o drums.mid
    python scripts/midi/generate_drums.py melody.mid "hip hop groove" --measures 16
"""

import json
from pathlib import Path
import typer
from mido import MidiFile, MidiTrack, Message, MetaMessage
from scripts.utils.llm_client import call_llm
from scripts.utils.midi_utils import load_prompt

app = typer.Typer()


def extract_tempo(midi_file_path: Path) -> int:
    """
    Extract only the tempo from a MIDI file.
    
    Args:
        midi_file_path: Path to the MIDI file
    
    Returns:
        Tempo in BPM (default 120 if not found)
    """
    midi = MidiFile(str(midi_file_path))
    
    # Extract tempo
    for track in midi.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                return int(60_000_000 / msg.tempo)
    
    return 120  # Default tempo


def create_drum_midi(drum_data: dict, output_path: Path) -> None:
    """
    Convert JSON drum data to MIDI file.
    
    Args:
        drum_data: Dict with tempo, measures, and notes
        output_path: Where to save the MIDI file
    """
    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)
    
    # Set tempo
    tempo = drum_data.get("tempo", 120)
    microseconds_per_beat = int(60_000_000 / tempo)
    track.append(MetaMessage('set_tempo', tempo=microseconds_per_beat))
    
    # Set time signature
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))
    
    # Set to MIDI channel 10 (drums)
    track.append(Message('program_change', program=0, channel=9, time=0))
    
    # Sort notes by time
    notes = sorted(drum_data.get("notes", []), key=lambda n: n.get("time", 0))
    
    ticks_per_beat = midi.ticks_per_beat
    current_time = 0
    
    # Group notes by time (for simultaneous hits)
    note_events = []
    for note_data in notes:
        start_time = note_data.get("time", 0.0)
        pitch = note_data.get("pitch", 36)
        velocity = note_data.get("velocity", 80)
        duration = note_data.get("duration", 0.25)
        
        note_events.append({
            "type": "on",
            "time": start_time,
            "pitch": pitch,
            "velocity": velocity
        })
        note_events.append({
            "type": "off",
            "time": start_time + duration,
            "pitch": pitch,
            "velocity": 0
        })
    
    # Sort all events by time
    note_events.sort(key=lambda e: e["time"])
    
    # Write events to track
    for event in note_events:
        event_time_ticks = int(event["time"] * ticks_per_beat)
        delta_time = event_time_ticks - current_time
        
        if event["type"] == "on":
            track.append(Message('note_on', note=event["pitch"], velocity=event["velocity"], 
                               channel=9, time=delta_time))
        else:
            track.append(Message('note_off', note=event["pitch"], velocity=0, 
                               channel=9, time=delta_time))
        
        current_time = event_time_ticks
    
    # End of track
    track.append(MetaMessage('end_of_track'))
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    midi.save(str(output_path))


def generate_drums_core(
    tempo: int,
    description: str,
    measures: int = 8,
    temperature: float = 0.8,
) -> dict:
    """
    Core logic to generate drum pattern.
    
    Args:
        tempo: Tempo in BPM
        description: Text description of the drum vibe/pattern
        measures: Number of measures (default: 8)
        temperature: Creativity level (0.0-1.0)
    
    Returns:
        Dictionary with drum pattern data
    """
    system_prompt = load_prompt("drums")
    
    total_beats = measures * 4  # Assuming 4/4 time
    
    user_prompt = f"""Generate a drum pattern with this vibe:

"{description}"

Requirements:
- Tempo: {tempo} BPM
- Time signature: 4/4
- MUST be exactly {measures} measures = {total_beats} beats long
- Pattern MUST span from beat 0.0 all the way to beat {total_beats}.0
- Use dynamics and fills to match the described vibe
- Remember: multiple drums can play at the same time (same time value)

CRITICAL: The pattern must be FULL LENGTH - {total_beats} beats total. Do NOT create a shorter pattern (like {measures//2} measures). Fill the entire {total_beats} beat duration.

IMPORTANT: Return pure JSON only. Do NOT include any comments (// or /* */) in the JSON.

Generate a musical, production-ready drum pattern."""
    
    # Retry logic for flaky LLM responses
    max_retries = 3
    import time
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"⚠️  Retry attempt {attempt + 1}/{max_retries}...")
                time.sleep(1)  # Brief pause between retries
            
            response = call_llm(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=15000,  # Drum patterns have MANY notes - need lots of tokens
            )
            
            # Check for empty response
            if not response or len(response.strip()) == 0:
                raise ValueError("Empty response from LLM")
            
            # Clean up response
            response = response.strip()
            if response.startswith("```"):
                lines = response.split('\n')
                response = '\n'.join(lines[1:-1])
            
            # Remove // comments from JSON (LLMs love to add these)
            import re
            response = re.sub(r'//.*$', '', response, flags=re.MULTILINE)
            
            drum_data = json.loads(response)
            
            # Ensure tempo matches
            drum_data["tempo"] = tempo
            drum_data["measures"] = measures
            
            print(f"✓ Successfully generated drums on attempt {attempt + 1}")
            return drum_data
            
        except (json.JSONDecodeError, ValueError) as e:
            if attempt == max_retries - 1:
                # Last attempt failed, raise error
                raise ValueError(f"LLM did not return valid JSON after {max_retries} attempts: {e}\nLast response: {response}")
            # Otherwise continue to next retry
            print(f"⚠️  Attempt {attempt + 1} failed: {e}")


@app.command()
def generate(
    reference_midi: str = typer.Argument(..., help="Reference MIDI file (to extract tempo)"),
    description: str = typer.Argument(..., help="Drum vibe/pattern description"),
    measures: int = typer.Option(8, "--measures", "-m", help="Number of measures"),
    temperature: float = typer.Option(0.8, "--temp", "-t", help="Creativity level (0.0-1.0)"),
    output: str = typer.Option(None, "--output", "-o", help="Output MIDI file path"),
):
    """
    Generate MIDI drums that match your song's tempo and vibe.
    
    Extracts tempo from reference MIDI, then generates drums based on your description.
    Default is 8 measures (matching your typical workflow).
    
    Examples:
        generate_drums.py melody.mid "energetic rock beat"
        generate_drums.py song.mid "start epic, intense fill, end on toms" -o drums.mid
        generate_drums.py track.mid "simple hip hop groove" --measures 16
    """
    reference_path = Path(reference_midi)
    
    if not reference_path.exists():
        typer.echo(f"Error: Reference file not found: {reference_midi}", err=True)
        raise typer.Exit(1)
    
    # Extract tempo from reference
    tempo = extract_tempo(reference_path)
    
    typer.echo(f"🥁 Generating drums...")
    typer.echo(f"   Tempo: {tempo} BPM (from {reference_midi})")
    typer.echo(f"   Measures: {measures}")
    typer.echo(f"   Vibe: {description}")
    typer.echo()
    
    # Generate drums
    try:
        drum_data = generate_drums_core(tempo, description, measures, temperature)
        typer.echo(f"✓ Drums generated!")
        typer.echo(f"  Tempo: {drum_data.get('tempo')} BPM")
        typer.echo(f"  Measures: {drum_data.get('measures')}")
        typer.echo(f"  Notes: {len(drum_data.get('notes', []))} drum hits")
        typer.echo()
    except Exception as e:
        typer.echo(f"Error generating drums: {e}", err=True)
        raise typer.Exit(1)
    
    # Determine output path
    if output:
        output_path = Path(output)
    else:
        # Auto-generate filename
        output_path = reference_path.parent / f"{reference_path.stem}_drums.mid"
    
    # Create MIDI file
    try:
        create_drum_midi(drum_data, output_path)
        typer.echo(f"✓ Drum MIDI saved to: {output_path}")
    except Exception as e:
        typer.echo(f"Error creating MIDI file: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo()
    typer.echo("✓ Done! In GarageBand:")
    typer.echo("   1. Create new Software Instrument track")
    typer.echo("   2. Choose a drum kit")
    typer.echo("   3. Drag in the drum MIDI file")


if __name__ == "__main__":
    app()

