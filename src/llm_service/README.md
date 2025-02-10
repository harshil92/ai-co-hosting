# LLM Service

This service provides a FastAPI-based REST API for interacting with Large Language Models through LM Studio, with advanced dialogue management and context handling.

## Features

- FastAPI-based REST API for LLM interactions
- Intelligent dialogue management with context tracking
- Response caching for improved performance
- Comprehensive error handling and logging
- Automatic response cleaning and formatting
- Real-time conversation topic tracking
- Asynchronous request handling

## Components

### API Server
- FastAPI-based REST endpoints
- Health check monitoring
- Conversation context management
- Request validation using Pydantic models
- Proper lifecycle management

### DialogueManager
- Maintains conversation context and history
- Tracks current topics and metadata
- Manages system prompts
- Implements context windowing
- Handles message formatting

### LMStudioClient
- Asynchronous communication with LM Studio
- Response caching with TTL
- Intelligent response cleaning
- Error handling and retries
- Connection pooling with aiohttp

## Installation

1. Install the required packages:
```bash
pip install -r ../../requirements.txt
```

2. Requirements:
   - Python 3.7 or later
   - Running LM Studio instance
   - FastAPI and uvicorn
   - aiohttp for async operations

## Configuration

The service can be configured through environment variables and initialization parameters:

```python
from llm_service.llm_client import LMStudioClient
from llm_service.dialogue_manager import DialogueManager

# Initialize LLM client
client = LMStudioClient(
    base_url="http://localhost:1234/v1",  # LM Studio endpoint
    cache_ttl=3600  # Cache timeout in seconds
)

# Initialize dialogue manager
dialogue_manager = DialogueManager(client)
```

## API Endpoints

### POST /chat
Generate a response to a chat message:
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"username": "user", "message": "Hello!", "emotes": []}'
```

### GET /context
Get current conversation context:
```bash
curl "http://localhost:8000/context"
```

### DELETE /context
Clear conversation context:
```bash
curl -X DELETE "http://localhost:8000/context"
```

### GET /health
Check service health:
```bash
curl "http://localhost:8000/health"
```

## Usage Examples

### Basic Usage
```python
from llm_service.llm_client import LMStudioClient

async with LMStudioClient() as client:
    response = await client.get_response("Hello, how are you?")
    print(response)
```

### With Dialogue Management
```python
from llm_service.dialogue_manager import DialogueManager
from llm_service.llm_client import LMStudioClient

client = LMStudioClient()
manager = DialogueManager(client)

# Add a message to the conversation
manager.add_message(
    username="user123",
    message="What's your favorite game?",
    emotes=["PogChamp"]
)

# Generate a response
response = await manager.generate_response()
print(response)
```

## Error Handling

The service includes comprehensive error handling:
- API endpoint validation
- LLM connection issues
- Response generation failures
- Context management errors
- Cache handling errors

## Performance Features

1. Response Caching
   - In-memory cache with TTL
   - Cache key generation based on input
   - Automatic cache cleanup

2. Connection Management
   - Connection pooling with aiohttp
   - Automatic retry logic
   - Timeout handling

3. Response Processing
   - Intelligent response cleaning
   - Internal monologue removal
   - Format standardization

## Testing

Run the test suite:
```bash
pytest test_api.py
```

The test suite includes:
- API endpoint testing
- Dialogue management testing
- LLM client testing
- Error handling scenarios
- Cache functionality

## Contributing

When contributing, please:
1. Add tests for new functionality
2. Ensure all tests pass
3. Follow the existing code style
4. Update documentation as needed

## License

This project is licensed under the MIT License. 