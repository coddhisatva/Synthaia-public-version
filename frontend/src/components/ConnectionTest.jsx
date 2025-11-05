/**
 * Connection Test Component
 * 
 * Tests WebSocket connection to backend and displays status
 */

import { useState, useEffect, useRef } from 'react';
import { checkHealth, generateSong } from '../services/websocket';
import ProgressIndicator from './ProgressIndicator';
import ErrorAlert from './ErrorAlert';
import LoadingSpinner from './LoadingSpinner';
import MidiPlayer from './MidiPlayer';

export default function ConnectionTest() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [healthError, setHealthError] = useState(null);
  
  const [testTheme, setTestTheme] = useState('summer vibes');
  const [provider, setProvider] = useState('');
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [currentWebSocket, setCurrentWebSocket] = useState(null);
  
  // Ref to track current result for callbacks (avoids stale closure)
  const resultRef = useRef(null);
  
  // Keep ref in sync with state
  useEffect(() => {
    resultRef.current = result;
  }, [result]);
  
  // Load song history from localStorage on mount
  const [songHistory, setSongHistory] = useState(() => {
    const saved = localStorage.getItem('songHistory');
    return saved ? JSON.parse(saved) : [];
  });

  // Save song history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('songHistory', JSON.stringify(songHistory));
  }, [songHistory]);

  // Auto-load default provider from backend on mount
  useEffect(() => {
    const loadDefaultProvider = async () => {
      try {
        const health = await checkHealth();
        if (health.provider) {
          setProvider(health.provider);
        }
      } catch (err) {
        console.error('Failed to load default provider:', err);
      }
    };
    loadDefaultProvider();
  }, []);

  // Save current song to history before page unload (refresh, close tab, navigate away)
  useEffect(() => {
    const handleBeforeUnload = () => {
      if (result) {
        // Add current song to history
        const currentHistory = JSON.parse(localStorage.getItem('songHistory') || '[]');
        const updated = [result, ...currentHistory].slice(0, 10);
        localStorage.setItem('songHistory', JSON.stringify(updated));
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [result]);

  const testHealth = async () => {
    setHealthLoading(true);
    setHealthError(null);
    try {
      const health = await checkHealth();
      setHealthStatus(health);
      // Update provider if backend config changed
      if (health.provider) {
        setProvider(health.provider);
      }
    } catch (err) {
      setHealthError(err.message);
    } finally {
      setHealthLoading(false);
    }
  };

  const testGeneration = () => {
    if (!testTheme.trim()) {
      setError('Please enter a theme');
      return;
    }

    // Move current song to history when generating new song
    if (resultRef.current) {
      setSongHistory(prev => [resultRef.current, ...prev].slice(0, 10));
    }

    setGenerating(true);
    setProgress(null);
    setResult(null);
    setError(null);

    const ws = generateSong(
      testTheme,
      provider,
      // onProgress
      (step, total, message, percentage) => {
        setProgress({ step, total, message, percentage });
      },
      // onComplete
      (newResult) => {
        console.log('🔍 Song generation complete, result:', newResult);
        console.log('🔍 vocal_wav_url in result:', newResult.vocal_wav_url);
        const resultWithTheme = {...newResult, theme: testTheme, id: `${Date.now()}-${Math.random()}`};
        
        // New song just becomes current (history is updated when user generates NEXT song)
        setResult(resultWithTheme);
        
        setGenerating(false);
        setProgress(null);
        setCurrentWebSocket(null);
      },
      // onError
      (error) => {
        setError(error);
        setGenerating(false);
        setProgress(null);
        setCurrentWebSocket(null);
      }
    );
    
    setCurrentWebSocket(ws);
  };

  const cancelGeneration = () => {
    if (currentWebSocket) {
      currentWebSocket.close();
      setCurrentWebSocket(null);
    }
    setGenerating(false);
    setProgress(null);
    setError('Generation cancelled by user');
  };

  const loadSongFromHistory = (song) => {
    // Swap: current → history, loaded song removed from history
    setSongHistory(prev => {
      const filtered = prev.filter(s => s.id !== song.id); // Remove loaded song
      if (resultRef.current) {
        return [resultRef.current, ...filtered].slice(0, 10); // Add current to history
      }
      return filtered;
    });
    
    // Display the loaded song
    setResult(song);
    setTestTheme(song.theme);
    setError(null);
  };

  return (
    <div className="flex gap-6">
      {/* Main Content - Song Generation */}
      <div className="flex-1">
        <div className="bg-white rounded-lg shadow p-6">
          {/* Header with Title and AI Model Selector */}
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold">Create Your Song Below</h3>
            
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">
                AI Model:
              </label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                disabled={generating}
                className="px-3 py-1 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
              >
                <option value="">Select...</option>
                <option value="google">Gemini 2.5 Flash</option>
                <option value="openai">GPT-4o Mini</option>
              </select>
            </div>
          </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AI, make me a song about...
            </label>
            <input
              type="text"
              value={testTheme}
              onChange={(e) => setTestTheme(e.target.value)}
              disabled={generating}
              placeholder="Enter a theme..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
            />
          </div>

          <div className="flex gap-3">
            <button
              onClick={testGeneration}
              disabled={generating}
              className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition font-medium"
            >
              {generating ? 'Generating...' : 'Create Song'}
            </button>
            
            {generating && (
              <button
                onClick={cancelGeneration}
                className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition font-medium"
              >
                Cancel
              </button>
            )}
          </div>

          {/* Troubleshooting Tip */}
          {(generating || error) && (
            <div className="mt-3">
              <p className="text-sm text-gray-500 text-center">
                If you are having trouble generating at a given time, try switching models.
              </p>
            </div>
          )}
        </div>

        {/* Progress Display */}
        {generating && (
          <div className="mt-6">
            {progress ? (
              <ProgressIndicator
                step={progress.step}
                total={progress.total}
                message={progress.message}
                percentage={progress.percentage}
              />
            ) : (
              <LoadingSpinner message="Connecting to backend..." />
            )}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mt-6">
            <ErrorAlert error={error} onClose={() => setError(null)} />
          </div>
        )}

        {/* Result Display */}
        {result && (
          <div className="mt-6 space-y-6">
            {/* Song Title & Info */}
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800 font-semibold text-lg mb-2">{result.theme}</p>
              <div className="space-y-2 text-sm">
                <p><strong>Complete MIDI:</strong> 
                  <a 
                    href={`http://localhost:8000${result.midi_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline ml-2"
                  >
                    Download All Tracks
                  </a>
                </p>
                <p><strong>Vocals MIDI:</strong> 
                  <a 
                    href={`http://localhost:8000${result.midi_url.replace('_complete', '_vocals')}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline ml-2"
                  >
                    Download Vocals Only
                  </a>
                  <span className="text-xs text-gray-500 ml-2">(Render in Synth V/Vocaloid)</span>
                </p>
                {result.complete_wav_url && (
                  <p><strong>Complete Audio (WAV):</strong> 
                    <a 
                      href={`http://localhost:8000${result.complete_wav_url}`}
                      download
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline ml-2"
                    >
                      Download with Vocal midi
                    </a>
                    <span className="text-xs text-gray-500 ml-2">(All 4 tracks mixed)</span>
                  </p>
                )}
                {result.instrumental_wav_url && (
                  <p><strong>Instrumental Audio (sans Vocal track) (WAV):</strong> 
                    <a 
                      href={`http://localhost:8000${result.instrumental_wav_url}`}
                      download
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline ml-2"
                    >
                      Download without Vocal midi
                    </a>
                    <span className="text-xs text-gray-500 ml-2">(Melody, harmony, drums only)</span>
                  </p>
                )}
                <p><strong>Timestamp:</strong> {result.timestamp}</p>
                <details className="mt-2">
                  <summary className="cursor-pointer text-gray-700 font-medium">View Lyrics</summary>
                  <pre className="mt-2 p-3 bg-white border border-gray-200 rounded text-xs overflow-auto max-h-64">
                    {result.lyrics}
                  </pre>
                </details>
              </div>
            </div>
            
            {/* MIDI Player */}
            <MidiPlayer midiUrl={result.midi_url} vocalWavUrl={result.vocal_wav_url} />
            
            {/* Vocal Synthesis Explanation */}
            <div className="mt-6 p-6 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Turning Vocal Track into Real Vocals Sung by AI</h3>
              
              <div className="space-y-3 text-sm text-gray-700">
                <p>
                  Unfortunately, while this functionality exists in various software, I haven't found a way to automate 
                  this within a web application, because none of the available software I've found have any APIs or CLIs. 
                  If you discover this functionality (or create it), please let me know at{' '}
                  <a href="mailto:conoregan151@gmail.com" className="text-blue-600 hover:underline">
                    conoregan151@gmail.com
                  </a>.
                </p>
                
                <p>
                  In the meantime, we've provided the vocal MIDI track for download, which has the lyrics embedded in it.
                </p>
                
                <p>
                  Therefore, all a user needs to do is open up one of these software, select a voice, and playback/export. 
                  Then they can take the rest of the MIDI into a DAW, and put the rest of the song together.
                </p>
                
                <div className="mt-4 space-y-2">
                  <p className="font-medium">Recommended Software:</p>
                  <ul className="list-disc list-inside space-y-1 ml-2">
                    <li>
                      <a 
                        href="https://dreamtonics.com/synthesizerv/" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline font-medium"
                      >
                        Synthesizer V
                      </a>
                      {' '}- One good option, which has a free trial that I've tested.
                    </li>
                    <li>
                      <a 
                        href="https://acestudio.ai/" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline font-medium"
                      >
                        ACE Studio
                      </a>
                      {' '}- Also supposed to be a solid option.
                    </li>
                  </ul>
                </div>
                
                <p className="mt-4 italic text-gray-600">
                  Hopefully, I am able to figure out a way to implement this feature in the future, and put the whole project together.
                </p>
              </div>
            </div>
          </div>
        )}
        </div>
      </div>

      {/* Right Sidebar */}
      <div className="w-50 space-y-6">
        {/* Backend Status */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-md font-semibold mb-4">Backend Status</h3>
          
          <button
            onClick={testHealth}
            disabled={healthLoading}
            className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition text-sm"
          >
            {healthLoading ? 'Checking...' : 'Check Connection'}
          </button>

          {healthLoading && (
            <div className="mt-4">
              <LoadingSpinner message="Checking..." />
            </div>
          )}

          {healthError && (
            <div className="mt-4">
              <ErrorAlert error={healthError} onClose={() => setHealthError(null)} />
            </div>
          )}

          {healthStatus && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800 font-medium text-sm">✓ Connected</p>
              <pre className="mt-2 text-xs text-gray-600 overflow-auto">
                {JSON.stringify(healthStatus, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Song History */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-md font-semibold mb-4">Recent Songs</h3>
          
          {songHistory.length === 0 ? (
            <p className="text-sm text-gray-500">No songs generated yet</p>
          ) : (
            <>
              <div className="space-y-3">
                {songHistory.map((song) => (
                  <div key={song.id} className="border border-gray-200 rounded-lg">
                    <div className="px-3 py-2 flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">{song.theme}</span>
                      <button
                        onClick={() => loadSongFromHistory(song)}
                        className="text-xs bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700 transition"
                      >
                        Load
                      </button>
                    </div>
                    <details className="border-t border-gray-200">
                      <summary className="cursor-pointer px-3 py-2 hover:bg-gray-50 text-xs text-gray-600">
                        More options...
                      </summary>
                      <div className="px-3 py-2 border-t border-gray-200 space-y-2">
                        <a 
                          href={`http://localhost:8000${song.midi_url}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block text-sm text-blue-600 hover:underline"
                        >
                          📥 Download MIDI
                        </a>
                        {song.complete_wav_url && (
                          <a 
                            href={`http://localhost:8000${song.complete_wav_url}`}
                            download
                            className="block text-sm text-blue-600 hover:underline"
                          >
                            🔊 Download Complete Audio (WAV)
                          </a>
                        )}
                        {song.instrumental_wav_url && (
                          <a 
                            href={`http://localhost:8000${song.instrumental_wav_url}`}
                            download
                            className="block text-sm text-blue-600 hover:underline"
                          >
                            🎵 Download Instrumental (WAV)
                          </a>
                        )}
                        <details className="mt-2">
                          <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-800">View Lyrics</summary>
                          <pre className="mt-2 p-2 bg-gray-50 border border-gray-200 rounded text-xs overflow-auto max-h-40">
                            {song.lyrics}
                          </pre>
                        </details>
                      </div>
                    </details>
                  </div>
                ))}
              </div>
              
              <button
                onClick={() => setSongHistory([])}
                className="w-full mt-4 bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition text-sm"
              >
                Clear History
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

