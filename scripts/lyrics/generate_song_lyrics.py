"""
Generate complete song lyrics from a concept or idea.

Usage:
    python scripts/lyrics/generate_song_lyrics.py "A song about summer romance on the beach"
    python scripts/lyrics/generate_song_lyrics.py "Lost love in a digital age" --genre "indie pop"
    python scripts/lyrics/generate_song_lyrics.py "Concept from idea generator" -o song.txt
"""

from pathlib import Path
import typer
from scripts.utils.llm_client import call_llm

app = typer.Typer()


def load_prompt(prompt_name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "lyrics" / f"{prompt_name}.md"
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    return prompt_path.read_text()


def generate_lyrics_core(
    concept: str,
    genre: str = None,
    mood: str = None,
    temperature: float = 0.8,
    max_tokens: int = 2500,
) -> str:
    """
    Core logic to generate song lyrics.
    
    Args:
        concept: The song concept, idea, or theme
        genre: Optional musical genre
        mood: Optional emotional mood
        temperature: Creativity level (0.0-1.0)
        max_tokens: Maximum tokens in response
    
    Returns:
        Generated lyrics as a string
    """
    system_prompt = load_prompt("song_lyrics")
    user_prompt = f"Write complete song lyrics for this concept:\n\n{concept}"
    
    if genre:
        user_prompt += f"\n\nGenre: {genre}"
    if mood:
        user_prompt += f"\nMood: {mood}"
    
    response = call_llm(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    # Clean up response: strip any commentary before [Verse 1]
    lines = response.split('\n')
    verse_start_idx = None
    for i, line in enumerate(lines):
        if '[Verse 1]' in line or '(Verse 1)' in line:
            verse_start_idx = i
            break
    
    if verse_start_idx is not None:
        # Return from [Verse 1] onwards
        response = '\n'.join(lines[verse_start_idx:])
    
    return response


@app.command()
def generate(
    concept: str = typer.Argument(None, help="The song concept, idea, or theme"),
    input_file: str = typer.Option(None, "--input", "-i", help="Read concept from file (e.g., from idea generator)"),
    genre: str = typer.Option(None, "--genre", "-g", help="Musical genre (e.g., 'indie rock', 'pop', 'hip-hop')"),
    mood: str = typer.Option(None, "--mood", "-m", help="Emotional mood (e.g., 'melancholic', 'upbeat', 'intimate')"),
    temperature: float = typer.Option(0.8, "--temp", "-t", help="Creativity level (0.0-1.0)"),
    output: str = typer.Option(None, "--output", "-o", help="Save to file instead of printing"),
):
    """
    Generate complete song lyrics from a concept or idea.
    
    Takes a song concept (can be from the idea generator) and writes
    full structured lyrics with verses, chorus, and bridge.
    
    Examples:
        generate_song_lyrics.py "A story about leaving home"
        generate_song_lyrics.py --input ideas.txt --genre "indie pop"
        generate_song_lyrics.py "Urban loneliness" -m "melancholic" -o lyrics.txt
    """
    # Get concept from either argument or file
    if input_file and concept:
        typer.echo("Error: Provide either a concept or --input file, not both", err=True)
        raise typer.Exit(1)
    
    if input_file:
        try:
            full_content = Path(input_file).read_text().strip()
            # Extract just the first idea (everything up to the second "###" or end of file)
            lines = full_content.split('\n')
            first_idea_lines = []
            found_first = False
            for line in lines:
                if line.startswith('###'):
                    if found_first:
                        break  # Stop at second idea
                    found_first = True
                first_idea_lines.append(line)
            concept = '\n'.join(first_idea_lines).strip()
        except FileNotFoundError:
            typer.echo(f"Error: File not found: {input_file}", err=True)
            raise typer.Exit(1)
    
    if not concept:
        typer.echo("Error: Provide a concept as argument or use --input to read from file", err=True)
        raise typer.Exit(1)
    
    # Show what we're doing
    typer.echo(f"✍️  Writing song lyrics for: '{concept}'")
    if genre:
        typer.echo(f"   Genre: {genre}")
    if mood:
        typer.echo(f"   Mood: {mood}")
    typer.echo()
    typer.echo("Generating... (this may take a moment)")
    typer.echo()
    
    # Call core function
    try:
        response = generate_lyrics_core(concept, genre, mood, temperature)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    
    # Output results
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(response, encoding='utf-8')
        typer.echo(f"✓ Saved to {output}")
    else:
        # Always print response
        typer.echo("---")
        typer.echo(response)
        typer.echo("---")
    
    typer.echo()
    typer.echo("✓ Done!")


if __name__ == "__main__":
    app()

