"""
MIDI channel to General MIDI instrument mapping.
"""

from pathlib import Path
from typing import Dict, Optional
import mido

from scripts.audio.audio_config import INSTRUMENT_MAP


def get_channel_instruments(midi_path: Path) -> Dict[int, int]:
    """
    Analyze a MIDI file and return which channels are active.
    
    Args:
        midi_path: Path to MIDI file
    
    Returns:
        Dict mapping channel number to recommended GM instrument number
    """
    midi = mido.MidiFile(str(midi_path))
    active_channels = set()
    
    # Find all channels with note events
    for track in midi.tracks:
        for msg in track:
            if msg.type in ('note_on', 'note_off') and hasattr(msg, 'channel'):
                active_channels.add(msg.channel)
    
    # Map active channels to instruments using our default mapping
    channel_map = {}
    for channel in active_channels:
        if channel in INSTRUMENT_MAP:
            channel_map[channel] = INSTRUMENT_MAP[channel]
        else:
            # Default to acoustic piano for unmapped channels
            channel_map[channel] = 0
    
    return channel_map


def create_instrument_config_file(
    channel_map: Dict[int, int],
    output_path: Path,
) -> None:
    """
    Create a FluidSynth config file for instrument assignments.
    
    FluidSynth can read a config file to set instruments per channel.
    
    Args:
        channel_map: Dict mapping channel → GM instrument number
        output_path: Where to save the config file
    """
    lines = []
    
    for channel, instrument in sorted(channel_map.items()):
        # FluidSynth command: prog channel bank program
        # For GM, bank is 0
        lines.append(f"prog {channel} 0 {instrument}\n")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("".join(lines))


def apply_instrument_mapping(
    midi_path: Path,
    output_path: Path,
    channel_map: Optional[Dict[int, int]] = None,
) -> None:
    """
    Create a modified MIDI file with instrument program changes.
    
    This embeds program change messages at the start of each track
    so the instruments are set correctly regardless of soundfont defaults.
    
    Args:
        midi_path: Input MIDI file
        output_path: Output MIDI file with instrument changes
        channel_map: Channel → instrument mapping (uses default if None)
    """
    if channel_map is None:
        channel_map = get_channel_instruments(midi_path)
    
    # Load MIDI
    midi = mido.MidiFile(str(midi_path))
    new_midi = mido.MidiFile(ticks_per_beat=midi.ticks_per_beat)
    
    # Create a new first track with ALL program changes at time 0
    setup_track = mido.MidiTrack()
    for channel in sorted(channel_map.keys()):
        if channel != 9:  # Skip drums
            instrument = channel_map[channel]
            setup_track.append(mido.Message(
                'program_change',
                program=instrument,
                channel=channel,
                time=0
            ))
    new_midi.tracks.append(setup_track)
    
    # Copy all original tracks unchanged
    for track in midi.tracks:
        new_track = mido.MidiTrack()
        for msg in track:
            new_track.append(msg.copy())
        new_midi.tracks.append(new_track)
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    new_midi.save(str(output_path))


def get_instrument_name(program: int) -> str:
    """
    Get the General MIDI instrument name for a program number.
    
    Args:
        program: GM instrument number (0-127)
    
    Returns:
        Instrument name string
    """
    from scripts.audio.audio_config import GM_INSTRUMENTS
    
    if program in GM_INSTRUMENTS:
        return GM_INSTRUMENTS[program]
    
    # Fallback to generic name
    return f"GM Program {program}"

