# TTS Service

This service provides Text-to-Speech functionality using Coqui-AI's XTTS-v2 model.

## Features

- High-quality speech synthesis using XTTS-v2
- Multi-language support (16 languages)
- Real-time audio streaming
- Sentence-level processing for better quality
- Configurable audio settings
- Comprehensive error handling and logging

## Supported Languages

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Polish (pl)
- Turkish (tr)
- Russian (ru)
- Dutch (nl)
- Czech (cs)
- Arabic (ar)
- Chinese (zh-cn)
- Japanese (ja)
- Hungarian (hu)
- Korean (ko)

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Make sure you have Python 3.7 or later installed.

## Configuration

The service can be configured through environment variables or the `config.py` file:

- `TTS_DEFAULT_SPEAKER`: Set a default speaker voice
- `TTS_CUSTOM_VOICE_DIR`: Directory for custom voice files
- Other settings available in `config.py`

## Usage

```python
from tts_engine import TTSEngine

# Initialize the engine
engine = TTSEngine()

# Generate and play speech
await engine.play_speech("Hello, this is a test!")

# Generate speech file
output_path = engine.generate_speech("Save this to a file", "output.wav")

# Change language
engine.language = "es"  # Switch to Spanish
await engine.play_speech("¡Hola mundo!")
```

## Testing

Run the test suite:
```bash
python test_tts.py
```

## Error Handling

The service includes comprehensive error handling and logging. Check the logs for detailed information about any issues.

## Contributing

Feel free to submit issues and pull requests.

## License

This project is licensed under the same terms as Coqui-AI's XTTS-v2 model. 