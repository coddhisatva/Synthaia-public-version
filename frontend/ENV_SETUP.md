# Environment Configuration

The frontend uses environment variables to configure the backend API connection.

## Default Configuration

By default, the app connects to:
- **API URL:** `http://localhost:8000`
- **WebSocket URL:** `ws://localhost:8000`

These defaults work for local development when running both frontend and backend on the same machine.

## Custom Configuration (Optional)

To override the defaults, create a `.env.local` file in the `frontend/` directory:

```bash
# .env.local
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

**Note:** `.env.local` is gitignored and won't be committed to the repository.

## Configuration File

All configuration is centralized in `src/config.js`, which exports:
- `apiUrl` - Backend HTTP API base URL
- `wsUrl` - WebSocket base URL
- `wsEndpoint` - WebSocket endpoint path

Import and use:
```javascript
import config from './config';

const ws = new WebSocket(`${config.wsUrl}${config.wsEndpoint}`);
```

