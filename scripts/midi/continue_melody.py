"""
Generate a continuation for an existing MIDI melody.

Usage:
    python scripts/midi/continue_melody.py input.mid
    python scripts/midi/continue_melody.py input.mid -o output.mid
"""

import json
from pathlib import Path
import typer
from scripts.utils.llm_client import call_llm
from scripts.utils.midi_utils import load_prompt, extract_melody_data, create_midi_from_json

app = typer.Typer()


def continue_melody_core(
    input_midi_path: Path,
    temperature: float = 0.8,
) -> dict:
    """
    Core logic to generate melody continuation.
    
    Args:
        input_midi_path: Path to input MIDI file
        temperature: Creativity level (0.0-1.0)
    
    Returns:
        Dictionary with continuation melody data
    """
    # Extract original melody
    original = extract_melody_data(input_midi_path)
    
    # Build prompt with original melody context
    system_prompt = load_prompt("continuation")
    
    # Format the original notes for the LLM
    notes_summary = []
    for i, note in enumerate(original["notes"][:8]):  # Show first 8 notes
        notes_summary.append(f"Note {i+1}: pitch={note['pitch']}, duration={note['duration']}")
    
    user_prompt = f"""Continue this melody:

Original melody:
- Tempo: {original['tempo']} BPM
- Number of notes: {len(original['notes'])}
- First notes: {', '.join([f"pitch {n['pitch']}" for n in original['notes'][:8]])}

Generate a continuation of approximately {len(original['notes'])} notes that completes this musical idea."""
    
    response = call_llm(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=6000,  # Extra tokens for continuation analysis + output
    )
    
    # Parse JSON response
    try:
        # Clean up response - remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```"):
            # Remove ```json and ``` markers
            lines = response.split('\n')
            response = '\n'.join(lines[1:-1])
        
        # Remove // comments from JSON (LLMs love to add these)
        import re
        response = re.sub(r'//.*$', '', response, flags=re.MULTILINE)
        
        melody_data = json.loads(response)
        
        # Ensure tempo matches original
        melody_data["tempo"] = original["tempo"]
        
        return melody_data
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON: {e}\nResponse: {response}")


@app.command()
def generate(
    input_midi: str = typer.Argument(..., help="Input MIDI file to continue"),
    temperature: float = typer.Option(0.8, "--temp", "-t", help="Creativity level (0.0-1.0)"),
    output: str = typer.Option(None, "--output", "-o", help="Output MIDI file path"),
):
    """
    Generate a continuation for an existing MIDI melody.
    
    The continuation will match the tempo and style of the original,
    creating a complete musical phrase when played back-to-back.
    
    Examples:
        continue_melody.py input.mid
        continue_melody.py melody.mid -o melody_continuation.mid
        continue_melody.py original.mid --temp 0.9
    """
    input_path = Path(input_midi)
    
    if not input_path.exists():
        typer.echo(f"Error: Input file not found: {input_midi}", err=True)
        raise typer.Exit(1)
    
    typer.echo(f"🎵 Generating continuation for: {input_midi}")
    typer.echo()
    
    # Generate continuation
    try:
        continuation_data = continue_melody_core(input_path, temperature)
        typer.echo(f"✓ Continuation generated!")
        typer.echo(f"  Tempo: {continuation_data.get('tempo')} BPM")
        typer.echo(f"  Key: {continuation_data.get('key')} {continuation_data.get('scale')}")
        typer.echo(f"  Notes: {len(continuation_data.get('notes', []))} notes")
        typer.echo()
    except Exception as e:
        typer.echo(f"Error generating continuation: {e}", err=True)
        raise typer.Exit(1)
    
    # Determine output path
    if output:
        output_path = Path(output)
    else:
        # Auto-generate filename
        stem = input_path.stem
        output_path = input_path.parent / f"{stem}_continuation.mid"
    
    # Create MIDI file
    try:
        create_midi_from_json(continuation_data, output_path)
        typer.echo(f"✓ MIDI file saved to: {output_path}")
    except Exception as e:
        typer.echo(f"Error creating MIDI file: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo()
    typer.echo("✓ Done! Play both files back-to-back in your DAW.")


if __name__ == "__main__":
    app()

