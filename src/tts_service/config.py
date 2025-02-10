"""
Configuration settings for the TTS service.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# TTS Model settings
TTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"  # XTTS-v2 model
USE_CUDA = True  # Will be automatically disabled if CUDA is not available
DEFAULT_LANGUAGE = "en"  # Default language for TTS

# Audio settings
SAMPLE_RATE = 24000  # Hz (XTTS-v2 uses 24kHz)
OUTPUT_FORMAT = "wav"
AUDIO_DIR = "output/audio"

# Performance settings
BATCH_SIZE = 1
MAX_WAV_VALUE = 32768.0

# Cache settings
ENABLE_CACHE = True
CACHE_DIR = "cache/tts"
MAX_CACHE_SIZE = 1000  # Maximum number of cached audio files

# Voice settings
DEFAULT_SPEAKER = os.getenv("TTS_DEFAULT_SPEAKER", None)  # Can be set via environment variable
CUSTOM_VOICE_DIR = os.getenv("TTS_CUSTOM_VOICE_DIR", "voices")  # Directory for custom voice files

# Create necessary directories
for directory in [AUDIO_DIR, CACHE_DIR, CUSTOM_VOICE_DIR]:
    Path(directory).mkdir(parents=True, exist_ok=True) 