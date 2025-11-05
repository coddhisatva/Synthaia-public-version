"""
Generate a harmony/counter-melody for existing MIDI files.

Takes two MIDI files (e.g., melody + continuation) and generates a parallel
harmony track that amplifies at first, then diverges into counter-melody.

Usage:
    python scripts/midi/harmonize_melody.py part1.mid part2.mid
    python scripts/midi/harmonize_melody.py melody.mid continuation.mid -o harmony.mid
"""

import json
from pathlib import Path
import typer
from scripts.utils.llm_client import call_llm
from scripts.utils.midi_utils import load_prompt, extract_melody_data, create_midi_from_json

app = typer.Typer()


def combine_melodies(part1: dict, part2: dict) -> dict:
    """Combine two melody parts into one sequence."""
    # Calculate when part1 ends
    if part1["notes"]:
        part1_end = max(n['start_time'] + n['duration'] for n in part1["notes"])
    else:
        part1_end = 0
    
    # Offset part2 notes to start after part1
    part2_offset_notes = []
    for note in part2["notes"]:
        offset_note = note.copy()
        offset_note['start_time'] = note['start_time'] + part1_end
        part2_offset_notes.append(offset_note)
    
    combined_notes = part1["notes"] + part2_offset_notes
    
    return {
        "tempo": part1["tempo"],
        "notes": combined_notes
    }


def harmonize_melody_core(
    part1_path: Path,
    part2_path: Path,
    temperature: float = 0.8,
) -> dict:
    """
    Core logic to generate harmony/counter-melody.
    
    Args:
        part1_path: Path to first MIDI file
        part2_path: Path to second MIDI file
        temperature: Creativity level (0.0-1.0)
    
    Returns:
        Dictionary with harmony melody data
    """
    # Extract both parts
    part1 = extract_melody_data(part1_path)
    part2 = extract_melody_data(part2_path)
    
    # Combine into full melody
    combined = combine_melodies(part1, part2)
    
    # Build prompt
    system_prompt = load_prompt("harmonize")
    
    # Summarize the melody for the LLM
    total_notes = len(combined["notes"])
    first_part_notes = len(part1["notes"])
    
    # Show first 10 notes with their durations and timing
    notes_preview = []
    for i, note in enumerate(combined["notes"][:10]):
        notes_preview.append(f"pitch {note['pitch']} at beat {note['start_time']} (duration: {note['duration']})")
    
    # Calculate total duration (including gaps)
    if combined["notes"]:
        # Find when the last note ends (start_time + duration)
        last_note_end = max(n['start_time'] + n['duration'] for n in combined["notes"])
        total_duration = last_note_end
    else:
        total_duration = 0
    
    user_prompt = f"""Create a harmony/counter-melody for this combined melody:

Original melody:
- Tempo: {combined['tempo']} BPM
- Total notes: {total_notes}
- Total duration: {total_duration:.2f} beats
- Structure: {first_part_notes} notes in part 1, {total_notes - first_part_notes} notes in part 2
- First notes (with durations): {', '.join(notes_preview)}

CRITICAL REQUIREMENTS:
1. Generate EXACTLY {total_notes} notes - no more, no less
2. Match the rhythm pattern of the original melody (use similar note durations)
3. Total duration should be approximately {total_duration:.2f} beats
4. Transpose notes DOWN by approximately 12 semitones (1 octave lower); follow closely during the first {first_part_notes} notes (amplifying with thirds/fifths)
5. Gradually diverge more in the second half (counter-melody)
6. Gradually introduce variations in the second half for counter-melody effect

Look at the durations in the original melody and create similar rhythmic variety in your harmony.

Generate a harmony line that will be played by a second instrument (like electric guitar) while the original plays on piano.

OUTPUT INSTRUCTIONS: Return ONLY valid JSON. No explanations, no text before or after, no markdown formatting. Just the raw JSON object."""
    
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
                max_tokens=10000,  # Large: analyzing 2 files + generating full harmony
            )
            
            # Debug: Show response length
            print(f"DEBUG: Response length: {len(response)} chars")
            if len(response) < 500:
                print(f"DEBUG: Full response: {response}")
            
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
            
            harmony_data = json.loads(response)
            
            # Ensure tempo matches
            harmony_data["tempo"] = combined["tempo"]
            
            print(f"✓ Successfully generated harmony on attempt {attempt + 1}")
            return harmony_data
            
        except (json.JSONDecodeError, ValueError) as e:
            if attempt == max_retries - 1:
                # Last attempt failed, raise error
                raise ValueError(f"LLM did not return valid JSON after {max_retries} attempts: {e}\nLast response: {response}")
            # Otherwise continue to next retry
            print(f"⚠️  Attempt {attempt + 1} failed: {e}")


@app.command()
def generate(
    part1: str = typer.Argument(..., help="First MIDI file (original melody)"),
    part2: str = typer.Argument(..., help="Second MIDI file (continuation)"),
    temperature: float = typer.Option(0.8, "--temp", "-t", help="Creativity level (0.0-1.0)"),
    output: str = typer.Option(None, "--output", "-o", help="Output MIDI file path"),
):
    """
    Generate a harmony/counter-melody for two combined MIDI files.
    
    Creates a parallel track that:
    - Follows closely at first (amplifying the melody)
    - Diverges more towards the end (counter-melody)
    - Same tempo and total length as the combined original
    
    Perfect for adding a second instrument (electric guitar, synth, etc.) that
    plays simultaneously with the original melody.
    
    Examples:
        harmonize_melody.py melody.mid continuation.mid
        harmonize_melody.py part1.mid part2.mid -o harmony.mid
        harmonize_melody.py original.mid next.mid --temp 0.9
    """
    part1_path = Path(part1)
    part2_path = Path(part2)
    
    if not part1_path.exists():
        typer.echo(f"Error: First input file not found: {part1}", err=True)
        raise typer.Exit(1)
    
    if not part2_path.exists():
        typer.echo(f"Error: Second input file not found: {part2}", err=True)
        raise typer.Exit(1)
    
    typer.echo(f"🎵 Generating harmony for combined melodies:")
    typer.echo(f"   Part 1: {part1}")
    typer.echo(f"   Part 2: {part2}")
    typer.echo()
    
    # Generate harmony
    try:
        harmony_data = harmonize_melody_core(part1_path, part2_path, temperature)
        typer.echo(f"✓ Harmony generated!")
        typer.echo(f"  Tempo: {harmony_data.get('tempo')} BPM")
        typer.echo(f"  Key: {harmony_data.get('key')} {harmony_data.get('scale')}")
        typer.echo(f"  Notes: {len(harmony_data.get('notes', []))} notes")
        typer.echo()
    except Exception as e:
        typer.echo(f"Error generating harmony: {e}", err=True)
        raise typer.Exit(1)
    
    # Determine output path
    if output:
        output_path = Path(output)
    else:
        # Auto-generate filename
        output_path = part1_path.parent / f"{part1_path.stem}_harmony.mid"
    
    # Create MIDI file (with louder velocity for guitar/synth)
    try:
        create_midi_from_json(harmony_data, output_path, velocity=80)
        typer.echo(f"✓ Harmony MIDI saved to: {output_path}")
    except Exception as e:
        typer.echo(f"Error creating MIDI file: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo()
    typer.echo("✓ Done! In your DAW:")
    typer.echo("   Track 1 (Piano): Play part1 + part2 sequentially")
    typer.echo(f"   Track 2 (Guitar): Play {output_path.name} simultaneously")


if __name__ == "__main__":
    app()

