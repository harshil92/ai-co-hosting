"""Twitch bot implementation using FastAPI and TwitchIO."""
from fastapi import FastAPI, WebSocket, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from twitchio.ext import commands
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging
from twitch_bot.config import settings
from twitch_bot.message_parser import MessageParser
from twitch_bot.llm_client import LLMClient
from tts_service.tts_engine import TTSEngine
from tts_service.config import DEFAULT_LANGUAGE

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Co-Host Twitch Bot")
connected_clients: List[WebSocket] = []

# Store the bot instance
bot_instance: Optional['Bot'] = None
access_token: Optional[str] = None
refresh_token: Optional[str] = None

def get_html_template(status: str, channel: str) -> str:
    """Get the HTML template with the current status."""
    return f"""
    <html>
        <head>
            <title>AI Co-Host Twitch Bot</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    max-width: 800px; 
                    margin: 40px auto; 
                    padding: 0 20px; 
                    line-height: 1.6; 
                }}
                .button {{ 
                    display: inline-block; 
                    padding: 10px 20px; 
                    background-color: #9146FF; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                }}
                .warning {{ 
                    color: #e74c3c; 
                }}
                .code {{ 
                    background: #f8f9fa; 
                    padding: 2px 5px; 
                    border-radius: 3px; 
                    font-family: monospace; 
                }}
            </style>
        </head>
        <body>
            <h1>AI Co-Host Twitch Bot</h1>
            
            <h2>Current Status</h2>
            <p>Bot Status: <span class="code">{status}</span></p>
            <p>Channel: <span class="code">{channel}</span></p>
            
            <h2>Setup Instructions</h2>
            <ol>
                <li>Make sure you have set all required environment variables:
                    <ul>
                        <li>TWITCH_CLIENT_ID</li>
                        <li>TWITCH_CLIENT_SECRET</li>
                        <li>TWITCH_CHANNEL</li>
                        <li>TWITCH_BOT_USERNAME</li>
                    </ul>
                </li>
                <li>Click the button below to authenticate with Twitch</li>
                <li>Log in with your bot account (not your main streaming account)</li>
                <li>Authorize the application</li>
            </ol>
            
            <p><a href="/auth/login" class="button">Authenticate with Twitch</a></p>
            
            <h2>Troubleshooting</h2>
            <p>If you encounter any issues:</p>
            <ol>
                <li>Check if all environment variables are set correctly</li>
                <li>Make sure your Twitch Application is properly configured at <a href="https://dev.twitch.tv/console">Twitch Developer Console</a></li>
                <li>Verify that <span class="code">http://localhost:8000/auth/callback</span> is added as an OAuth Redirect URL</li>
            </ol>
            
            <p class="warning">Note: Always authenticate using the button above. Do not access the callback URL directly.</p>
        </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with instructions."""
    return get_html_template(
        status="Online" if bot_instance else "Waiting for Authentication",
        channel=settings.TWITCH_CHANNEL or "Not Set"
    )

class Bot(commands.Bot):
    def __init__(self, access_token: str):
        """Initialize the bot with the given access token."""
        # Validate settings
        settings.validate_twitch_settings()
        
        logger.info(f"Initializing bot for channel: {settings.TWITCH_CHANNEL}")
        
        super().__init__(
            token=access_token,
            client_id=settings.TWITCH_CLIENT_ID,
            nick=settings.TWITCH_BOT_USERNAME,
            prefix="!",
            initial_channels=[settings.TWITCH_CHANNEL]
        )
        self.channel = settings.TWITCH_CHANNEL
        self.message_parser = MessageParser(settings.TWITCH_BOT_USERNAME)
        self.llm_client = LLMClient()
        self.tts_engine = None
        self.is_responding = False
        self.current_language = DEFAULT_LANGUAGE
        
        # Initialize TTS in background task
        asyncio.create_task(self._initialize_tts())

    async def stop(self):
        """Stops the bot and cleans up resources."""
        logger.info("Stopping the bot...")
        await self.cleanup()  # Ensure TTS and other resources are cleaned up
        if self.loop:
            self.loop.stop()  # Stop the TwitchIO bot's internal loop
        logger.info("Bot stopped.")
        
    async def _initialize_tts(self, max_retries=3, retry_delay=5):
        """Initialize TTS engine with retry logic."""
        if self.tts_engine is not None:
            logger.debug("TTS engine already initialized")
            return True
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to initialize TTS engine (attempt {attempt + 1}/{max_retries})")
                self.tts_engine = TTSEngine()
                
                # Test the TTS engine with an actual test phrase
                test_text = "TTS system initialization test."
                logger.info(f"Testing TTS with text: '{test_text}'")
                
                # Generate and play test audio
                test_wav = self.tts_engine.generate_speech_stream(test_text)
                if test_wav is not None:
                    logger.info("Generated test audio successfully, attempting playback")
                    try:
                        await self.tts_engine.play_speech(test_text)
                        logger.info("TTS engine initialized and tested successfully with audio playback")
                        return True
                    except Exception as e:
                        logger.error(f"Failed to play test audio: {e}")
                        raise
                else:
                    raise Exception("TTS engine failed to generate test audio")
                
            except Exception as e:
                logger.error(f"Failed to initialize TTS engine (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error("Failed to initialize TTS engine after all retries")
                    self.tts_engine = None
                    return False

    async def _ensure_tts_available(self):
        """Ensure TTS engine is available, attempting to reinitialize if needed."""
        if self.tts_engine is None:
            logger.info("TTS engine not available, attempting to initialize")
            await self._initialize_tts(max_retries=1)
        return self.tts_engine is not None

    async def broadcast_message(self, message: Dict):
        """Broadcast message to all connected WebSocket clients."""
        for client in connected_clients:
            try:
                await client.send_json(message)
            except:
                connected_clients.remove(client)

    async def event_ready(self):
        """Called once when the bot goes online."""
        logger.info(f"Bot is ready! Connected as: {self.nick}")
        await self.broadcast_message({
            "type": "status",
            "content": "Bot connected to Twitch chat",
            "timestamp": datetime.now().isoformat()
        })

    async def _play_tts_response(self, text: str):
        """
        Play TTS response.
        
        Args:
            text (str): Text to speak
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for TTS")
            return False

        if not await self._ensure_tts_available():
            logger.warning("TTS engine not available and could not be initialized")
            return False

        try:
            # Clean up the text - remove emotes and special characters
            cleaned_text = ' '.join(word for word in text.split() if not (word.startswith(':') and word.endswith(':')))
            if not cleaned_text.strip():
                logger.warning("No text left after cleaning")
                return False
            
            logger.info(f"Playing TTS for cleaned text: '{cleaned_text}'")

            # Play the speech
            success = await self.tts_engine.play_speech(cleaned_text)
            if not success:
                logger.error("Failed to play speech")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error playing TTS: {e}")
            # Only reinitialize if it's a critical error
            if "not initialized" in str(e).lower() or "device" in str(e).lower():
                logger.info("Critical TTS error, attempting to reinitialize")
                self.tts_engine = None
                asyncio.create_task(self._initialize_tts())
            return False

    async def event_message(self, message):
        """Called when a message is received in the Twitch chat."""
        if message.echo:
            return

        # Create message data
        msg_data = {
            "type": "chat_message",
            "content": message.content,
            "author": message.author.name,
            "timestamp": datetime.now().isoformat()
        }
        
        # Parse the message
        parsed_message = self.message_parser.parse_message(msg_data)
        if parsed_message:
            # Format for dialogue engine
            dialogue_message = self.message_parser.format_for_dialogue(parsed_message)
            
            # Add parsed data to broadcast
            msg_data.update({
                "parsed_data": {
                    "is_question": parsed_message.is_question,
                    "addressed_to_bot": parsed_message.addressed_to_bot,
                    "mentioned_users": parsed_message.mentioned_users,
                    "emotes": parsed_message.emotes
                }
            })
            
            # Log parsed message details
            logger.debug(f"Parsed message: {dialogue_message}")
            
            # Generate and send response if message is addressed to bot
            if not parsed_message.addressed_to_bot and not self.is_responding:
                try:
                    self.is_responding = True  # Prevent multiple simultaneous responses
                    
                    # Check if LLM service is available
                    if await self.llm_client.is_available():
                        # Generate response
                        response = await self.llm_client.generate_response(
                            username=message.author.name,
                            message=message.content
                        )
                        
                        if response:
                            # Extract the response text
                            response_text = response.get('response', '') if isinstance(response, dict) else response
                            
                            # Send response to chat first
                            await message.channel.send(response_text)
                            
                            # Play the response using TTS
                            tts_success = await self._play_tts_response(response_text)
                            
                            if not tts_success:
                                logger.warning(f"Failed to play TTS for response: {response_text}")
                            
                            # Broadcast response with TTS status
                            await self.broadcast_message({
                                "type": "bot_response",
                                "content": response_text,
                                "tts_played": tts_success,
                                "timestamp": datetime.now().isoformat()
                            })
                        else:
                            logger.error("Failed to generate response")
                    else:
                        logger.error("LLM service is not available")
                    
                except Exception as e:
                    logger.error(f"Error generating/sending response: {e}")
                finally:
                    self.is_responding = False
        
        # Broadcast to WebSocket clients
        await self.broadcast_message(msg_data)
        
        # Handle commands
        await self.handle_commands(message)

    @commands.command(name="tts")
    async def tts_command(self, ctx, *, text: str = None):
        """Command to test TTS with specific text."""
        if not text:
            await ctx.send("Please provide text to speak.")
            return
            
        if not self.tts_engine:
            await ctx.send("TTS is not available.")
            return
            
        try:
            await self._play_tts_response(text)
            await ctx.send("TTS test completed.")
        except Exception as e:
            await ctx.send(f"TTS test failed: {str(e)}")

    async def cleanup(self):
        """Cleanup bot resources."""
        if self.tts_engine:
            try:
                # Add cleanup method to TTSEngine class if needed
                await self.tts_engine.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up TTS engine: {e}")
            self.tts_engine = None

@app.get("/auth/login")
async def auth_login():
    """Start the OAuth flow by redirecting to Twitch."""
    oauth_url = settings.get_oauth_url()
    logger.debug(f"Redirecting to Twitch OAuth URL: {oauth_url}")
    return RedirectResponse(oauth_url)

@app.get("/auth/callback")
async def auth_callback(code: str = None, error: str = None, error_description: str = None):
    """Handle the OAuth callback from Twitch."""
    global bot_instance, access_token, refresh_token
    
    logger.debug(f"Received callback - code: {'present' if code else 'missing'}, error: {error}")
    
    if error:
        error_msg = f"Auth error: {error} - {error_description}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code provided")
    
    try:
        # Exchange the code for tokens
        token_data = settings.exchange_code_for_token(code)
        logger.debug("Successfully exchanged code for token")
        
        access_token = token_data['access_token']
        refresh_token = token_data.get('refresh_token')
        
        # Initialize the bot with the new token
        if bot_instance:
            logger.debug("Shutting down existing bot instance")
            # TODO: Implement proper bot shutdown
            pass
            
        logger.debug("Initializing new bot instance")
        bot_instance = Bot(access_token=access_token)
        asyncio.create_task(bot_instance.start())
        
        return {"message": "Authentication successful! You can close this window."}
        
    except Exception as e:
        logger.exception("Failed to authenticate")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/auth/refresh")
async def auth_refresh():
    """Refresh the access token using the refresh token."""
    global access_token, refresh_token, bot_instance
    
    if not refresh_token:
        raise HTTPException(status_code=400, detail="No refresh token available")
        
    try:
        token_data = settings.refresh_access_token(refresh_token)
        access_token = token_data['access_token']
        refresh_token = token_data.get('refresh_token', refresh_token)
        
        # Reinitialize the bot with the new token
        if bot_instance:
            # TODO: Implement proper bot shutdown
            pass
            
        bot_instance = Bot(access_token=access_token)
        asyncio.create_task(bot_instance.start())
        
        return {"message": "Token refreshed successfully"}
        
    except Exception as e:
        logger.error(f"Failed to refresh token: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except:
        connected_clients.remove(websocket)

@app.get("/status")
async def get_status():
    """Get the current status of the bot."""
    return {
        "status": "online" if bot_instance else "waiting_for_auth",
        "channel": settings.TWITCH_CHANNEL,
        "connected_clients": len(connected_clients),
        "authenticated": bool(access_token)
    }
