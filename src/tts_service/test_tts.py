import unittest
import asyncio
from tts_service.tts_engine import TTSEngine
import numpy as np
import logging
import scipy.io.wavfile
import sounddevice as sd
from unittest.mock import patch

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Changed to INFO to reduce noise
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='tts_engine.log'
)
logger = logging.getLogger(__name__)

class TestTTSEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        logger.info("Initializing TTS Engine for tests")
        cls.tts_engine = TTSEngine()

    def setUp(self):
        logger.info("Setting up test case")
        try:
            self.engine = TTSEngine()
        except Exception as e:
            logger.error(f"Failed to initialize TTSEngine: {e}")
            self.fail(f"TTSEngine initialization failed: {e}")

    def test_basic_tts(self):
        """Test basic TTS functionality."""
        logger.info("Testing basic TTS generation")
        text = "This is a test sentence."
        wav = self.engine.generate_speech_stream(text)
        self.assertIsNotNone(wav)
        self.assertTrue(isinstance(wav, np.ndarray))
        self.assertTrue(wav.size > 0)

    # Comment out other tests temporarily
    # def test_generate_speech_stream_long_text(self):
    # ...
    #
    # def test_play_speech(self):
    # ...
    #
    # def test_invalid_input(self):
    # ...
    #
    # def test_audio_format(self):
    # ...

    def generate_audio_file(self, text, filename):
        """Generate an audio file from the given text."""
        logger.info(f"Generating audio file for text: {text}")
        try:
            audio_data = self.engine.generate_speech_stream(text)
            sample_rate = 22050  # Use the sample rate from your TTS engine
            scipy.io.wavfile.write(filename, sample_rate, audio_data)
            logger.info(f"Audio file saved as {filename}")
        except Exception as e:
            logger.error(f"Failed to generate audio file: {e}")
            raise

    async def async_test_play_speech(self):
        """Helper method to run play_speech asynchronously."""
        test_text = "OH MAN, TALKING ANIME NOW?! :eyes: That's like asking me to choose my fave pizza topping, redblazin"
        logger.info(f"Testing play_speech with text: {test_text}")
        
        # Create a flag to track if audio was generated
        audio_generated = False
        
        try:
            # Generate and play the audio
            audio_data = self.engine.generate_speech_stream(test_text)
            if audio_data is not None and len(audio_data) > 0:
                audio_generated = True
                await self.engine.play_speech(test_text)
                # Wait for audio to finish playing
                await asyncio.sleep(3)
            
            logger.info(f"Audio generation completed. Audio generated: {audio_generated}")
            return audio_generated
            
        except Exception as e:
            logger.error(f"Error during play_speech test: {e}")
            raise

    def test_play_speech(self):
        """Test that play_speech generates and attempts to play audio."""
        logger.info("Starting play_speech test")
        
        try:
            # Run the async test
            audio_generated = asyncio.run(self.async_test_play_speech())
            
            # Verify audio was generated
            self.assertTrue(audio_generated, "No audio was generated during play_speech")
            logger.info("play_speech test completed successfully")
            
        except Exception as e:
            logger.error(f"play_speech test failed: {e}")
            raise

    def test_generate_audio_file(self):
        """Test the generation of an audio file."""
        logger.info("Testing audio file generation")
        try:
            self.generate_audio_file("Hello, this is a test.", "test_output.wav")
            logger.info("Audio file generation test completed successfully")
        except Exception as e:
            logger.error(f"Audio file generation test failed: {e}")
            raise

    @classmethod
    def tearDownClass(cls):
        logger.info("TTS tests completed.")

if __name__ == '__main__':
    unittest.main() 