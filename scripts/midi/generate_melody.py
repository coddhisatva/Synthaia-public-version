"""
Generate a MIDI melody from a text description.

Usage:
    python scripts/midi/generate_melody.py "bunnies running through the field"
    python scripts/midi/generate_melody.py "dark stormy night" -o output/midi/storm.mid
"""

import json
from pathlib import Path
import typer
from scripts.utils.llm_client import call_llm
from scripts.utils.midi_utils import load_prompt, create_midi_from_json

app = typer.Typer()


def generate_melody_core(
    description: str,
    temperature: float = 0.8,
) -> dict:
    """
    Core logic to generate melody from text description.
    
    Args:
        description: Text describing the melody feeling/vibe
        temperature: Creativity level (0.0-1.0)
    
    Returns:
        Dictionary with melody data (tempo, key, notes)
    """
    system_prompt = load_prompt("melody")
    user_prompt = f"Create a melody for: {description}"
    
    response = call_llm(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=4000,  # 2.5-flash uses tokens for internal reasoning
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
        return melody_data
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON: {e}\nResponse: {response}")


@app.command()
def generate(
    description: str = typer.Argument(..., help="Text description of the melody"),
    temperature: float = typer.Option(0.8, "--temp", "-t", help="Creativity level (0.0-1.0)"),
    output: str = typer.Option(None, "--output", "-o", help="Output MIDI file path"),
):
    """
    Generate a MIDI melody from a text description.
    
    The AI will interpret your description and create a melody that matches
    the mood, energy, and imagery you describe.
    
    Examples:
        generate_melody.py "bunnies running through the field"
        generate_melody.py "dark and mysterious night" -o output/midi/mystery.mid
        generate_melody.py "happy birthday celebration" --temp 0.9
    """
    typer.echo(f"🎵 Generating melody for: '{description}'")
    typer.echo()
    
    # Generate melody data
    try:
        melody_data = generate_melody_core(description, temperature)
        typer.echo(f"✓ Melody generated!")
        typer.echo(f"  Tempo: {melody_data.get('tempo')} BPM")
        typer.echo(f"  Key: {melody_data.get('key')} {melody_data.get('scale')}")
        typer.echo(f"  Notes: {len(melody_data.get('notes', []))} notes")
        typer.echo()
    except Exception as e:
        typer.echo(f"Error generating melody: {e}", err=True)
        raise typer.Exit(1)
    
    # Determine output path
    if output:
        output_path = Path(output)
    else:
        # Auto-generate filename from description
        filename = description.replace(" ", "_").lower()[:30] + ".mid"
        output_path = Path("output/midi") / filename
    
    # Create MIDI file
    try:
        create_midi_from_json(melody_data, output_path)
        typer.echo(f"✓ MIDI file saved to: {output_path}")
    except Exception as e:
        typer.echo(f"Error creating MIDI file: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo()
    typer.echo("✓ Done!")


if __name__ == "__main__":
    app()

