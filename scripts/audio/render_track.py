"""
Render individual tracks/channels from MIDI with specific instruments.
"""

from pathlib import Path
from typing import Optional
import mido
import typer

from scripts.audio.render_midi import render_midi_to_wav
from scripts.audio.instrument_mapper import apply_instrument_mapping, get_instrument_name
from scripts.audio.audio_config import DEFAULT_SAMPLE_RATE, OUTPUT_AUDIO_DIR

app = typer.Typer()


def extract_channel(
    midi_path: Path,
    channel: int,
    output_path: Path,
) -> None:
    """
    Extract a single channel from a multi-track MIDI file.
    
    Args:
        midi_path: Input MIDI file
        channel: Channel number to extract (0-15)
        output_path: Output MIDI file with only the specified channel
    """
    midi = mido.MidiFile(str(midi_path))
    new_midi = mido.MidiFile(ticks_per_beat=midi.ticks_per_beat)
    
    for track in midi.tracks:
        new_track = mido.MidiTrack()
        
        # Copy meta messages and messages for the target channel
        for msg in track:
            if msg.is_meta:
                new_track.append(msg.copy())
            elif hasattr(msg, 'channel') and msg.channel == channel:
                new_track.append(msg.copy())
        
        # Only add track if it has content
        if len(new_track) > 0:
            new_midi.tracks.append(new_track)
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    new_midi.save(str(output_path))


def render_single_track(
    midi_path: Path,
    channel: int,
    output_path: Path,
    instrument: Optional[int] = None,
    soundfont_path: Optional[Path] = None,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
) -> None:
    """
    Render a single channel/track from a MIDI file with a specific instrument.
    
    Args:
        midi_path: Input MIDI file
        channel: Channel number to render (0-15)
        output_path: Output WAV file
        instrument: GM instrument number (0-127). If None, uses channel default.
        soundfont_path: Path to soundfont. If None, uses default.
        sample_rate: Audio sample rate in Hz
    """
    # Create temp directory for intermediate files
    temp_dir = output_path.parent / ".temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract the channel
    channel_midi = temp_dir / f"channel_{channel}.mid"
    extract_channel(midi_path, channel, channel_midi)
    
    # Apply instrument mapping if specified
    if instrument is not None:
        mapped_midi = temp_dir / f"channel_{channel}_mapped.mid"
        channel_map = {channel: instrument}
        apply_instrument_mapping(channel_midi, mapped_midi, channel_map)
        render_input = mapped_midi
    else:
        render_input = channel_midi
    
    # Render to audio
    render_midi_to_wav(render_input, output_path, soundfont_path, sample_rate)
    
    # Clean up temp files
    import shutil
    shutil.rmtree(temp_dir)


@app.command()
def render(
    midi_file: str = typer.Argument(..., help="Path to MIDI file"),
    channel: int = typer.Argument(..., help="Channel number to render (0-15)"),
    output: str = typer.Option(None, "--output", "-o", help="Output WAV file path"),
    instrument: int = typer.Option(None, "--instrument", "-i", help="GM instrument number (0-127)"),
    soundfont: str = typer.Option(None, "--soundfont", "-s", help="Path to soundfont file"),
    sample_rate: int = typer.Option(DEFAULT_SAMPLE_RATE, "--rate", "-r", help="Sample rate (Hz)"),
):
    """
    Render a single channel/track from a multi-track MIDI file.
    
    This extracts one channel and renders it with a specific instrument,
    useful for isolating individual parts (melody, drums, harmony, etc.).
    
    Examples:
        # Render channel 0 (melody) as piano
        render_track.py song.mid 0 -i 0
        
        # Render channel 1 (harmony) as guitar
        render_track.py song.mid 1 -i 24 -o harmony.wav
        
        # Render channel 9 (drums)
        render_track.py song.mid 9
    """
    midi_path = Path(midi_file)
    
    if not midi_path.exists():
        typer.echo(f"Error: MIDI file not found: {midi_file}", err=True)
        raise typer.Exit(1)
    
    if channel < 0 or channel > 15:
        typer.echo(f"Error: Channel must be between 0 and 15", err=True)
        raise typer.Exit(1)
    
    if instrument is not None and (instrument < 0 or instrument > 127):
        typer.echo(f"Error: Instrument must be between 0 and 127", err=True)
        raise typer.Exit(1)
    
    # Determine output path
    if output:
        output_path = Path(output)
    else:
        OUTPUT_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_AUDIO_DIR / f"{midi_path.stem}_channel{channel}.wav"
    
    soundfont_path = Path(soundfont) if soundfont else None
    
    typer.echo(f"🎵 Rendering Track (Channel {channel})")
    typer.echo(f"   Input: {midi_path}")
    typer.echo(f"   Channel: {channel}")
    if instrument is not None:
        typer.echo(f"   Instrument: {instrument} ({get_instrument_name(instrument)})")
    typer.echo(f"   Output: {output_path}")
    typer.echo()
    
    try:
        render_single_track(
            midi_path, channel, output_path,
            instrument, soundfont_path, sample_rate
        )
        typer.echo(f"✓ Rendered successfully!")
        typer.echo(f"  Output saved to: {output_path}")
    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

