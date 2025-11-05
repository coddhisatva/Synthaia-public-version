"""
Generate a complete song from a single theme.

This script chains together all the individual tools:
- Lyrics generation
- MIDI melody generation
- Continuation, harmony, drums, vocals
- Final multi-track arrangement

Usage:
    python scripts/create_full_song.py "this woman is my therapy"
    python scripts/create_full_song.py "summer nights" -o my_song
"""

from pathlib import Path
import typer
from lyrics.idea_to_lyrics import generate_ideas_core, generate_lyrics_core
from midi.generate_melody import generate_melody_core
from midi.continue_melody import continue_melody_core
from midi.harmonize_melody import harmonize_melody_core
from midi.generate_drums import generate_drums_core
from midi.generate_vocal_melody import generate_vocal_melody_core
from utils.midi_utils import create_midi_from_json

app = typer.Typer()


@app.command()
def create(
    theme: str = typer.Argument(..., help="Song theme or concept"),
    output_name: str = typer.Option(None, "--output", "-o", help="Base name for output files (default: auto-generated)"),
):
    """
    Create a complete song from a theme in one command.
    
    Generates:
    - Lyrics
    - Melody + continuation + harmony
    - Drums
    - Vocals
    - Final arranged MIDI
    
    Examples:
        create_full_song.py "this woman is my therapy"
        create_full_song.py "summer nights" -o summer_song
    """
    from utils import cfg
    
    typer.echo("="*60)
    typer.echo("🎼 FULL SONG GENERATOR")
    typer.echo("="*60)
    typer.echo(f"Theme: {theme}")
    typer.echo(f"Using: {cfg.get_active_provider()} ({cfg.get_active_model()})")
    typer.echo()
    
    # Generate base name for files
    if not output_name:
        output_name = theme.lower().replace(" ", "_")[:30]
    
    # Create output directories
    output_dir = Path("output")
    ideas_dir = output_dir / "ideas"
    songs_dir = output_dir / "songs"
    midi_dir = output_dir / "midi"
    
    for d in [ideas_dir, songs_dir, midi_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    typer.echo("Step 1/7: Generating lyrics...")
    try:
        # Generate idea
        idea = generate_ideas_core(theme, count=1)
        
        # Generate lyrics from idea
        lyrics = generate_lyrics_core(idea)
        
        # Save lyrics
        lyrics_path = songs_dir / f"{output_name}.txt"
        lyrics_path.write_text(f"# Song Concept\n\n{idea}\n\n{'='*60}\n\n# Lyrics\n\n{lyrics}", encoding='utf-8')
        
        typer.echo(f"  ✓ Lyrics saved to: {lyrics_path}")
    except Exception as e:
        typer.echo(f"  ✗ Error: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo()
    typer.echo("Step 2/7: Generating melody...")
    try:
        melody_data = generate_melody_core(theme)
        melody_path = midi_dir / f"{output_name}.mid"
        create_midi_from_json(melody_data, melody_path)
        typer.echo(f"  ✓ Melody saved to: {melody_path}")
    except Exception as e:
        typer.echo(f"  ✗ Error: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo()
    typer.echo("Step 3/7: Generating continuation...")
    try:
        continuation_data = continue_melody_core(melody_path)
        continuation_path = midi_dir / f"{output_name}_continuation.mid"
        create_midi_from_json(continuation_data, continuation_path)
        typer.echo(f"  ✓ Continuation saved to: {continuation_path}")
    except Exception as e:
        typer.echo(f"  ✗ Error: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo()
    typer.echo("Step 4/7: Generating harmony...")
    try:
        harmony_data = harmonize_melody_core(melody_path, continuation_path)
        harmony_path = midi_dir / f"{output_name}_harmony.mid"
        create_midi_from_json(harmony_data, harmony_path)
        typer.echo(f"  ✓ Harmony saved to: {harmony_path}")
    except Exception as e:
        typer.echo(f"  ✗ Error: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo()
    typer.echo("Step 5/7: Generating drums...")
    try:
        # Extract tempo from melody
        from utils.midi_utils import extract_melody_data
        melody_info = extract_melody_data(melody_path)
        tempo = melody_info['tempo']
        
        drums_data = generate_drums_core(tempo, "steady beat with emotional fills", measures=8)
        drums_path = midi_dir / f"{output_name}_drums.mid"
        create_midi_from_json(drums_data, drums_path)
        typer.echo(f"  ✓ Drums saved to: {drums_path}")
    except Exception as e:
        typer.echo(f"  ✗ Error: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo()
    typer.echo("Step 6/7: Generating vocals...")
    try:
        vocals_data = generate_vocal_melody_core(melody_path, continuation_path, harmony_path, lyrics)
        vocals_path = midi_dir / f"{output_name}_vocals.mid"
        
        # Get word mapping from vocals_data (already computed by core function)
        word_mapping = vocals_data.get("word_mapping", [])
        
        # Create MIDI with embedded lyrics
        create_midi_from_json(vocals_data, vocals_path, word_mapping=word_mapping)
        typer.echo(f"  ✓ Vocals saved to: {vocals_path}")
        if word_mapping:
            typer.echo(f"    Embedded {len(word_mapping)} lyric events")
    except Exception as e:
        typer.echo(f"  ✗ Error: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo()
    typer.echo("Step 7/7: Arranging final song...")
    try:
        import subprocess
        
        arranged_path = midi_dir / f"{output_name}_complete.mid"
        
        # Call arrange_song.py as subprocess
        result = subprocess.run([
            "python", "scripts/midi/arrange_song.py",
            "-m", str(melody_path),
            "-c", str(continuation_path),
            "-h", str(harmony_path),
            "-d", str(drums_path),
            "-v", str(vocals_path),
            "-o", str(arranged_path)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            typer.echo(f"  ✗ Error: {result.stderr}", err=True)
            raise typer.Exit(1)
        
        typer.echo(f"  ✓ Complete song saved to: {arranged_path}")
    except Exception as e:
        typer.echo(f"  ✗ Error: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo()
    typer.echo("="*60)
    typer.echo("✓ SONG COMPLETE!")
    typer.echo("="*60)
    typer.echo(f"Lyrics: {lyrics_path}")
    typer.echo(f"Complete MIDI: {arranged_path}")
    typer.echo()
    typer.echo("Import the MIDI into GarageBand and start mixing!")


if __name__ == "__main__":
    app()

