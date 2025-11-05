/**
 * Application Configuration
 * 
 * Environment variables for connecting to the backend API
 */

const config = {
  // Backend API base URL (HTTP)
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  
  // WebSocket URL for real-time song generation
  wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
  
  // WebSocket endpoint path
  wsEndpoint: '/api/ws/generate-song',
};

export default config;

