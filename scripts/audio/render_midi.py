"""
Basic MIDI to WAV rendering using FluidSynth.
"""

import subprocess
from pathlib import Path
from typing import Optional, List
import typer
import mido

from scripts.audio.audio_config import (
    get_default_soundfont,
    DEFAULT_SAMPLE_RATE,
    OUTPUT_AUDIO_DIR,
    QUALITY_PRESETS,
)
from scripts.audio.instrument_mapper import apply_instrument_mapping

app = typer.Typer()


def render_midi_to_wav(
    midi_path: Path,
    output_path: Path,
    soundfont_path: Optional[Path] = None,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    gain: float = 1.0,
) -> None:
    """
    Render a MIDI file to WAV using FluidSynth.
    
    Args:
        midi_path: Path to input MIDI file
        output_path: Path to output WAV file
        soundfont_path: Path to soundfont (.sf2/.sf3). If None, uses default.
        sample_rate: Audio sample rate in Hz (default: 44100)
        gain: Audio gain/volume multiplier (default: 1.0)
    
    Raises:
        FileNotFoundError: If MIDI file or soundfont not found
        RuntimeError: If FluidSynth rendering fails
    """
    # Validate input
    if not midi_path.exists():
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")
    
    # Get soundfont
    if soundfont_path is None:
        soundfont_path = get_default_soundfont()
    elif not soundfont_path.exists():
        raise FileNotFoundError(f"Soundfont not found: {soundfont_path}")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Apply instrument mapping to a temp file
    temp_midi = output_path.parent / f".temp_{midi_path.name}"
    apply_instrument_mapping(midi_path, temp_midi)
    
    # Debug: show what instruments were applied
    from scripts.audio.instrument_mapper import get_channel_instruments, get_instrument_name
    channel_map = get_channel_instruments(midi_path)
    print(f"DEBUG: Applied instruments:")
    for ch, inst in sorted(channel_map.items()):
        print(f"  Channel {ch}: {get_instrument_name(inst)}")
    
    # Build FluidSynth command
    # Options must come BEFORE soundfont/MIDI files
    # -ni: no interactive mode
    # -F: output to file
    # -r: sample rate
    # -g: gain
    command = [
        "fluidsynth",
        "-ni",                          # No interactive shell
        "-F", str(output_path),         # WAV output
        "-r", str(sample_rate),         # Sample rate
        "-g", str(gain),                # Gain/volume
        str(soundfont_path),            # Soundfont file
        str(temp_midi),                 # MIDI input (with instruments)
    ]
    
    # Run FluidSynth
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        # Clean up temp file before raising
        if temp_midi.exists():
            temp_midi.unlink()
        raise RuntimeError(
            f"FluidSynth rendering failed:\n{e.stderr}"
        )
    except FileNotFoundError:
        # Clean up temp file before raising
        if temp_midi.exists():
            temp_midi.unlink()
        raise RuntimeError(
            "FluidSynth not found. Please install it:\n"
            "  macOS: brew install fluidsynth\n"
            "  Linux: sudo apt-get install fluidsynth\n"
            "See AUDIO_SETUP.md for details."
        )
    finally:
        # Clean up temp MIDI file
        if temp_midi.exists():
            temp_midi.unlink()


def filter_midi_channels(
    midi_path: Path,
    output_path: Path,
    exclude_channels: List[int]
) -> None:
    """
    Create a new MIDI file with specific channels removed.
    
    Args:
        midi_path: Input MIDI file
        output_path: Output MIDI file
        exclude_channels: List of channel numbers to remove (0-15)
    """
    midi = mido.MidiFile(str(midi_path))
    new_midi = mido.MidiFile(ticks_per_beat=midi.ticks_per_beat)
    
    for track in midi.tracks:
        new_track = mido.MidiTrack()
        for msg in track:
            # Keep all meta messages
            if msg.is_meta:
                new_track.append(msg.copy())
            # Keep messages not on excluded channels
            elif not hasattr(msg, 'channel') or msg.channel not in exclude_channels:
                new_track.append(msg.copy())
        new_midi.tracks.append(new_track)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    new_midi.save(str(output_path))


def render_complete_song_wav(
    midi_path: Path,
    output_path: Path,
    soundfont_path: Optional[Path] = None,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    gain: float = 1.0,
) -> Path:
    """
    Render complete multi-track MIDI to WAV with all instruments.
    
    This renders the full arrangement including:
    - Channel 0: Melody/Piano
    - Channel 1: Harmony/Guitar
    - Channel 2: Vocals (choir/synth)
    - Channel 9: Drums
    
    Args:
        midi_path: Path to complete MIDI file (e.g., {song}_complete.mid)
        output_path: Where to save the WAV file
        soundfont_path: Path to soundfont (optional)
        sample_rate: Audio sample rate in Hz
        gain: Audio gain/volume multiplier
    
    Returns:
        Path to generated WAV file
    """
    render_midi_to_wav(midi_path, output_path, soundfont_path, sample_rate, gain)
    return output_path


def render_instrumental_wav(
    midi_path: Path,
    output_path: Path,
    soundfont_path: Optional[Path] = None,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    gain: float = 1.0,
) -> Path:
    """
    Render instrumental-only WAV (excludes vocal track).
    
    This renders the arrangement without vocals:
    - Channel 0: Melody/Piano
    - Channel 1: Harmony/Guitar
    - Channel 9: Drums
    (Channel 2 vocals excluded)
    
    Args:
        midi_path: Path to complete MIDI file (e.g., {song}_complete.mid)
        output_path: Where to save the WAV file
        soundfont_path: Path to soundfont (optional)
        sample_rate: Audio sample rate in Hz
        gain: Audio gain/volume multiplier
    
    Returns:
        Path to generated WAV file
    """
    # Create temp MIDI without vocals (channel 2)
    temp_midi = output_path.parent / f".temp_instrumental_{midi_path.name}"
    filter_midi_channels(midi_path, temp_midi, exclude_channels=[2])
    
    try:
        # Render the filtered MIDI
        render_midi_to_wav(temp_midi, output_path, soundfont_path, sample_rate, gain)
        return output_path
    finally:
        # Clean up temp file
        if temp_midi.exists():
            temp_midi.unlink()


@app.command()
def render(
    midi_file: str = typer.Argument(..., help="Path to MIDI file"),
    output: str = typer.Option(None, "--output", "-o", help="Output WAV file path"),
    soundfont: str = typer.Option(None, "--soundfont", "-s", help="Path to soundfont file"),
    quality: str = typer.Option(None, "--quality", "-q", help="Quality preset: low, medium, high, ultra"),
    sample_rate: int = typer.Option(None, "--rate", "-r", help="Sample rate (Hz, overrides quality preset)"),
    gain: float = typer.Option(None, "--gain", "-g", help="Audio gain/volume (0.1-2.0, overrides quality preset)"),
):
    """
    Render a MIDI file to WAV audio.
    
    Uses FluidSynth to synthesize the MIDI file with a soundfont.
    
    Examples:
        render_midi.py song.mid
        render_midi.py song.mid -q high
        render_midi.py song.mid -o output.wav --gain 1.5
        render_midi.py song.mid -s mysoundfont.sf2 -r 48000
    """
    midi_path = Path(midi_file)
    
    # Apply quality preset or use defaults
    if quality:
        if quality not in QUALITY_PRESETS:
            typer.echo(f"Error: Invalid quality preset '{quality}'", err=True)
            typer.echo(f"Available presets: {', '.join(QUALITY_PRESETS.keys())}", err=True)
            raise typer.Exit(1)
        
        preset = QUALITY_PRESETS[quality]
        final_sample_rate = preset["sample_rate"]
        final_gain = preset["gain"]
    else:
        final_sample_rate = DEFAULT_SAMPLE_RATE
        final_gain = 1.0
    
    # Override with explicit options if provided
    if sample_rate is not None:
        final_sample_rate = sample_rate
    if gain is not None:
        final_gain = gain
    
    # Determine output path
    if output:
        output_path = Path(output)
    else:
        # Auto-generate output path
        OUTPUT_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_AUDIO_DIR / f"{midi_path.stem}.wav"
    
    # Get soundfont path
    soundfont_path = Path(soundfont) if soundfont else None
    
    typer.echo(f"🎵 Rendering MIDI → WAV")
    typer.echo(f"   Input: {midi_path}")
    typer.echo(f"   Output: {output_path}")
    if soundfont_path:
        typer.echo(f"   Soundfont: {soundfont_path}")
    else:
        try:
            default_sf = get_default_soundfont()
            typer.echo(f"   Soundfont: {default_sf} (auto-detected)")
        except FileNotFoundError as e:
            typer.echo(f"   Error: {e}", err=True)
            raise typer.Exit(1)
    typer.echo(f"   Sample Rate: {final_sample_rate} Hz")
    typer.echo(f"   Gain: {final_gain}x")
    if quality:
        typer.echo(f"   Quality: {quality} ({QUALITY_PRESETS[quality]['description']})")
    typer.echo()
    
    try:
        render_midi_to_wav(midi_path, output_path, soundfont_path, final_sample_rate, final_gain)
        typer.echo(f"✓ Rendered successfully!")
        typer.echo(f"  Output saved to: {output_path}")
    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

