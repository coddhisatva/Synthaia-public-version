/**
 * MIDI Player Component
 * 
 * Loads and plays MIDI files with multi-track display
 */

import { useState, useEffect, useRef } from 'react';
import { Midi } from '@tonejs/midi';
import * as Tone from 'tone';
import Soundfont from 'soundfont-player';
import config from '../config';

export default function MidiPlayer({ midiUrl, vocalWavUrl }) {
  const [isLoading, setIsLoading] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [tracks, setTracks] = useState([]);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [error, setError] = useState(null);
  const [isLoadingInstruments, setIsLoadingInstruments] = useState(false);
  const [selectedInstruments, setSelectedInstruments] = useState({
    0: 'acoustic_grand_piano',
    1: 'lead_8_bass__lead',
    2: 'voice_oohs',  // Vocal track
    9: 'webaudiofont_power' // Track drum kit selection
  });
  const [isDrumWebAudioFont, setIsDrumWebAudioFont] = useState(true);
  const [channelGains, setChannelGains] = useState({
    0: 100,   // Melody (100% = 1.0 gain)
    1: 100,   // Harmony (100% = 1.0 gain)
    2: 100,   // Vocal MIDI (default 100% = 1.0 gain)
    9: 100,   // Drums (100% = 0.2 gain for WebAudioFont, 1.0 for soundfont)
    'wav': 100 // Vocal WAV (100% = 1.0 gain)
  });
  
  const instrumentsRef = useRef({});
  const midiRef = useRef(null);
  const playbackRef = useRef(null);
  const drumPlayerRef = useRef(null);
  const drumKitRef = useRef(null);
  const drumGainRef = useRef(null);
  const vocalAudioRef = useRef(null);
  const [vocalWavMuted, setVocalWavMuted] = useState(false);
  
  // Instrument options for each channel
  const instrumentOptions = {
    0: [
      { value: 'acoustic_grand_piano', label: 'Piano' },
      { value: 'distortion_guitar', label: 'Distorted Guitar' },
      { value: 'lead_1_square', label: 'Square Lead' },
      { value: 'lead_2_sawtooth', label: 'Sawtooth Lead' },
      { value: 'synth_strings_1', label: 'Synth Strings' }
    ],
    1: [
      { value: 'rock_organ', label: 'Rock Organ' },
      { value: 'distortion_guitar', label: 'Distorted Guitar' },
      { value: 'lead_2_sawtooth', label: 'Sawtooth Lead' },
      { value: 'lead_8_bass__lead', label: 'Bass Lead' },
      { value: 'string_ensemble_1', label: 'String Ensemble' }
    ],
    2: [
      { value: 'choir_aahs', label: 'Choir Aahs' },
      { value: 'voice_oohs', label: 'Voice Oohs' },
      { value: 'lead_6_voice', label: 'Lead Voice' },
      { value: 'pad_3_polysynth', label: 'Poly Synth Pad' },
      { value: 'flute', label: 'Flute' },
      { value: 'ocarina', label: 'Ocarina' },
      { value: 'blown_bottle', label: 'Blown Bottle' },
      { value: 'pad_4_choir', label: 'Choir Pad' }
    ],
    9: [
      { value: 'webaudiofont_power', label: 'Power Drums (WebAudioFont)' },
      { value: 'synth_drum', label: 'Synth Drums' },
      { value: 'taiko_drum', label: 'Taiko Drums' },
      { value: 'steel_drums', label: 'Steel Drums' },
      { value: 'woodblock', label: 'Woodblock' }
    ]
  };

  // Load drums once on mount
  useEffect(() => {
    loadDrums();
  }, []);

  // Load MIDI file when URL changes
  useEffect(() => {
    loadMidi();
    return () => {
      // Cleanup on unmount
      stopPlayback();
    };
  }, [midiUrl]);

  // Load vocal WAV when URL changes
  useEffect(() => {
    console.log('🔍 MidiPlayer vocalWavUrl prop:', vocalWavUrl);
    if (vocalWavUrl) {
      console.log('✅ Loading vocal WAV audio');
      const audio = new Audio(`${config.apiUrl}${vocalWavUrl}`);
      audio.volume = channelGains['wav'] / 100;
      vocalAudioRef.current = audio;
    } else {
      console.log('⚠️ No vocalWavUrl provided to MidiPlayer');
    }
    return () => {
      if (vocalAudioRef.current) {
        vocalAudioRef.current.pause();
        vocalAudioRef.current = null;
      }
    };
  }, [vocalWavUrl]);

  const loadMidi = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Fetch MIDI file
      const response = await fetch(`${config.apiUrl}${midiUrl}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const arrayBuffer = await response.arrayBuffer();
      
      // Parse MIDI
      const midi = new Midi(arrayBuffer);
      midiRef.current = midi;
      
      // Map channels to instrument names for display (initial load)
      const getInstrumentLabel = (channel, instrumentValue) => {
        const options = instrumentOptions[channel];
        if (options) {
          const found = options.find(opt => opt.value === instrumentValue);
          return found ? found.label : instrumentValue;
        }
        return instrumentValue;
      };
      
      const channelNames = {
        0: getInstrumentLabel(0, selectedInstruments[0]),
        1: getInstrumentLabel(1, selectedInstruments[1]),
        2: getInstrumentLabel(2, selectedInstruments[2]),
        9: getInstrumentLabel(9, selectedInstruments[9]),
      };
      
      // Map track names based on channel
      const getTrackName = (channel, index) => {
        if (channel === 0) return 'Melody';
        if (channel === 1) return 'Harmony';
        if (channel === 2) return 'Vocals';
        if (channel === 9) return 'Drums';
        return `Track ${index + 1}`;
      };
      
      // Extract track info
      const trackInfo = midi.tracks.map((track, index) => ({
        index,
        name: getTrackName(track.channel, index),
        channel: track.channel,
        instrument: channelNames[track.channel] || 'Piano',
        noteCount: track.notes.length,
        muted: false,
      }));
      
      setTracks(trackInfo);
      setDuration(midi.duration);
      
      // Load soundfonts for each track
      await loadInstruments(trackInfo);
      
      setIsLoading(false);
    } catch (err) {
      console.error('Error loading MIDI:', err);
      setError(`Failed to load MIDI file: ${err.message}`);
      setIsLoading(false);
    }
  };

  const loadWebAudioFontPlayer = () => {
    return new Promise((resolve, reject) => {
      // Check if already loaded
      if (window.WebAudioFontPlayer) {
        resolve(window.WebAudioFontPlayer);
        return;
      }
      
      // Load the WebAudioFont player script from CDN
      const script = document.createElement('script');
      script.src = 'https://surikov.github.io/webaudiofont/npm/dist/WebAudioFontPlayer.js';
      script.onload = () => {
        if (window.WebAudioFontPlayer) {
          resolve(window.WebAudioFontPlayer);
        } else {
          reject(new Error('WebAudioFontPlayer not found after script load'));
        }
      };
      script.onerror = () => reject(new Error('Failed to load WebAudioFontPlayer script'));
      document.head.appendChild(script);
    });
  };

  const loadDrums = async () => {
    try {
      console.log('🥁 Loading drum samples on page load...');
      
      // Load WebAudioFont player
      const WebAudioFontPlayer = await loadWebAudioFontPlayer();
      const audioContext = Tone.context.rawContext;
      
      // Initialize WebAudioFont player for drums
      drumPlayerRef.current = new WebAudioFontPlayer();
      
      // Create a gain node to control drum volume
      // Base volume is 0.2 (20%), but UI will show as 100% (neutral)
      drumGainRef.current = audioContext.createGain();
      drumGainRef.current.gain.value = 0.2 * (channelGains[9] / 100);
      drumGainRef.current.connect(audioContext.destination);
      
      // Load individual drum samples for the 10 notes our AI generates
      const drumNotes = [36, 38, 42, 46, 41, 47, 48, 43, 49, 51];
      drumKitRef.current = {};
      
      // Load all drum script files
      const loadPromises = drumNotes.map(async (note) => {
        const drumUrl = `https://surikov.github.io/webaudiofontdata/sound/128${note}_1_JCLive_sf2_file.js`;
        try {
          const response = await fetch(drumUrl);
          const drumCode = await response.text();
          
          // Use indirect eval to execute in global scope
          (0, eval)(drumCode);
          
          // Store the drum preset by MIDI note number
          const varName = `_drum_${note}_1_JCLive_sf2_file`;
          const preset = window[varName];
          
          if (preset) {
            drumKitRef.current[note] = preset;
            console.log(`✓ Loaded drum ${note}`);
            return { note, varName, preset };
          } else {
            console.error(`Failed to find window.${varName} after eval`);
            return null;
          }
        } catch (err) {
          console.warn(`Failed to load drum ${note}:`, err);
          return null;
        }
      });
      
      const loadedDrums = await Promise.all(loadPromises);
      
      // Now decode all the samples (this prepares them for playback)
      console.log('Decoding drum samples...');
      for (const drumInfo of loadedDrums) {
        if (drumInfo) {
          drumPlayerRef.current.loader.decodeAfterLoading(audioContext, drumInfo.varName);
        }
      }
      
      // Wait for decoding to complete
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log('✅ All drums ready for playback');
    } catch (err) {
      console.error('Failed to load drums:', err);
    }
  };

  const loadInstruments = async (trackInfo) => {
    const audioContext = Tone.context.rawContext;
    
    // Load soundfonts for melodic channels only (drums loaded separately on mount)
    const channelInstruments = {
      0: await Soundfont.instrument(audioContext, selectedInstruments[0]),  // Melody
      1: await Soundfont.instrument(audioContext, selectedInstruments[1]),  // Harmony
      2: await Soundfont.instrument(audioContext, selectedInstruments[2]),  // Vocals
    };
    
    // Assign instruments based on channel
    trackInfo.forEach(track => {
      // Skip channel 9 (drums) - uses WebAudioFont loaded on page load
      if (track.channel !== 9) {
        const instrument = channelInstruments[track.channel] || channelInstruments[0];
        instrumentsRef.current[track.index] = instrument;
      }
    });
  };

  const changeGain = (channel, newGain) => {
    setChannelGains(prev => ({ ...prev, [channel]: newGain }));
    
    // Update WAV volume in real-time if it's playing
    if (channel === 'wav' && vocalAudioRef.current) {
      vocalAudioRef.current.volume = newGain / 100;
    }
  };

  const changeInstrument = async (channel, newInstrumentValue) => {
    setIsLoadingInstruments(true);
    
    try {
      const audioContext = Tone.context.rawContext;
      
      // Handle drums (channel 9) specially
      if (channel === 9) {
        if (newInstrumentValue === 'webaudiofont_power') {
          // Switch to WebAudioFont drums (already loaded)
          setIsDrumWebAudioFont(true);
          console.log('✓ Switched to WebAudioFont Power Drums');
        } else {
          // Switch to soundfont drums
          const newInstrument = await Soundfont.instrument(audioContext, newInstrumentValue);
          
          // Update instruments ref for drum tracks
          tracks.forEach((track, index) => {
            if (track.channel === 9) {
              instrumentsRef.current[index] = newInstrument;
            }
          });
          
          setIsDrumWebAudioFont(false);
          console.log(`✓ Switched to soundfont drums: ${newInstrumentValue}`);
        }
      } else {
        // Handle melodic instruments (channels 0, 1)
        const newInstrument = await Soundfont.instrument(audioContext, newInstrumentValue);
        
        // Update the instruments ref for all tracks using this channel
        tracks.forEach((track, index) => {
          if (track.channel === channel) {
            instrumentsRef.current[index] = newInstrument;
          }
        });
        
        console.log(`✓ Changed channel ${channel} to ${newInstrumentValue}`);
      }
      
      // Update state
      setSelectedInstruments(prev => ({
        ...prev,
        [channel]: newInstrumentValue
      }));
      
    } catch (err) {
      console.error(`Failed to load instrument ${newInstrumentValue}:`, err);
    } finally {
      setIsLoadingInstruments(false);
    }
  };

  const togglePlayback = async () => {
    if (isPlaying) {
      stopPlayback();
    } else {
      await startPlayback();
    }
  };

  const toggleVocalWavMute = () => {
    setVocalWavMuted(prev => !prev);
  };

  const startPlayback = async () => {
    if (!midiRef.current) return;
    
    // Start Tone.js audio context
    await Tone.start();
    
    // Restore drum gain if it was muted, applying user's gain setting
    if (drumGainRef.current) {
      const drumGain = 0.2 * (channelGains[9] / 100);
      drumGainRef.current.gain.cancelScheduledValues(Tone.context.rawContext.currentTime);
      drumGainRef.current.gain.setValueAtTime(drumGain, Tone.context.rawContext.currentTime);
    }
    
    setIsPlaying(true);
    const startTime = Tone.now();
    const audioContext = Tone.context.rawContext;
    
    // Start vocal WAV if available and not muted
    if (vocalAudioRef.current && !vocalWavMuted) {
      vocalAudioRef.current.currentTime = 0;
      vocalAudioRef.current.play().catch(err => console.error('Error playing vocal WAV:', err));
    }
    
    // Schedule all notes
    midiRef.current.tracks.forEach((track, trackIndex) => {
      if (tracks[trackIndex]?.muted) return;
      
      // Check if this is a drum track (channel 9)
      const isDrumTrack = track.channel === 9;
      
      if (isDrumTrack) {
        if (isDrumWebAudioFont && drumPlayerRef.current && drumKitRef.current && drumGainRef.current) {
          // Use WebAudioFont for drums
          console.log('Playing WebAudioFont drums with', track.notes.length, 'notes');
          
          track.notes.forEach(note => {
            const noteTime = startTime + note.time;
            const when = noteTime - Tone.now() + audioContext.currentTime;
            
            // Get the drum sample for this specific MIDI note
            const drumPreset = drumKitRef.current[note.midi];
            
            if (drumPreset) {
              // Route drums through gain node for volume control
              drumPlayerRef.current.queueWaveTable(
                audioContext,
                drumGainRef.current, // Use gain node for volume control
                drumPreset,
                when,
                note.midi, // MIDI note number (e.g., 36 = kick, 38 = snare)
                3 // Fixed duration in seconds like the working example
              );
            }
          });
        } else {
          // Use soundfont-player for drums
          const instrument = instrumentsRef.current[trackIndex];
          if (instrument) {
            console.log('Playing soundfont drums with', track.notes.length, 'notes');
            const gain = channelGains[9] / 100;
            track.notes.forEach(note => {
              const noteTime = startTime + note.time;
              instrument.play(note.name, noteTime, { duration: note.duration, gain });
            });
          }
        }
      } else {
        // Use soundfont-player for melodic instruments
        const instrument = instrumentsRef.current[trackIndex];
        if (!instrument) return;
        
        // Get gain for this channel
        const gain = channelGains[track.channel] / 100 || 1.0;
        
        track.notes.forEach(note => {
          const noteTime = startTime + note.time;
          instrument.play(note.name, noteTime, { duration: note.duration, gain });
        });
      }
    });
    
    // Update progress
    const updateInterval = setInterval(() => {
      const elapsed = Tone.now() - startTime;
      setCurrentTime(elapsed);
      
      if (elapsed >= duration) {
        stopPlayback();
      }
    }, 100);
    
    playbackRef.current = { startTime, updateInterval };
  };

  const stopPlayback = () => {
    setIsPlaying(false);
    setCurrentTime(0);
    
    if (playbackRef.current?.updateInterval) {
      clearInterval(playbackRef.current.updateInterval);
    }
    
    // Stop all soundfont instruments
    Object.values(instrumentsRef.current).forEach(instrument => {
      if (instrument.stop) instrument.stop();
    });
    
    // Clear WebAudioFont drum queue by disconnecting and recreating gain node
    // (queued audio samples can't be cancelled, so we disconnect the destination)
    if (drumGainRef.current) {
      drumGainRef.current.disconnect();
      
      // Recreate gain node for next playback
      const audioContext = Tone.context.rawContext;
      drumGainRef.current = audioContext.createGain();
      drumGainRef.current.gain.value = 0.2 * (channelGains[9] / 100);
      drumGainRef.current.connect(audioContext.destination);
    }
    
    // Stop vocal WAV
    if (vocalAudioRef.current) {
      vocalAudioRef.current.pause();
      vocalAudioRef.current.currentTime = 0;
    }
    
    playbackRef.current = null;
  };

  const toggleMute = (trackIndex) => {
    setTracks(prev => prev.map((track, i) => 
      i === trackIndex ? { ...track, muted: !track.muted } : track
    ));
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">Loading MIDI player...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">🎹 MIDI Player</h3>
      
      {/* Playback Controls */}
      <div className="mb-6">
        <div className="flex items-center gap-4 mb-3">
          <button
            onClick={togglePlayback}
            disabled={isLoadingInstruments}
            className={`${isLoadingInstruments ? 'bg-gray-400 cursor-not-allowed' : 'bg-purple-600 hover:bg-purple-700'} text-white px-6 py-2 rounded-lg transition font-medium`}
          >
            {isPlaying ? '⏸ Pause' : '▶ Play'}
          </button>
          
          <button
            onClick={stopPlayback}
            disabled={!isPlaying || isLoadingInstruments}
            className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 disabled:bg-gray-300 transition font-medium"
          >
            ⏹ Stop
          </button>
          
          <span className="text-sm text-gray-600">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-purple-600 h-2 rounded-full transition-all"
            style={{ width: `${(currentTime / duration) * 100}%` }}
          />
        </div>
      </div>
      
      {/* Track List */}
      <div className="space-y-2">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">Tracks ({tracks.length})</h4>
        {tracks.map((track) => (
          <div 
            key={track.index}
            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
          >
            <div className="flex items-center gap-3">
              <button
                onClick={() => toggleMute(track.index)}
                className={`px-3 py-1 rounded text-sm font-medium transition ${
                  track.muted 
                    ? 'bg-gray-300 text-gray-600' 
                    : 'bg-green-500 text-white'
                }`}
              >
                {track.muted ? '🔇' : '🔊'}
              </button>
              <div>
                <p className="text-sm font-medium text-gray-800">{track.name}</p>
                <p className="text-xs text-gray-500">{track.noteCount} notes</p>
              </div>
            </div>
            
            {/* Instrument selector and gain control for channels 0, 1, 2 (vocals), and 9 (drums) */}
            {(track.channel === 0 || track.channel === 1 || track.channel === 2 || track.channel === 9) && instrumentOptions[track.channel] ? (
              <div className="flex items-center gap-2">
                <select
                  value={selectedInstruments[track.channel]}
                  onChange={(e) => changeInstrument(track.channel, e.target.value)}
                  disabled={isLoadingInstruments || isPlaying}
                  className="text-xs px-2 py-1 border border-gray-300 rounded bg-white disabled:bg-gray-100 disabled:cursor-not-allowed"
                >
                  {instrumentOptions[track.channel].map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                
                <div className="flex items-center gap-1">
                  <span className="text-xs text-gray-600">Vol:</span>
                  <input
                    type="range"
                    min="0"
                    max="150"
                    value={channelGains[track.channel] || 100}
                    onChange={(e) => changeGain(track.channel, parseInt(e.target.value))}
                    disabled={isPlaying}
                    className="w-20 h-1 disabled:opacity-50 disabled:cursor-not-allowed"
                    style={{
                      accentColor: isPlaying ? '#9ca3af' : '#9333ea'
                    }}
                  />
                  <span className="text-xs text-gray-600 w-8">{channelGains[track.channel] || 100}%</span>
                </div>
              </div>
            ) : (
              <span className="text-xs text-gray-500">{track.instrument}</span>
            )}
          </div>
        ))}
        
        {/* Vocal WAV Track (if available) */}
        {vocalWavUrl && (
          <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center gap-3">
              <button
                onClick={toggleVocalWavMute}
                className={`px-3 py-1 rounded text-sm font-medium transition ${
                  vocalWavMuted 
                    ? 'bg-gray-300 text-gray-600' 
                    : 'bg-green-500 text-white'
                }`}
              >
                {vocalWavMuted ? '🔇' : '🔊'}
              </button>
              <div>
                <p className="text-sm font-medium text-gray-800">🎤 Vocal Audio (WAV)</p>
                <p className="text-xs text-gray-500">AI-generated vocals</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                <span className="text-xs text-gray-600">Vol:</span>
                <input
                  type="range"
                  min="0"
                  max="150"
                  value={channelGains['wav'] || 100}
                  onChange={(e) => changeGain('wav', parseInt(e.target.value))}
                  className="w-20 h-1"
                  style={{
                    accentColor: '#9333ea'
                  }}
                />
                <span className="text-xs text-gray-600 w-8">{channelGains['wav'] || 100}%</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

