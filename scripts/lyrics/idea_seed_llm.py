"""
Generate song ideas from a theme using AI.

Usage:
    python scripts/lyrics/idea_seed_llm.py --theme "summer romance"
    python scripts/lyrics/idea_seed_llm.py --theme "urban loneliness" --count 5
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


def generate_ideas_core(theme: str, count: int = 1, temperature: float = 0.8) -> str:
    """
    Core logic to generate song ideas.
    
    Args:
        theme: The theme or concept for song ideas
        count: Number of ideas to generate
        temperature: Creativity level (0.0-1.0)
    
    Returns:
        Generated ideas as a string
    """
    system_prompt = load_prompt("seed")
    user_prompt = f"Generate {count} song ideas based on this theme: {theme}"
    response = call_llm(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=temperature,
    )
    return response


@app.command()
def generate(
    theme: str = typer.Argument(..., help="The theme or concept for song ideas"),
    count: int = typer.Option(1, "--count", "-c", help="Number of ideas to generate (1-10)"),
    temperature: float = typer.Option(0.8, "--temp", "-t", help="Creativity level (0.0-1.0)"),
    output: str = typer.Option(None, "--output", "-o", help="Save to file instead of printing"),
):
    """
    Generate song ideas based on a theme.
    
    Examples:
        idea_seed_llm.py "summer vibes"
        idea_seed_llm.py "heartbreak" --count 5
        idea_seed_llm.py "nostalgia" -o ideas.txt
    """
    # Validate count
    if count < 1 or count > 10:
        typer.echo("Error: count must be between 1 and 10", err=True)
        raise typer.Exit(1)
    
    # Show what we're doing
    typer.echo(f"🎵 Generating {count} song ideas for theme: '{theme}'...")
    typer.echo()
    
    # Call core function
    try:
        response = generate_ideas_core(theme, count, temperature)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    
    # Output results
    if output:
        output_path = Path(output)
        output_path.write_text(response, encoding='utf-8')
        typer.echo(f"✓ Saved to {output}")
    else:
        typer.echo(response)
    
    typer.echo()
    typer.echo("✓ Done!")


if __name__ == "__main__":
    app()

