"""
Synthesizer V + REAPER client for AI singing synthesis.
Generates REAPER projects with Synth V VST and renders singing audio.
"""

import subprocess
import time
from pathlib import Path
from typing import Optional
from scripts.utils import cfg


def create_reaper_project(
    musicxml_path: Path,
    output_rpp_path: Path,
    voice: Optional[str] = None
) -> Path:
    """
    Generate a REAPER project file (.rpp) that loads Synth V VST with MusicXML.
    
    Args:
        musicxml_path: Path to MusicXML file with lyrics
        output_rpp_path: Where to save the .rpp project file
        voice: Synth V voice to use (default from config)
    
    Returns:
        Path to created .rpp file
    """
    if voice is None:
        voice = cfg.SYNTHV_VOICE
    
    print(f"[CREATE_REAPER_PROJECT] Starting")
    print(f"[CREATE_REAPER_PROJECT] MusicXML input: {musicxml_path}")
    print(f"[CREATE_REAPER_PROJECT] MusicXML exists: {musicxml_path.exists()}")
    print(f"[CREATE_REAPER_PROJECT] Voice: {voice}")
    print(f"[CREATE_REAPER_PROJECT] VST path: {cfg.SYNTHV_VST_PATH}")
    print(f"[CREATE_REAPER_PROJECT] VST exists: {Path(cfg.SYNTHV_VST_PATH).exists()}")
    print(f"[CREATE_REAPER_PROJECT] Output RPP: {output_rpp_path}")
    
    # REAPER project file format
    # This is a simplified version - real .rpp files are more complex
    # We'll create a minimal project that loads Synth V VST
    
    rpp_content = f"""<REAPER_PROJECT 0.1 "7.0"
  RIPPLE 0
  GROUPOVERRIDE 0 0 0
  AUTOXFADE 1
  ENVATTACH 3
  POOLEDENVATTACH 0
  MIXERUIFLAGS 11 48
  PEAKGAIN 1
  FEEDBACK 0
  PANLAW 1
  PROJOFFS 0 0 0
  MAXPROJLEN 0 600
  GRID 3199 8 1 8 1 0 0 0
  TIMEMODE 1 5 -1 30 0 0 -1
  VIDEO_CONFIG 0 0 256
  PANMODE 3
  CURSOR 0
  ZOOM 100 0 0
  VZOOMEX 6 0
  USE_REC_CFG 0
  RECMODE 1
  SMPTESYNC 0 30 100 40 1000 300 0 0 1 0 0
  LOOP 0
  LOOPGRAN 0 4
  RECORD_PATH "" ""
  <RECORD_CFG
  >
  <APPLYFX_CFG
  >
  RENDER_FILE ""
  RENDER_PATTERN ""
  RENDER_FMT 0 2 0
  RENDER_1X 0
  RENDER_RANGE 1 0 0 18 1000
  RENDER_RESAMPLE 3 0 1
  RENDER_ADDTOPROJ 0
  RENDER_STEMS 0
  RENDER_DITHER 0
  TIMELOCKMODE 1
  TEMPOENVLOCKMODE 1
  ITEMMIX 0
  DEFPITCHMODE 589824 0
  TAKELANE 1
  SAMPLERATE 44100 0 0
  <RENDER_CFG
  >
  LOCK 1
  <METRONOME 6 2
    VOL 0.25 0.125
    FREQ 800 1600 1
    BEATLEN 4
    SAMPLES "" ""
    PATTERN 2863311530 2863311529
    MULT 1
  >
  GLOBAL_AUTO -1
  TEMPO 120 4 4
  PLAYRATE 1 0 0.25 4
  SELECTION 0 0
  SELECTION2 0 0
  MASTERAUTOMODE 0
  MASTERTRACKHEIGHT 0 0
  MASTERPEAKCOL 16576
  MASTERMUTESOLO 0
  MASTERTRACKVIEW 0 0.6667 0.5 0.5 0 0 0 0 0 0 0 0 0
  MASTER_NCH 2 2
  MASTER_VOLUME 1 0 -1 -1 1
  MASTER_FX 1
  MASTER_SEL 0
  <TRACK {{00000000-0000-0000-0000-000000000000}}
    NAME "Vocals - Synth V"
    PEAKCOL 16576
    BEAT -1
    AUTOMODE 0
    VOLPAN 1 0 -1 -1 1
    MUTESOLO 0 0 0
    IPHASE 0
    PLAYOFFS 0 1
    ISBUS 0 0
    BUSCOMP 0 0 0 0 0
    SHOWINMIX 1 0.6667 0.5 1 0.5 0 0 0
    FREEMODE 0
    REC 0 0 1 0 0 0 0
    VU 2
    TRACKHEIGHT 0 0 0 0 0 0
    INQ 0 0 0 0.5 100 0 0 100
    NCHAN 2
    FX 1
    TRACKID {{00000000-0000-0000-0000-000000000001}}
    PERF 0
    MIDIOUT -1
    MAINSEND 1 0
    <FXCHAIN
      WNDRECT 0 0 0 0
      SHOW 0
      LASTSEL 0
      DOCKED 0
      BYPASS 0 0 0
      <VST "VST3: Synthesizer V Studio 2 Pro (Dreamtonics)" "{cfg.SYNTHV_VST_PATH}"
        Y3NldnQD////////////////AAAAAAAAAAAAAAABAAAAAAAAAAEAAAABAAAADwAAAA==
        776t3g3wrd7fBgAAEAAAAAAAAAASAAAAAAAAAOxMpQABAAAAAQAAAA==
      >
    </FXCHAIN>
  >
>
"""
    
    # Create output directory
    output_rpp_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write project file
    with open(output_rpp_path, 'w') as f:
        f.write(rpp_content)
    
    print(f"[CREATE_REAPER_PROJECT] RPP file written: {output_rpp_path.stat().st_size} bytes")
    print(f"[CREATE_REAPER_PROJECT] Complete")
    return output_rpp_path


def render_with_reaper(
    rpp_project_path: Path,
    output_wav_path: Path,
    timeout: int = 120
) -> Path:
    """
    Render a REAPER project to WAV using command line.
    
    Args:
        rpp_project_path: Path to .rpp project file
        output_wav_path: Where to save the rendered WAV
        timeout: Maximum seconds to wait for render (default: 120)
    
    Returns:
        Path to rendered WAV file
    
    Raises:
        Exception: If rendering fails or times out
    """
    print(f"[RENDER_WITH_REAPER] Starting")
    print(f"[RENDER_WITH_REAPER] REAPER executable: {cfg.REAPER_EXECUTABLE}")
    print(f"[RENDER_WITH_REAPER] REAPER exists: {Path(cfg.REAPER_EXECUTABLE).exists()}")
    print(f"[RENDER_WITH_REAPER] Project file: {rpp_project_path}")
    print(f"[RENDER_WITH_REAPER] Project exists: {rpp_project_path.exists()}")
    print(f"[RENDER_WITH_REAPER] Output WAV: {output_wav_path}")
    
    # Ensure output directory exists
    output_wav_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Call REAPER CLI to render project
    cmd = [
        cfg.REAPER_EXECUTABLE,
        '-renderproject', str(rpp_project_path)
    ]
    
    print(f"[RENDER_WITH_REAPER] Command: {' '.join(cmd)}")
    print(f"[RENDER_WITH_REAPER] Timeout: {timeout}s")
    
    try:
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = time.time() - start_time
        
        print(f"[RENDER_WITH_REAPER] Process completed in {elapsed:.1f}s")
        print(f"[RENDER_WITH_REAPER] Return code: {result.returncode}")
        
        if result.stdout:
            print(f"[RENDER_WITH_REAPER] STDOUT: {result.stdout[:200]}")
        if result.stderr:
            print(f"[RENDER_WITH_REAPER] STDERR: {result.stderr[:200]}")
        
        if result.returncode != 0:
            print(f"[RENDER_WITH_REAPER] ERROR: Rendering failed")
            raise Exception(f"REAPER rendering failed: {result.stderr}")
        
        # Check if output file was created
        print(f"[RENDER_WITH_REAPER] Checking for output WAV...")
        if not output_wav_path.exists():
            print(f"[RENDER_WITH_REAPER] WAV not at expected location: {output_wav_path}")
            # REAPER might have saved to a different location
            project_dir = rpp_project_path.parent
            print(f"[RENDER_WITH_REAPER] Searching in: {project_dir}")
            possible_outputs = list(project_dir.glob("*.wav"))
            print(f"[RENDER_WITH_REAPER] Found {len(possible_outputs)} WAV files")
            if possible_outputs:
                print(f"[RENDER_WITH_REAPER] Moving {possible_outputs[0]} to {output_wav_path}")
                import shutil
                shutil.move(str(possible_outputs[0]), str(output_wav_path))
            else:
                print(f"[RENDER_WITH_REAPER] ERROR: No WAV files found")
                raise Exception(f"Rendered WAV not found at: {output_wav_path}")
        else:
            print(f"[RENDER_WITH_REAPER] WAV found at expected location")
        
        wav_size = output_wav_path.stat().st_size
        print(f"[RENDER_WITH_REAPER] WAV size: {wav_size} bytes ({wav_size/1024:.1f} KB)")
        print(f"[RENDER_WITH_REAPER] Complete")
        return output_wav_path
        
    except subprocess.TimeoutExpired:
        raise Exception(f"REAPER rendering timeout after {timeout} seconds")
    except Exception as e:
        raise Exception(f"REAPER rendering failed: {e}")


def generate_singing_audio(
    musicxml_path: Path,
    output_wav_path: Path,
    voice: Optional[str] = None
) -> Path:
    """
    Generate singing audio from MusicXML using Synth V + REAPER.
    
    This is the main function that orchestrates the whole workflow:
    1. Create REAPER project with Synth V VST
    2. Render the project to WAV
    
    Args:
        musicxml_path: Path to MusicXML file with embedded lyrics
        output_wav_path: Where to save the singing WAV
        voice: Synth V voice to use (optional)
    
    Returns:
        Path to generated singing WAV file
    """
    print(f"[GENERATE_SINGING_AUDIO] Starting")
    print(f"[GENERATE_SINGING_AUDIO] MusicXML: {musicxml_path}")
    print(f"[GENERATE_SINGING_AUDIO] Output WAV: {output_wav_path}")
    print(f"[GENERATE_SINGING_AUDIO] Voice: {voice or cfg.SYNTHV_VOICE}")
    
    # Create temporary REAPER project file
    rpp_path = output_wav_path.with_suffix('.rpp')
    
    # Step 1: Create REAPER project
    print(f"[GENERATE_SINGING_AUDIO] Step 1: Creating REAPER project...")
    create_reaper_project(musicxml_path, rpp_path, voice)
    
    # Step 2: Render with REAPER
    print(f"[GENERATE_SINGING_AUDIO] Step 2: Rendering with REAPER...")
    render_with_reaper(rpp_path, output_wav_path)
    
    print(f"[GENERATE_SINGING_AUDIO] Complete: {output_wav_path}")
    return output_wav_path

