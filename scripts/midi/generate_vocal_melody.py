"""
Generate a vocal melody that complements instrumental tracks and lyrics.

Usage:
    python scripts/midi/generate_vocal_melody.py melody.mid continuation.mid harmony.mid --lyrics song.txt
    python scripts/midi/generate_vocal_melody.py part1.mid part2.mid harmony.mid -l lyrics.txt -o vocal.mid
"""

import json
import os
from pathlib import Path
import typer
from scripts.utils.llm_client import call_llm
from scripts.utils.midi_utils import load_prompt, extract_melody_data, create_midi_from_json
from scripts.utils.musicxml_utils import create_musicxml_with_lyrics
from scripts.utils import cfg

app = typer.Typer()


def extract_first_verse(lyrics_text: str) -> str:
    """
    Extract the first verse from full lyrics.
    
    Stops at [Chorus] or [Verse 2] tags, or after 4 lines.
    Filters out structural markers like (Verse 1), [Verse 1], etc.
    
    Verses should be exactly 4 lines per the lyrics generator prompt,
    but we enforce the 4-line limit here as a safety measure.
    
    Args:
        lyrics_text: Full lyrics text
    
    Returns:
        First verse text only (exactly 4 lines for 8-measure arrangement)
    """
    import re
    lines = lyrics_text.split('\n')
    first_verse_lines = []
    
    for line in lines:
        # Stop at section markers (except [Verse 1] or [Verse])
        if any(marker in line for marker in ['[Chorus]', '[Verse 2]', '[Bridge]', '[Outro]']):
            break
        
        # Skip structural markers in parentheses like (Verse 1), (Chorus), etc.
        if re.match(r'^\s*\([A-Za-z\s\d]+\)\s*$', line):
            continue
        
        # Skip empty lines and section headers, but include lyrics
        if line.strip() and not (line.startswith('[') and line.endswith(']')):
            first_verse_lines.append(line)
        
        # Limit to 4 lines (matches 8 measures of space)
        if len(first_verse_lines) >= 4:
            break
    
    return '\n'.join(first_verse_lines)


def map_words_to_notes(lyrics_text: str, vocal_notes: list) -> list:
    """
    Map lyrics words to MIDI notes.
    
    Simple algorithm:
    - Split lyrics into words
    - Distribute notes across words based on duration
    - Group consecutive same-pitch notes together for one word
    
    Args:
        lyrics_text: Verse lyrics (already filtered, no structural markers)
        vocal_notes: List of note dicts with 'pitch' and 'duration'
    
    Returns:
        List of tuples (word, pitch, start_time, duration)
    """
    # Note: Structural markers already filtered out in extract_first_verse()
    words = lyrics_text.replace('\n', ' ').split()
    words = [w.strip() for w in words if w.strip()]
    
    print(f"📝 Mapping lyrics to notes...")
    print(f"   Words: {len(words)} ({', '.join(words)})")
    print(f"   Notes: {len(vocal_notes)}")
    
    if not words or not vocal_notes:
        print(f"   ⚠️  Empty words or notes, skipping mapping")
        return []
    
    # Calculate cumulative times
    current_time = 0
    notes_with_time = []
    for note in vocal_notes:
        notes_with_time.append({
            'pitch': note['pitch'],
            'duration': note['duration'],
            'start_time': current_time
        })
        current_time += note['duration']
    
    # Simple mapping: distribute notes evenly across words
    result = []
    notes_per_word = max(1, len(notes_with_time) // len(words))
    
    print(f"   Notes per word: ~{notes_per_word}")
    
    for i, word in enumerate(words):
        start_idx = i * notes_per_word
        end_idx = start_idx + notes_per_word if i < len(words) - 1 else len(notes_with_time)
        
        if start_idx >= len(notes_with_time):
            break
        
        word_notes = notes_with_time[start_idx:end_idx]
        if not word_notes:
            continue
        
        # Use the longest note's pitch (most prominent)
        longest_note = max(word_notes, key=lambda n: n['duration'])
        pitch = longest_note['pitch']
        start_time = word_notes[0]['start_time']
        duration = sum(n['duration'] for n in word_notes)
        
        result.append((word, pitch, start_time, duration))
        print(f"   '{word}' → pitch {pitch} (MIDI), {start_time:.2f}s, {duration:.2f}s")
    
    print(f"   ✅ Mapped {len(result)} words to notes")
    return result


def generate_vocal_audio(
    vocal_data: dict,
    word_mapping: list,
    audio_output_path: Path,
    voice: str = None
) -> Path:
    """
    Generate singing WAV audio using PySinsy.
    
    Creates MusicXML from vocal MIDI + lyrics, then uses PySinsy
    to synthesize singing audio.
    
    Args:
        vocal_data: Dict with 'tempo', 'key', 'notes' from LLM
        word_mapping: List of (word, pitch, start_time, duration) tuples
        audio_output_path: Where to save the singing WAV file
        voice: Not used for PySinsy (kept for API compatibility)
    
    Returns:
        Path to generated WAV file
    """
    import pysinsy
    
    print(f"[GENERATE_VOCAL_AUDIO] Starting with PySinsy")
    print(f"[GENERATE_VOCAL_AUDIO] Words mapped: {len(word_mapping)}")
    print(f"[GENERATE_VOCAL_AUDIO] Tempo: {vocal_data['tempo']} BPM")
    print(f"[GENERATE_VOCAL_AUDIO] Output: {audio_output_path}")
    
    # Ensure vocal_data has key/scale for MusicXML
    if 'key' not in vocal_data:
        vocal_data['key'] = 'C'
    if 'scale' not in vocal_data:
        vocal_data['scale'] = 'major'
    
    # Step 1: Create MusicXML with embedded lyrics
    musicxml_path = audio_output_path.with_suffix('.musicxml')
    print(f"[GENERATE_VOCAL_AUDIO] Step 1: Creating MusicXML...")
    create_musicxml_with_lyrics(vocal_data, word_mapping, musicxml_path)
    
    # Step 2: Generate singing with PySinsy
    print(f"[GENERATE_VOCAL_AUDIO] Step 2: Synthesizing vocals with PySinsy...")
    
    try:
        # Initialize PySinsy
        sinsy = pysinsy.Sinsy()
        
        # Set language to English
        default_dic = pysinsy.get_default_dic_dir()
        print(f"[GENERATE_VOCAL_AUDIO] Dictionary directory: {default_dic}")
        
        if not sinsy.setLanguages("english", default_dic):
            raise Exception("Failed to set English language in PySinsy")
        
        # Load the MusicXML score
        if not sinsy.loadScoreFromMusicXML(str(musicxml_path)):
            raise Exception(f"Failed to load MusicXML file: {musicxml_path}")
        
        # Synthesize and save WAV
        sinsy.synthesize()
        
        # Ensure output directory exists
        audio_output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the synthesized audio
        if not sinsy.saveSynthesizedWav(str(audio_output_path)):
            raise Exception(f"Failed to save WAV file: {audio_output_path}")
        
        # Clear the score for next use
        sinsy.clearScore()
        
        print(f"[GENERATE_VOCAL_AUDIO] Complete: {audio_output_path}")
        return audio_output_path
        
    except Exception as e:
        print(f"[GENERATE_VOCAL_AUDIO] Error: {e}")
        raise


def generate_vocal_melody_core(
    melody_path: Path,
    continuation_path: Path,
    harmony_path: Path,
    lyrics_text: str,
    temperature: float = 0.8,
    generate_audio: bool = False,  # Disabled: no working English singing synthesis
    audio_output_path: Path = None,
) -> dict:
    """
    Core logic to generate vocal melody (MIDI + optional WAV audio).
    
    Args:
        melody_path: Path to original melody MIDI
        continuation_path: Path to continuation MIDI
        harmony_path: Path to harmony/counter-melody MIDI
        lyrics_text: Lyrics text (will extract first verse)
        temperature: Creativity level (0.0-1.0)
        generate_audio: Whether to generate WAV audio with TTS (default: True)
        audio_output_path: Where to save WAV file (default: same dir as MIDI)
    
    Returns:
        Dictionary with vocal melody data (includes 'audio_path' if generated)
    """
    # Extract data from all 3 instrumental tracks
    melody_data = extract_melody_data(melody_path)
    continuation_data = extract_melody_data(continuation_path)
    harmony_data = extract_melody_data(harmony_path)
    
    # Get first verse only
    first_verse = extract_first_verse(lyrics_text)
    
    # Calculate total instrumental context
    total_melody_notes = len(melody_data["notes"]) + len(continuation_data["notes"])
    total_harmony_notes = len(harmony_data["notes"])
    
    # Build prompt
    system_prompt = load_prompt("vocals")
    
    user_prompt = f"""Generate a vocal melody for this arrangement:

Instrumental context:
- Tempo: {melody_data['tempo']} BPM
- Length: 8 measures (32 beats total in 4/4 time)
- Main melody: {total_melody_notes} notes (piano/lead)
- Counter-melody: {total_harmony_notes} notes (guitar/synth, lower octave)

First verse lyrics:
{first_verse}

CRITICAL REQUIREMENT - LENGTH:
The vocal melody MUST be the same length as the instrumental tracks.
- Approximately 8 measures
- Approximately 32 beats total (in 4/4 time)
- Start at beat 0, end at beat 32
- This is NOT negotiable - the instrumental music is 8 measures and vocals must match

RHYTHM & VARIETY:
- Use varied note durations: mix 0.25, 0.5, 1.0, 2.0 beats
- Natural phrasing that matches lyrical rhythm

Other requirements:
- Match tempo: {melody_data['tempo']} BPM
- Singable range (C3-C5 / MIDI 48-72)
- Natural phrasing that works with the lyrics (fit them into the 32 beats)
- Complement the instrumental tracks
- Create a memorable, singable melody

If the lyrics are too long for 8 measures, sing faster or use melismas. The 32-beat length is fixed.

OUTPUT INSTRUCTIONS: Return ONLY valid JSON. No comments, no // annotations, no explanations. Pure JSON only."""
    
    # Retry logic for flaky LLM responses
    max_retries = 3
    import time
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"⚠️  Retry attempt {attempt + 1}/{max_retries}...")
                time.sleep(1)  # Brief pause between retries
            
            response = call_llm(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=15000,  # Needs room for analysis + generation
            )
            
            # Check for empty response
            if not response or len(response.strip()) == 0:
                raise ValueError("Empty response from LLM")
            
            # Clean up response
            response = response.strip()
            if response.startswith("```"):
                lines = response.split('\n')
                response = '\n'.join(lines[1:-1])
            
            # Remove // comments from JSON (LLMs love to add these)
            import re
            response = re.sub(r'//.*$', '', response, flags=re.MULTILINE)
            
            vocal_data = json.loads(response)
            
            # Ensure tempo matches
            vocal_data["tempo"] = melody_data["tempo"]
            
            print(f"✓ Successfully generated vocals on attempt {attempt + 1}")
            
            # Always create word mapping (needed for MIDI lyrics embedding)
            word_mapping = map_words_to_notes(first_verse, vocal_data["notes"])
            vocal_data["word_mapping"] = word_mapping  # Include in result
            
            # Generate Synthesizer V singing audio if requested (only after successful MIDI generation)
            if generate_audio:
                try:
                    # Determine audio output path
                    if audio_output_path is None:
                        audio_output_path = melody_path.parent.parent / "audio" / f"{melody_path.stem}_vocals.wav"
                    
                    # Generate singing WAV file using Synthesizer V + REAPER
                    generate_vocal_audio(vocal_data, word_mapping, audio_output_path)
                    vocal_data["audio_path"] = str(audio_output_path)
                    
                    print(f"✓ Generated vocal audio: {audio_output_path}")
                except Exception as e:
                    print(f"⚠ Failed to generate vocal audio: {e}")
                    print("  Continuing with MIDI only...")
                    vocal_data["audio_path"] = None
            
            return vocal_data
            
        except (json.JSONDecodeError, ValueError) as e:
            if attempt == max_retries - 1:
                # Last attempt failed, raise error
                raise ValueError(f"LLM did not return valid JSON after {max_retries} attempts: {e}\nLast response: {response}")
            # Otherwise continue to next retry
            print(f"⚠️  Attempt {attempt + 1} failed: {e}")


@app.command()
def generate(
    melody: str = typer.Argument(..., help="Original melody MIDI file"),
    continuation: str = typer.Argument(..., help="Continuation MIDI file"),
    harmony: str = typer.Argument(..., help="Harmony/counter-melody MIDI file"),
    lyrics: str = typer.Option(..., "--lyrics", "-l", help="Path to lyrics file"),
    temperature: float = typer.Option(0.8, "--temp", "-t", help="Creativity level (0.0-1.0)"),
    output: str = typer.Option(None, "--output", "-o", help="Output MIDI file path"),
):
    """
    Generate a vocal melody that complements your instrumental tracks and lyrics.
    
    Reads 3 instrumental MIDI files and lyrics, then generates a singable
    vocal melody for the first verse that works with the arrangement.
    
    Examples:
        generate_vocal_melody.py melody.mid continuation.mid harmony.mid --lyrics song.txt
        generate_vocal_melody.py part1.mid part2.mid harmony.mid -l lyrics.txt -o vocal.mid
        generate_vocal_melody.py original.mid next.mid counter.mid -l song.txt --temp 0.9
    """
    melody_path = Path(melody)
    continuation_path = Path(continuation)
    harmony_path = Path(harmony)
    lyrics_path = Path(lyrics)
    
    # Validate inputs
    if not melody_path.exists():
        typer.echo(f"Error: Melody file not found: {melody}", err=True)
        raise typer.Exit(1)
    if not continuation_path.exists():
        typer.echo(f"Error: Continuation file not found: {continuation}", err=True)
        raise typer.Exit(1)
    if not harmony_path.exists():
        typer.echo(f"Error: Harmony file not found: {harmony}", err=True)
        raise typer.Exit(1)
    if not lyrics_path.exists():
        typer.echo(f"Error: Lyrics file not found: {lyrics}", err=True)
        raise typer.Exit(1)
    
    # Read lyrics
    lyrics_text = lyrics_path.read_text()
    
    typer.echo(f"🎤 Generating vocal melody...")
    typer.echo(f"   Melody: {melody}")
    typer.echo(f"   Continuation: {continuation}")
    typer.echo(f"   Harmony: {harmony}")
    typer.echo(f"   Lyrics: {lyrics}")
    typer.echo()
    
    # Generate vocal melody
    try:
        vocal_data = generate_vocal_melody_core(
            melody_path,
            continuation_path,
            harmony_path,
            lyrics_text,
            temperature
        )
        typer.echo(f"✓ Vocal melody generated!")
        typer.echo(f"  Tempo: {vocal_data.get('tempo')} BPM")
        typer.echo(f"  Key: {vocal_data.get('key')} {vocal_data.get('scale')}")
        typer.echo(f"  Notes: {len(vocal_data.get('notes', []))} notes")
        if vocal_data.get('audio_path'):
            typer.echo(f"  Audio: {vocal_data.get('audio_path')}")
        typer.echo()
    except Exception as e:
        typer.echo(f"Error generating vocal melody: {e}", err=True)
        raise typer.Exit(1)
    
    # Determine output path
    if output:
        output_path = Path(output)
    else:
        # Auto-generate filename
        output_path = melody_path.parent / f"{melody_path.stem}_vocals.mid"
    
    # Create MIDI file with embedded lyrics
    try:
        # Get word mapping from vocal_data (already computed by core function)
        word_mapping = vocal_data.get("word_mapping", [])
        
        # Create MIDI with embedded lyrics
        create_midi_from_json(vocal_data, output_path, word_mapping=word_mapping)
        typer.echo(f"✓ Vocal MIDI saved to: {output_path}")
        if word_mapping:
            typer.echo(f"  Embedded {len(word_mapping)} lyric events")
    except Exception as e:
        typer.echo(f"Error creating MIDI file: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo()
    if vocal_data.get('audio_path'):
        typer.echo("✓ Done! Generated:")
        typer.echo(f"   - MIDI: {output_path}")
        typer.echo(f"   - Audio (PySinsy): {vocal_data.get('audio_path')}")
        typer.echo()
        typer.echo("The audio uses PySinsy singing synthesis.")
    else:
        typer.echo("✓ Done! Next steps:")
        typer.echo("   1. Import vocal MIDI into your DAW")
        typer.echo("   2. Use AI vocal tools (Synthesizer V, Suno, etc.)")
        typer.echo("   3. Feed them the vocal MIDI + lyrics for actual singing")


if __name__ == "__main__":
    app()

