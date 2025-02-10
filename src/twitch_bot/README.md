# Twitch Bot Service

This service provides an AI-powered Twitch chat bot that integrates with TTS and LLM services to create an engaging co-hosting experience.

## Features

- FastAPI-based web interface for bot management
- OAuth-based Twitch authentication
- Intelligent message parsing and response handling
- Text-to-Speech integration for voice responses
- LLM-powered chat interactions
- WebSocket-based real-time updates
- Comprehensive command system
- Message queue for rate limiting
- Robust error handling and logging

## Components

### Bot Core
- TwitchIO-based bot implementation
- Asynchronous message processing
- Background task management
- Resource cleanup handling
- OAuth token management

### Message Parser
- Intelligent message analysis
- Command detection
- User mention tracking
- Emote handling
- Question detection
- Context-aware response triggering

### Command Handlers
- Modular command system
- TTS command support
- Custom command registration
- Permission management
- Error recovery

### Configuration
- Environment-based configuration
- Twitch API settings
- Logging configuration
- Service integration settings

## Installation

1. Install the required packages:
```bash
pip install -r ../../requirements.txt
```

2. Requirements:
   - Python 3.7 or later
   - Twitch Developer Application
   - Running TTS service
   - Running LLM service
   - Valid Twitch account

## Configuration

Set up the required environment variables:

```bash
# Twitch Configuration
export TWITCH_CLIENT_ID="your_client_id"
export TWITCH_CLIENT_SECRET="your_client_secret"
export TWITCH_BOT_USERNAME="your_bot_username"
export TWITCH_CHANNEL="your_channel"

# API Configuration
export API_HOST="0.0.0.0"
export API_PORT="8000"
export API_DEBUG="true"
```

## Usage

### Starting the Bot

1. Run the bot service:
```bash
python -m twitch_bot
```

2. Open the web interface:
```
http://localhost:8000
```

3. Click "Authenticate with Twitch" and follow the OAuth flow

### Available Commands

- `!tts <text>` - Generate TTS for the specified text
- More commands can be added through the command handler system

### WebSocket Events

Connect to the WebSocket endpoint to receive real-time updates:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

## API Endpoints

### GET /
Web interface for bot management

### GET /auth/login
Start the Twitch OAuth flow

### GET /auth/callback
OAuth callback handler

### GET /auth/refresh
Refresh the OAuth token

### GET /status
Get bot status information

### WebSocket /ws
Real-time event updates

## Integration

### TTS Service Integration
```python
from tts_service.tts_engine import TTSEngine, AudioConfig

# Initialize TTS
tts_config = AudioConfig(...)
tts_engine = TTSEngine(config=tts_config)
```

### LLM Service Integration
```python
from llm_service.llm_client import LLMClient

# Initialize LLM client
llm_client = LLMClient()
response = await llm_client.get_response(message)
```

## Error Handling

The service includes comprehensive error handling:
- OAuth error recovery
- Service connection retries
- Message processing errors
- Command execution errors
- WebSocket connection handling

## Performance Features

1. Message Queue
   - Rate limiting
   - Async processing
   - Error recovery

2. Background Tasks
   - Service initialization
   - Token refresh
   - Resource cleanup

3. Connection Management
   - WebSocket connection pool
   - Service connection monitoring
   - Auto-reconnection

## Testing

Run the test suite:
```bash
pytest tests/
```

The test suite includes:
- Bot initialization tests
- Message parsing tests
- Command handling tests
- OAuth flow tests
- Integration tests

## Contributing

When contributing, please:
1. Add tests for new functionality
2. Ensure all tests pass
3. Follow the existing code style
4. Update documentation as needed

## License

This project is licensed under the MIT License. 