import os
import torch
import time
import sounddevice as sd
import numpy as np
from TTS.api import TTS
from TTS.config.shared_configs import BaseAudioConfig
from TTS.utils.generic_utils import get_user_data_dir
from pathlib import Path
import logging
import asyncio
from typing import Optional, List, Dict
from dataclasses import dataclass
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class AudioConfig:
    """Configuration for audio processing."""
    sample_rate: int
    device_index: int
    cache_dir: Path
    model_name: str

class AudioCache:
    """Handles caching of generated audio data."""
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_key(self, text: str) -> str:
        """Generate a unique cache key for the text."""
        return hashlib.md5(text.encode()).hexdigest()
    
    def get_cached_audio(self, text: str) -> Optional[np.ndarray]:
        """Retrieve cached audio if available."""
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.npy"
        
        if cache_file.exists():
            try:
                return np.load(cache_file)
            except Exception as e:
                logger.error(f"Error loading cached audio: {e}")
                return None
        return None
    
    def cache_audio(self, text: str, audio_data: np.ndarray) -> None:
        """Cache generated audio data."""
        try:
            cache_key = self._get_cache_key(text)
            cache_file = self.cache_dir / f"{cache_key}.npy"
            np.save(cache_file, audio_data)
        except Exception as e:
            logger.error(f"Error caching audio: {e}")

class AudioProcessor:
    """Handles audio processing and normalization."""
    @staticmethod
    def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio data to prevent clipping."""
        if audio_data.max() > 1.0 or audio_data.min() < -1.0:
            return audio_data / max(abs(audio_data.max()), abs(audio_data.min()))
        return audio_data
    
    @staticmethod
    def validate_audio(audio_data: np.ndarray) -> bool:
        """Validate audio data."""
        return (
            isinstance(audio_data, np.ndarray) 
            and audio_data.size > 0 
            and not np.isnan(audio_data).any()
        )

class AudioDeviceManager:
    """Manages audio device configuration and playback."""
    def __init__(self, sample_rate: int, device_index: int):
        self.sample_rate = sample_rate
        self.device_index = device_index
        self._setup_device()
    
    def _find_valid_device(self) -> int:
        """Find a valid output device."""
        try:
            devices = sd.query_devices()
            logger.debug(f"Available audio devices:\n{devices}")
            
            # First try the specified device
            if self.device_index < len(devices):
                device = devices[self.device_index]
                if device['max_output_channels'] > 0:
                    return self.device_index
            
            # If specified device is not valid, find the default output device
            default_device = sd.default.device[1]  # [1] is the default output device
            if default_device is not None and default_device < len(devices):
                device = devices[default_device]
                if device['max_output_channels'] > 0:
                    logger.info(f"Using default output device: {device['name']}")
                    return default_device
            
            # If no default device, find first valid output device
            for idx, device in enumerate(devices):
                if device['max_output_channels'] > 0:
                    logger.info(f"Using first available output device: {device['name']}")
                    return idx
            
            raise Exception("No valid output device found")
            
        except Exception as e:
            logger.error(f"Error finding valid audio device: {e}")
            raise
    
    def _setup_device(self) -> None:
        """Configure the audio device."""
        try:
            # Find valid output device
            self.device_index = self._find_valid_device()
            devices = sd.query_devices()
            device = devices[self.device_index]
            
            # Configure device settings
            sd.default.device = self.device_index
            sd.default.samplerate = self.sample_rate
            sd.default.channels = min(2, device['max_output_channels'])  # Use mono or stereo
            sd.default.dtype = np.float32
            
            logger.info(f"Configured audio device: {device['name']}")
            logger.info(f"Sample rate: {self.sample_rate}")
            logger.info(f"Channels: {sd.default.channels}")
            
        except Exception as e:
            logger.error(f"Error setting up audio device: {e}")
            raise
    
    async def play_audio(self, audio_data: np.ndarray) -> bool:
        """Play audio data asynchronously."""
        try:
            # Ensure audio data matches device configuration
            if len(audio_data.shape) == 1:
                # Convert mono to stereo if needed
                if sd.default.channels == 2:
                    audio_data = np.column_stack((audio_data, audio_data))
            
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                await loop.run_in_executor(
                    executor,
                    lambda: sd.play(audio_data, self.sample_rate)
                )
                await loop.run_in_executor(
                    executor,
                    sd.wait
                )
            return True
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False

class TTSEngine:
    """Main TTS engine class coordinating all components."""
    def __init__(self, config: AudioConfig):
        """
        Initialize the TTS Engine with all necessary components.
        
        Args:
            config (AudioConfig): Configuration for the TTS engine
        """
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Initialize components
        self._init_tts_model()
        self.audio_cache = AudioCache(config.cache_dir)
        self.audio_processor = AudioProcessor()
        self.device_manager = AudioDeviceManager(
            config.sample_rate,
            config.device_index
        )
        
    def _init_tts_model(self) -> None:
        """Initialize the TTS model."""
        try:
            self.tts = TTS(
                model_name=self.config.model_name,
                progress_bar=False
            ).to(self.device)
            
            if hasattr(self.tts, "speakers") and self.tts.speakers:
                self.speaker = self.tts.speakers[0]
            else:
                self.speaker = None
                
        except Exception as e:
            logger.error(f"Error initializing TTS model: {e}")
            raise
    
    def _generate_audio(self, text: str) -> Optional[np.ndarray]:
        """Generate audio for the given text."""
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided")
                return None
            
            # Check cache first
            cached_audio = self.audio_cache.get_cached_audio(text)
            if cached_audio is not None:
                logger.info("Using cached audio")
                return cached_audio
            
            # Generate new audio
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            if not sentences:
                sentences = [text]
            
            audio_segments = []
            for sentence in sentences:
                logger.debug(f"Generating audio for sentence: {sentence}")
                try:
                    wav = self.tts.tts(
                        text=sentence,
                        speaker=self.speaker if self.speaker else None
                    )
                    if wav is not None:
                        # Ensure audio is float32 and normalized
                        wav = np.array(wav, dtype=np.float32)
                        if wav.ndim == 2:  # If stereo, convert to mono
                            wav = wav.mean(axis=1)
                        audio_segments.append(wav)
                except Exception as e:
                    logger.error(f"Error generating audio for sentence: {e}")
                    continue
            
            if not audio_segments:
                return None
            
            # Concatenate and normalize
            final_audio = np.concatenate(audio_segments)
            final_audio = self.audio_processor.normalize_audio(final_audio)
            
            # Ensure proper shape (mono)
            if final_audio.ndim > 1:
                final_audio = final_audio.mean(axis=1)
            
            # Cache the generated audio
            self.audio_cache.cache_audio(text, final_audio)
            
            return final_audio
            
        except Exception as e:
            logger.exception(f"Error in audio generation: {e}")
            return None
    
    async def play_speech(self, text: str) -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text (str): Text to convert to speech
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Processing speech request: '{text}'")
            
            # Generate audio
            audio_data = self._generate_audio(text)
            if audio_data is None:
                logger.error("Failed to generate audio")
                return False
            
            # Validate audio data
            if not self.audio_processor.validate_audio(audio_data):
                logger.error("Invalid audio data generated")
                return False
            
            # Play audio
            return await self.device_manager.play_audio(audio_data)
            
        except Exception as e:
            logger.error(f"Error in play_speech: {e}")
            return False 