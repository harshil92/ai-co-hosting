# TTS Service

This service provides Text-to-Speech functionality using Coqui TTS with advanced audio processing capabilities.

## Features

- High-quality speech synthesis using Coqui TTS
- Asynchronous audio playback with proper device management
- Intelligent audio device selection and configuration
- Audio caching for improved performance
- Comprehensive error handling and logging
- Automatic audio format conversion (mono/stereo)
- Robust audio normalization and validation

## Components

### TTSEngine
- Main coordinator for all TTS operations
- Manages model initialization and audio generation
- Handles text preprocessing and sentence splitting
- Supports both CPU and CUDA acceleration

### AudioDeviceManager
- Automatic audio device detection and configuration
- Fallback mechanisms for device selection
- Proper channel and sample rate management
- Asynchronous audio playback using ThreadPoolExecutor

### AudioCache
- Efficient caching of generated audio
- MD5-based cache key generation
- Persistent storage of audio data
- Automatic cache directory management

### AudioProcessor
- Audio normalization to prevent clipping
- Audio validation and quality checks
- Format conversion and channel management

## Installation

1. Install the required packages:
```bash
pip install -r ../../requirements.txt
```

2. Requirements:
   - Python 3.7 or later
   - CUDA-capable GPU (optional, for faster processing)
   - Working audio output device

## Configuration

The service can be configured through `AudioConfig`:

```python
from pathlib import Path
from tts_engine import TTSEngine, AudioConfig

config = AudioConfig(
    sample_rate=22050,          # Standard sample rate for TTS
    device_index=0,             # Audio device index (auto-detects best device)
    cache_dir=Path("./cache"),  # Directory for caching audio files
    model_name="tts_models/en/ljspeech/vits"  # TTS model to use
)

engine = TTSEngine(config)
```

## Usage

### Basic Usage
```python
# Initialize the engine with configuration
engine = TTSEngine(config)

# Generate and play speech
await engine.play_speech("Hello, this is a test!")
```

### Error Handling
The service includes comprehensive error handling:
- Audio device validation and fallback
- Cache error recovery
- Model initialization retry logic
- Proper cleanup on shutdown

### Logging
Detailed logging is available for:
- Audio device configuration
- TTS model initialization
- Cache operations
- Playback status
- Error conditions

## Testing

Run the test suite:
```bash
pytest test_tts.py
```

The test suite includes:
- Audio cache functionality
- Audio processing operations
- Device management
- TTS engine initialization
- Error handling scenarios

## Performance Considerations

1. Audio Caching
   - Frequently used phrases are cached
   - Cache uses MD5 hashing for efficient lookup
   - Automatic cache cleanup (TODO)

2. Device Management
   - Automatic selection of best available device
   - Proper channel configuration
   - Sample rate optimization

3. Memory Management
   - Efficient audio data handling
   - Proper resource cleanup
   - Asynchronous operations for better performance

## Contributing

When contributing, please:
1. Add tests for new functionality
2. Ensure all tests pass
3. Follow the existing code style
4. Update documentation as needed

## License

This project is licensed under the MIT License. Note that the TTS models may have their own licensing terms. 