"""Tests for the Twitch bot implementation."""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from twitch_bot.bot import Bot
from twitch_bot.command_handlers import CommandHandlers

# Mock environment variables for testing
TEST_ENV = {
    "TWITCH_CLIENT_ID": "test_client_id",
    "TWITCH_CLIENT_SECRET": "test_client_secret",
    "TWITCH_BOT_USERNAME": "test_bot",
    "TWITCH_CHANNEL": "test_channel",
}

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Automatically mock environment variables for all tests."""
    for key, value in TEST_ENV.items():
        monkeypatch.setenv(key, value)

@pytest.fixture
def mock_message():
    """Create a mock message for testing."""
    message = Mock()
    message.content = "Hello bot!"
    message.author = Mock()
    message.author.name = "test_user"
    message.channel = AsyncMock()
    return message

@pytest.fixture
async def bot():
    """Create a bot instance for testing."""
    with patch('twitch_bot.bot.settings') as mock_settings:
        # Set required attributes on mock settings
        mock_settings.TWITCH_CHANNEL = TEST_ENV["TWITCH_CHANNEL"]
        mock_settings.TWITCH_CLIENT_ID = TEST_ENV["TWITCH_CLIENT_ID"]
        mock_settings.TWITCH_BOT_USERNAME = TEST_ENV["TWITCH_BOT_USERNAME"]
        mock_settings.TWITCH_CLIENT_SECRET = TEST_ENV["TWITCH_CLIENT_SECRET"]
        
        # Mock the validate_twitch_settings method
        mock_settings.validate_twitch_settings = Mock(return_value=True)
        
        bot = Bot("test_token")
        
        # Mock LLM client and TTS engine
        bot.llm_client = AsyncMock()
        bot.tts_engine = AsyncMock()
        
        yield bot
        await bot.cleanup()

@pytest.mark.asyncio
async def test_message_queue_processing(bot, mock_message):
    """Test that messages are properly queued and processed."""
    # Add a message to the queue
    await bot.message_queue.put(mock_message)
    
    # Wait for message processing
    await asyncio.sleep(0.2)
    
    # Verify message was processed
    mock_message.channel.send.assert_called()

@pytest.mark.asyncio
async def test_tts_command(bot):
    """Test the TTS command handling."""
    ctx = AsyncMock()
    text = "Test TTS message"
    
    # Execute command
    await bot.tts_command(ctx, text=text)
    
    # Verify response was sent
    ctx.send.assert_called_with(f"Playing TTS: {text}")

@pytest.mark.asyncio
async def test_cleanup(bot):
    """Test that cleanup properly handles resources."""
    # Mock background tasks
    mock_task = AsyncMock()
    bot._background_tasks = [mock_task]
    
    # Execute cleanup
    await bot.cleanup()
    
    # Verify cleanup
    mock_task.cancel.assert_called_once()
    bot.tts_engine.cleanup.assert_called_once()

@pytest.mark.asyncio
async def test_event_ready(bot):
    """Test the event_ready handler."""
    # Mock broadcast_message
    bot.broadcast_message = AsyncMock()
    
    # Trigger event_ready
    await bot.event_ready()
    
    # Verify broadcast was called with correct status
    bot.broadcast_message.assert_called_once()
    call_args = bot.broadcast_message.call_args[0][0]
    assert call_args["type"] == "status"
    assert "Bot connected to Twitch chat" in call_args["content"]

@pytest.mark.asyncio
async def test_handle_message_with_response(bot, mock_message):
    """Test message handling when bot should respond."""
    # Mock dependencies
    bot.message_parser.should_respond = Mock(return_value=True)
    bot.llm_client.get_response = AsyncMock(return_value="Test response")
    bot._play_tts_response = AsyncMock()
    
    # Handle message
    await bot._handle_message(mock_message)
    
    # Verify response was sent
    mock_message.channel.send.assert_called_with("Test response")
    bot._play_tts_response.assert_called_with("Test response") 