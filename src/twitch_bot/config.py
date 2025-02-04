"""Configuration management for the AI Co-host Twitch Bot."""
from pydantic_settings import BaseSettings
import os
import requests
from typing import Optional
import logging
from urllib.parse import urlencode

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Twitch OAuth scopes needed for the bot
REQUIRED_SCOPES = [
    'chat:read',
    'chat:edit',
    'channel:moderate',
    'channel:read:redemptions'
]

class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Twitch Configuration
    TWITCH_CLIENT_ID: Optional[str] = None
    TWITCH_CLIENT_SECRET: Optional[str] = None
    TWITCH_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    TWITCH_BOT_USERNAME: Optional[str] = None
    TWITCH_CHANNEL: Optional[str] = None
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    def validate_twitch_settings(self):
        """Validate that all required Twitch settings are present."""
        missing = []
        if not self.TWITCH_CLIENT_ID:
            missing.append("TWITCH_CLIENT_ID")
        if not self.TWITCH_CLIENT_SECRET:
            missing.append("TWITCH_CLIENT_SECRET")
        if not self.TWITCH_CHANNEL:
            missing.append("TWITCH_CHANNEL")
        if not self.TWITCH_BOT_USERNAME:
            missing.append("TWITCH_BOT_USERNAME")
        
        # Log current settings (masking sensitive data)
        logger.debug(f"Current settings:")
        logger.debug(f"TWITCH_CLIENT_ID: {'present' if self.TWITCH_CLIENT_ID else 'missing'}")
        logger.debug(f"TWITCH_CLIENT_SECRET: {'present' if self.TWITCH_CLIENT_SECRET else 'missing'}")
        logger.debug(f"TWITCH_CHANNEL: {self.TWITCH_CHANNEL}")
        logger.debug(f"TWITCH_BOT_USERNAME: {self.TWITCH_BOT_USERNAME}")
        logger.debug(f"TWITCH_REDIRECT_URI: {self.TWITCH_REDIRECT_URI}")
        
        if missing:
            error_msg = (
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Please set these variables in your environment before running the application.\n"
                "In PowerShell, you can set them using:\n"
                f"$env:TWITCH_CLIENT_ID = 'your_client_id'\n"
                f"$env:TWITCH_CLIENT_SECRET = 'your_client_secret'\n"
                f"$env:TWITCH_CHANNEL = 'your_channel_name'\n"
                f"$env:TWITCH_BOT_USERNAME = 'your_bot_username'\n\n"
                "You can get your client ID and secret from https://dev.twitch.tv/console\n"
                "Make sure to:\n"
                "1. Register your application at https://dev.twitch.tv/console\n"
                "2. Add 'http://localhost:8000/auth/callback' as an OAuth Redirect URL\n"
                "3. Copy the Client ID and Client Secret"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

    def get_oauth_url(self) -> str:
        """Get the Twitch OAuth authorization URL."""
        self.validate_twitch_settings()
        
        params = {
            'client_id': self.TWITCH_CLIENT_ID,
            'redirect_uri': self.TWITCH_REDIRECT_URI,
            'response_type': 'code',
            'scope': ' '.join(REQUIRED_SCOPES),
            'force_verify': 'true'
        }
        url = f'https://id.twitch.tv/oauth2/authorize?{urlencode(params)}'
        logger.debug(f"Generated OAuth URL (client_id and sensitive data masked): {url.replace(self.TWITCH_CLIENT_ID, 'CLIENT_ID')}")
        return url

    def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token.
        
        Args:
            code: The authorization code from Twitch OAuth redirect
            
        Returns:
            dict: Token response containing access_token, refresh_token, etc.
            
        Raises:
            requests.RequestException: If the token request fails
        """
        response = requests.post(
            'https://id.twitch.tv/oauth2/token',
            data={
                'client_id': self.TWITCH_CLIENT_ID,
                'client_secret': self.TWITCH_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.TWITCH_REDIRECT_URI
            }
        )
        
        if response.status_code != 200:
            raise requests.RequestException(
                f"Failed to get access token: {response.status_code} - {response.text}"
            )
            
        return response.json()

    def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh an expired access token.
        
        Args:
            refresh_token: The refresh token from the original OAuth flow
            
        Returns:
            dict: Token response containing new access_token, refresh_token, etc.
            
        Raises:
            requests.RequestException: If the token refresh fails
        """
        response = requests.post(
            'https://id.twitch.tv/oauth2/token',
            data={
                'client_id': self.TWITCH_CLIENT_ID,
                'client_secret': self.TWITCH_CLIENT_SECRET,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
        )
        
        if response.status_code != 200:
            raise requests.RequestException(
                f"Failed to refresh token: {response.status_code} - {response.text}"
            )
            
        return response.json()

    class Config:
        """Pydantic configuration class."""
        env_file = None  # Disable .env file loading

# Initialize settings
settings = Settings(
    TWITCH_CLIENT_ID=os.environ.get("TWITCH_CLIENT_ID"),
    TWITCH_CLIENT_SECRET=os.environ.get("TWITCH_CLIENT_SECRET"),
    TWITCH_CHANNEL=os.environ.get("TWITCH_CHANNEL"),
    TWITCH_BOT_USERNAME=os.environ.get("TWITCH_BOT_USERNAME")
) 