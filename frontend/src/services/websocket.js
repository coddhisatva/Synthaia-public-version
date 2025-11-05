/**
 * WebSocket Service for Song Generation
 * 
 * Handles WebSocket connection to backend for real-time song generation
 * with progress updates.
 */

import config from '../config';

/**
 * Connect to WebSocket and generate a song
 * 
 * @param {string} theme - Song theme/concept
 * @param {string} provider - AI provider ('gemini' or 'openai')
 * @param {Function} onProgress - Callback for progress updates (step, total, message, percentage)
 * @param {Function} onComplete - Callback when generation is complete (result)
 * @param {Function} onError - Callback for errors (error)
 * @returns {WebSocket} - The WebSocket connection (to allow manual close)
 */
export function generateSong(theme, provider, onProgress, onComplete, onError) {
  const wsUrl = `${config.wsUrl}${config.wsEndpoint}`;
  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log('WebSocket connected');
    // Send request to start generation
    ws.send(JSON.stringify({ theme, provider }));
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);

      // Check for errors
      if (data.status === 'error' || data.error) {
        console.error('WebSocket error:', data);
        onError(data.error || data.message || 'Unknown error');
        ws.close();
        return;
      }

      // Check if generation is complete
      if (data.status === 'success' && data.result) {
        console.log('Generation complete!', data.result);
        onComplete(data.result);
        ws.close();
        return;
      }

      // Progress update
      if (data.step && data.total && data.message) {
        console.log(`Progress: Step ${data.step}/${data.total} - ${data.message}`);
        onProgress(data.step, data.total, data.message, data.percentage);
      }
    } catch (err) {
      console.error('Error parsing WebSocket message:', err);
      onError('Failed to parse server response');
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    onError('Connection error. Make sure the backend is running.');
  };

  ws.onclose = (event) => {
    console.log('WebSocket disconnected', event);
    // If connection closes unexpectedly (not cleanly), treat as error
    if (!event.wasClean) {
      console.error('WebSocket closed unexpectedly');
      onError('Connection lost. Check backend logs for errors.');
    }
  };

  return ws;
}

/**
 * Check backend health
 * 
 * @returns {Promise<object>} - Health check response
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${config.apiUrl}/health`);
    return await response.json();
  } catch (error) {
    throw new Error('Backend is not reachable');
  }
}

