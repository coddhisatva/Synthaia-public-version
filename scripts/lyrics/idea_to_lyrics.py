"""
Generate a complete song from theme to lyrics in one command.

This combines idea generation and lyrics writing into a single workflow.

Usage:
    python scripts/lyrics/full_song.py "summer romance"
    python scripts/lyrics/full_song.py "heartbreak" --genre "indie pop" -o output/songs/heartbreak_full.txt
"""

from pathlib import Path
import typer
from scripts.lyrics.idea_seed_llm import generate_ideas_core
from scripts.lyrics.generate_song_lyrics import generate_lyrics_core

app = typer.Typer()


@app.command()
def generate(
    theme: str = typer.Argument(..., help="The theme or concept for the song"),
    genre: str = typer.Option(None, "--genre", "-g", help="Musical genre (e.g., 'indie rock', 'pop', 'hip-hop')"),
    mood: str = typer.Option(None, "--mood", "-m", help="Emotional mood (e.g., 'melancholic', 'upbeat', 'intimate')"),
    temperature: float = typer.Option(0.8, "--temp", "-t", help="Creativity level (0.0-1.0)"),
    output: str = typer.Option(None, "--output", "-o", help="Save to file instead of printing"),
    save_idea: bool = typer.Option(False, "--save-idea", help="Also save the generated idea to output/ideas/"),
):
    """
    Generate a complete song from theme to final lyrics in one command.
    
    This command:
    1. Generates a song idea/concept from your theme
    2. Immediately writes full lyrics based on that idea
    
    Examples:
        full_song.py "summer romance"
        full_song.py "heartbreak" --genre "indie pop" -o output/songs/heartbreak.txt
        full_song.py "nostalgia" --save-idea -o output/songs/nostalgia.txt
    """
    typer.echo(f"🎵 Starting full song generation for theme: '{theme}'")
    typer.echo()
    
    # Step 1: Generate idea
    typer.echo("Step 1/2: Generating song idea...")
    try:
        idea = generate_ideas_core(theme, count=1, temperature=temperature)
        typer.echo("✓ Idea generated!")
        typer.echo()
        
        # Optionally save the idea
        if save_idea:
            idea_filename = theme.replace(" ", "_").lower()
            idea_path = Path("output/ideas") / f"{idea_filename}.txt"
            idea_path.parent.mkdir(parents=True, exist_ok=True)
            idea_path.write_text(idea, encoding='utf-8')
            typer.echo(f"  Saved idea to: {idea_path}")
            typer.echo()
        
    except Exception as e:
        typer.echo(f"Error generating idea: {e}", err=True)
        raise typer.Exit(1)
    
    # Step 2: Generate lyrics from idea
    typer.echo("Step 2/2: Writing song lyrics...")
    try:
        lyrics = generate_lyrics_core(
            concept=idea,
            genre=genre,
            mood=mood,
            temperature=temperature,
        )
        typer.echo("✓ Lyrics generated!")
        typer.echo()
        
    except Exception as e:
        typer.echo(f"Error generating lyrics: {e}", err=True)
        raise typer.Exit(1)
    
    # Output results
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Combine idea and lyrics in output file
        full_content = f"# Song Concept\n\n{idea}\n\n{'='*60}\n\n# Lyrics\n\n{lyrics}"
        output_path.write_text(full_content, encoding='utf-8')
        
        typer.echo(f"✓ Saved complete song to: {output}")
    else:
        # Print to console
        typer.echo("="*60)
        typer.echo("SONG CONCEPT:")
        typer.echo("="*60)
        typer.echo(idea)
        typer.echo()
        typer.echo("="*60)
        typer.echo("LYRICS:")
        typer.echo("="*60)
        typer.echo(lyrics)
        typer.echo("="*60)
    
    typer.echo()
    typer.echo("✓ Complete song generated!")


if __name__ == "__main__":
    app()

