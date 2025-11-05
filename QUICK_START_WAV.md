# Quick Start: WAV Export

## What's New?

Your songs now **automatically export as playable audio files**! 🎉

## Two Versions

Every song generates **2 WAV files**:

1. **Complete Audio** (`{song}_complete.wav`)
   - All 4 tracks: Melody + Harmony + Vocals + Drums
   - Vocals are choir/synth sounds (not sung)
   - Ready to play or share

2. **Instrumental** (`{song}_instrumental.wav`)
   - 3 tracks: Melody + Harmony + Drums
   - No vocals - perfect backing track
   - Great for karaoke or adding your own vocals

## How to Use

### Web App (Automatic):
1. Generate a song
2. Wait for steps 8/9 and 9/9 (WAV rendering)
3. Click download buttons that appear
4. Play in any audio player!

### CLI (Manual):
```bash
# Render existing MIDI to WAV
python scripts/audio/render_midi.py output/midi/my_song_complete.mid -o output/audio/my_song.wav
```

## Requirements

**FluidSynth** must be installed:
```bash
# macOS
brew install fluidsynth

# Linux
sudo apt-get install fluidsynth
```

**Soundfont** is already included (`soundfonts/MuseScore_General.sf3`)

## Testing

Run the test suite to verify everything works:
```bash
python test_wav_export.py
```

## Quality

- **Sample Rate**: 44.1 kHz (CD quality)
- **Format**: Uncompressed WAV
- **Duration**: ~30-60 seconds per song
- **File Size**: ~5-15 MB per WAV

## Tips

### Want better vocals?
1. Download the vocals MIDI (`{song}_vocals.mid`)
2. Import into Synthesizer V or ACE Studio
3. Render with AI singing voice
4. Mix with instrumental WAV in your DAW

### Want professional mixing?
1. Download the complete MIDI
2. Import into GarageBand, Logic, or Ableton
3. Add effects (reverb, EQ, compression)
4. Export with custom instrument sounds

### Having issues?
- Check if FluidSynth is installed: `fluidsynth --version`
- Check backend console for error messages
- WAV generation is optional - MIDI will still work
- See `WAV_EXPORT_IMPLEMENTATION.md` for troubleshooting

## Files Reference

```
output/
├── audio/
│   ├── song_123_complete.wav       ← All tracks
│   └── song_123_instrumental.wav   ← No vocals
├── midi/
│   ├── song_123_complete.mid       ← Full MIDI
│   └── song_123_vocals.mid         ← For Synth V
└── songs/
    └── song_123.txt                ← Lyrics
```

## What's Next?

Future improvements:
- [ ] Per-track volume mixing controls
- [ ] Basic reverb/EQ effects
- [ ] Progress bar for long renders
- [ ] Batch WAV rendering for old songs

## Questions?

See `WAV_EXPORT_IMPLEMENTATION.md` for technical details.

---

**Enjoy your instant audio exports!** 🎶

