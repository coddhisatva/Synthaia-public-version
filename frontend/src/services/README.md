# Services

This directory contains service modules for interacting with the backend.

## WebSocket Service

### Usage Example

```javascript
import { generateSong, checkHealth } from './services/websocket';

// Generate a song with real-time progress
const ws = generateSong(
  'summer romance',  // theme
  
  // onProgress callback
  (step, total, message, percentage) => {
    console.log(`Step ${step}/${total}: ${message} (${percentage}%)`);
  },
  
  // onComplete callback
  (result) => {
    console.log('Song complete!');
    console.log('Lyrics:', result.lyrics);
    console.log('MIDI URL:', result.midi_url);
  },
  
  // onError callback
  (error) => {
    console.error('Error:', error);
  }
);

// To cancel generation (optional)
// ws.close();

// Check backend health
const health = await checkHealth();
console.log('Backend status:', health);
```

## API Responses

### Progress Update
```json
{
  "step": 2,
  "total": 7,
  "message": "Creating melody...",
  "percentage": 28
}
```

### Success Response
```json
{
  "step": 7,
  "total": 7,
  "message": "Complete! ✓",
  "percentage": 100,
  "status": "success",
  "result": {
    "theme": "summer romance",
    "lyrics": "Verse 1:\n...",
    "midi_url": "/files/midi/summer_romance_1234_complete.mid",
    "timestamp": 1234567890
  }
}
```

### Error Response
```json
{
  "error": "Theme is required",
  "status": "error"
}
```

