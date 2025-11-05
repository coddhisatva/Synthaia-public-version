"""
Arrange multiple MIDI files into a single multi-track composition.

Combines melody, continuation, harmony, drums, and vocals with proper timing.

Usage:
    python scripts/midi/arrange_song.py --melody melody.mid --continuation cont.mid
"""

import typer
from pathlib import Path
from mido import MidiFile, MidiTrack, Message, MetaMessage

app = typer.Typer()


def load_midi_file(file_path: str) -> MidiFile:
    """
    Load a MIDI file from disk.
    
    Args:
        file_path: Path to the MIDI file
    
    Returns:
        MidiFile object
    
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"MIDI file not found: {file_path}")
    
    return MidiFile(str(path))


def combine_sequential(midi1: MidiFile, midi2: MidiFile, measures_per_section: int = 2) -> MidiFile:
    """
    Combine two MIDI files sequentially (one after another).
    
    Args:
        midi1: First MIDI file
        midi2: Second MIDI file
        measures_per_section: How many measures midi1 should occupy (default: 2)
    
    Returns:
        New MidiFile with midi2 starting after midi1's allocated time
    """
    # Create new MIDI file with same properties as first
    combined = MidiFile(ticks_per_beat=midi1.ticks_per_beat)
    
    # Copy all tracks from first MIDI
    for track in midi1.tracks:
        new_track = MidiTrack()
        for msg in track:
            new_track.append(msg.copy())
        combined.tracks.append(new_track)
    
    # Force each section to be exactly the specified number of measures
    # This preserves gaps and ensures consistent timing
    beats_per_section = measures_per_section * 4  # 4 beats per measure in 4/4 time
    first_length = beats_per_section * midi1.ticks_per_beat
    
    # Add tracks from second MIDI with time offset
    for track in midi2.tracks:
        new_track = MidiTrack()
        
        # Add offset to first message
        first_msg = True
        for msg in track:
            if first_msg and not msg.is_meta:
                # Add the offset to the first non-meta message
                offset_msg = msg.copy()
                offset_msg.time += first_length
                new_track.append(offset_msg)
                first_msg = False
            else:
                new_track.append(msg.copy())
        
        combined.tracks.append(new_track)
    
    return combined


def add_parallel_track(base_midi: MidiFile, new_track_midi: MidiFile, start_offset: int = 0) -> MidiFile:
    """
    Add a track from another MIDI file to play in parallel with the base.
    
    Args:
        base_midi: Base MIDI file to add tracks to
        new_track_midi: MIDI file containing track(s) to add
        start_offset: Time offset in ticks for when the new track should start
    
    Returns:
        Modified base_midi with new track(s) added
    """
    # Add tracks from new_track_midi to base
    for track in new_track_midi.tracks:
        new_track = MidiTrack()
        
        # Add time offset to first message if needed
        first_msg = True
        for msg in track:
            if first_msg and start_offset > 0 and not msg.is_meta:
                offset_msg = msg.copy()
                offset_msg.time += start_offset
                new_track.append(offset_msg)
                first_msg = False
            else:
                new_track.append(msg.copy())
        
        base_midi.tracks.append(new_track)
    
    return base_midi


def calculate_midi_length(midi: MidiFile) -> int:
    """
    Calculate the total length of a MIDI file in ticks.
    
    Args:
        midi: MidiFile to measure
    
    Returns:
        Total length in ticks
    """
    max_length = 0
    for track in midi.tracks:
        track_time = 0
        for msg in track:
            track_time += msg.time
        max_length = max(max_length, track_time)
    
    return max_length


def measures_to_ticks(measures: int, ticks_per_beat: int, beats_per_measure: int = 4) -> int:
    """
    Convert measures to MIDI ticks.
    
    Args:
        measures: Number of measures
        ticks_per_beat: MIDI ticks per beat
        beats_per_measure: Beats per measure (default 4/4 time)
    
    Returns:
        Number of ticks
    """
    return measures * beats_per_measure * ticks_per_beat


def assign_channel_to_track(track: MidiTrack, channel: int) -> MidiTrack:
    """
    Assign all note messages in a track to a specific MIDI channel.
    
    Args:
        track: MidiTrack to modify
        channel: MIDI channel (0-15, where 9 is drums)
    
    Returns:
        Modified track with channel assignments
    """
    new_track = MidiTrack()
    
    for msg in track:
        if msg.type in ('note_on', 'note_off', 'program_change', 'control_change'):
            # Change channel for instrument messages
            new_msg = msg.copy(channel=channel)
            new_track.append(new_msg)
        else:
            # Keep other messages unchanged
            new_track.append(msg.copy())
    
    return new_track


@app.command()
def arrange(
    melody: str = typer.Option(None, "--melody", "-m", help="Melody MIDI file (plays measures 1-2)"),
    continuation: str = typer.Option(None, "--continuation", "-c", help="Continuation MIDI file (plays measures 3-4)"),
    harmony: str = typer.Option(None, "--harmony", "-h", help="Harmony MIDI file (starts at measure 5)"),
    drums: str = typer.Option(None, "--drums", "-d", help="Drums MIDI file (plays throughout)"),
    vocals: str = typer.Option(None, "--vocals", "-v", help="Vocals MIDI file (plays throughout)"),
    output: str = typer.Option("output/midi/arranged_song.mid", "--output", "-o", help="Output file path"),
):
    """
    Arrange multiple MIDI files into a single multi-track composition.
    
    Creates a structured arrangement with proper timing:
    - Measures 1-2: Melody only
    - Measures 3-4: Continuation
    - Measures 5-8: Melody + Continuation loop with Harmony
    - Drums and Vocals: Throughout all measures
    
    Channel assignments:
    - Channel 0: Melody/Piano
    - Channel 1: Harmony/Guitar
    - Channel 2: Vocals
    - Channel 9: Drums (standard)
    
    Examples:
        arrange_song.py -m melody.mid -c cont.mid -d drums.mid -o song.mid
        arrange_song.py --melody m.mid --continuation c.mid --harmony h.mid
        arrange_song.py -m m.mid -c c.mid -h h.mid -d d.mid -v v.mid
    """
    typer.echo("🎼 MIDI Arranger")
    typer.echo()
    
    # Validate required files
    if not melody or not continuation:
        typer.echo("Error: Both --melody and --continuation are required for arrangement", err=True)
        typer.echo("Tip: Use --help to see usage examples", err=True)
        raise typer.Exit(1)
    
    # Track which files were provided
    tracks = []
    tracks.append(f"Melody: {melody} (measures 1-2, channel 0)")
    tracks.append(f"Continuation: {continuation} (measures 3-4, channel 0)")
    
    if harmony:
        tracks.append(f"Harmony: {harmony} (starts measure 5, channel 1)")
    if drums:
        tracks.append(f"Drums: {drums} (throughout, channel 9)")
    if vocals:
        tracks.append(f"Vocals: {vocals} (throughout, channel 2)")
    
    typer.echo("Input tracks:")
    for track in tracks:
        typer.echo(f"  • {track}")
    typer.echo()
    
    # Load MIDI files
    typer.echo("Loading MIDI files...")
    midi_files = {}
    
    try:
        if melody:
            midi_files['melody'] = load_midi_file(melody)
            typer.echo(f"  ✓ Loaded melody ({len(midi_files['melody'].tracks)} track(s))")
        
        if continuation:
            midi_files['continuation'] = load_midi_file(continuation)
            typer.echo(f"  ✓ Loaded continuation ({len(midi_files['continuation'].tracks)} track(s))")
        
        if harmony:
            midi_files['harmony'] = load_midi_file(harmony)
            typer.echo(f"  ✓ Loaded harmony ({len(midi_files['harmony'].tracks)} track(s))")
        
        if drums:
            midi_files['drums'] = load_midi_file(drums)
            typer.echo(f"  ✓ Loaded drums ({len(midi_files['drums'].tracks)} track(s))")
        
        if vocals:
            midi_files['vocals'] = load_midi_file(vocals)
            typer.echo(f"  ✓ Loaded vocals ({len(midi_files['vocals'].tracks)} track(s))")
    
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo()
    
    # Define channel assignments
    # Channel 0 = Melody/Piano
    # Channel 1 = Harmony/Guitar
    # Channel 2 = Vocals
    # Channel 9 = Drums (standard)
    channels = {
        'melody': 0,
        'continuation': 0,  # Same as melody
        'harmony': 1,
        'vocals': 2,
        'drums': 9
    }
    
    typer.echo("Assigning MIDI channels to tracks...")
    for track_name, midi in midi_files.items():
        if track_name in channels:
            channel = channels[track_name]
            # Assign channel to all tracks in this MIDI file
            for i, track in enumerate(midi.tracks):
                midi.tracks[i] = assign_channel_to_track(track, channel)
            typer.echo(f"  • {track_name}: Channel {channel}")
    typer.echo()
    
    # Combine melody and continuation sequentially, then loop
    if 'melody' in midi_files and 'continuation' in midi_files:
        typer.echo("Combining melody and continuation with loop...")
        
        # First pass: melody → continuation
        first_pass = combine_sequential(midi_files['melody'], midi_files['continuation'])
        
        # Second pass: melody → continuation again (loop)
        second_pass = combine_sequential(midi_files['melody'], midi_files['continuation'])
        
        # Combine both passes into full 8-measure loop
        # first_pass is 4 measures, so we need to tell combine_sequential that
        full_loop = combine_sequential(first_pass, second_pass, measures_per_section=4)
        
        # Merge all tracks into one with proper timing
        ticks_per_beat = full_loop.ticks_per_beat
        
        # Collect all events with absolute time
        events = []
        for track in full_loop.tracks:
            abs_time = 0
            for msg in track:
                abs_time += msg.time
                if not msg.is_meta or msg.type == 'set_tempo':
                    events.append({'time': abs_time, 'msg': msg.copy()})
        
        # Sort by time and convert back to delta times
        events.sort(key=lambda e: e['time'])
        
        merged_track = MidiTrack()
        last_time = 0
        for event in events:
            delta = event['time'] - last_time
            event['msg'].time = delta
            merged_track.append(event['msg'])
            last_time = event['time']
        
        merged_track.append(MetaMessage('end_of_track', time=0))
        
        # Create new MIDI with single melody track
        combined_melody = MidiFile(ticks_per_beat=ticks_per_beat)
        combined_melody.tracks.append(merged_track)
        
        midi_files['combined_melody'] = combined_melody
        typer.echo("  ✓ Combined into single looping track (8 measures)")
        typer.echo()
    
    # Add drums in parallel if they exist (starting from the beginning)
    if 'drums' in midi_files and 'combined_melody' in midi_files:
        typer.echo("Adding drums track in parallel...")
        combined_with_drums = add_parallel_track(midi_files['combined_melody'], midi_files['drums'])
        midi_files['combined_melody'] = combined_with_drums
        typer.echo("  ✓ Drums added (starts at measure 1)")
        typer.echo()
    
    # Add harmony with offset (starts at measure 5 when melody loops)
    if 'harmony' in midi_files and 'combined_melody' in midi_files:
        typer.echo("Adding harmony track with timing offset...")
        
        # Harmony comes in at measure 5 (after first loop of melody + continuation)
        ticks_per_beat = midi_files['combined_melody'].ticks_per_beat
        harmony_offset = measures_to_ticks(4, ticks_per_beat)  # Start at measure 5 (after 4 measures)
        
        combined_with_harmony = add_parallel_track(
            midi_files['combined_melody'], 
            midi_files['harmony'],
            start_offset=harmony_offset
        )
        midi_files['combined_melody'] = combined_with_harmony
        typer.echo(f"  ✓ Harmony added (starts at measure 5, offset: {harmony_offset} ticks)")
        typer.echo()
    
    # Add vocals in parallel (plays throughout)
    if 'vocals' in midi_files and 'combined_melody' in midi_files:
        typer.echo("Adding vocals track in parallel...")
        combined_with_vocals = add_parallel_track(midi_files['combined_melody'], midi_files['vocals'])
        midi_files['combined_melody'] = combined_with_vocals
        typer.echo("  ✓ Vocals added (plays throughout)")
        typer.echo()
    
    # Store final arrangement
    if 'combined_melody' in midi_files:
        final_arrangement = midi_files['combined_melody']
    else:
        typer.echo("Error: Could not create arrangement", err=True)
        raise typer.Exit(1)
    
    # Save the arranged MIDI file
    typer.echo("Saving arranged MIDI file...")
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        final_arrangement.save(str(output_path))
        typer.echo(f"  ✓ Saved to: {output_path}")
        typer.echo()
    except Exception as e:
        typer.echo(f"Error saving file: {e}", err=True)
        raise typer.Exit(1)
    
    # Summary
    typer.echo("="*60)
    typer.echo("✓ Arrangement Complete!")
    typer.echo("="*60)
    typer.echo(f"Output file: {output_path}")
    typer.echo(f"Total tracks: {len(final_arrangement.tracks)}")
    typer.echo()
    typer.echo("Next steps:")
    typer.echo("  1. Import into GarageBand or your DAW")
    typer.echo("  2. Assign instruments to each channel")
    typer.echo("  3. Mix and master your song!")


if __name__ == "__main__":
    app()

