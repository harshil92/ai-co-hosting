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

# --- Corrected Logging Setup ---
log_file_path = Path.home() / "tts_engine.log"  # Use user's home directory
try:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )
except Exception as e:
    print(f"Error setting up logging: {e}") # Fallback if logging setup fails

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Ensure the logger uses DEBUG level

class TTSEngine:
    def __init__(self, model_name="tts_models/en/ljspeech/vits"):
        """
        Initialize the TTS Engine with Coqui TTS.
        
        Args:
            model_name (str): Name of the TTS model to use
        """
        self.device = "cpu"
        logger.info(f"Using device: {self.device}")

        try:
            logger.info(f"Initializing TTS with model: {model_name}")
            self.tts = TTS(model_name=model_name, progress_bar=False).to(self.device)
            logger.info("TTS model initialized successfully")
            logger.info(f"Model loaded on device: {self.device}")

            if hasattr(self.tts, "speakers") and self.tts.speakers:
                logger.info(f"Available speakers: {self.tts.speakers}")
                self.speaker = self.tts.speakers[0]
            else:
                self.speaker = None

        except Exception as e:
            logger.error(f"Error initializing TTS model: {e}")
            raise

        self.sample_rate = self.tts.synthesizer.output_sample_rate
        
        # Audio device setup
        try:
            desired_device_index = 8  # REPLACE WITH YOUR DESIRED DEVICE INDEX
            devices = sd.query_devices()
            logger.info(f"Using audio output device: {devices[desired_device_index]['name']}")
            logger.debug(f"Available audio devices:\n{devices}")
            
            sd.default.samplerate = self.sample_rate
            sd.default.device = desired_device_index
            
        except Exception as e:
            logger.error(f"Error querying or setting audio device: {e}")

    def _generate_audio(self, text):
        try:
            if text is None or not text.strip():
                logger.warning("Input text is empty or None. Returning None.")
                return None

            sentences = [s.strip() for s in text.split('.') if s.strip()]
            if not sentences:
                sentences = [text]
            
            audio_segments = []
            for sentence in sentences:
                logger.debug(f"Generating audio for sentence: {sentence}")
                try:
                    if self.speaker:
                        wav = self.tts.tts(text=sentence, speaker=self.speaker)
                    else:
                        wav = self.tts.tts(text=sentence)
                    
                    if wav is not None:
                        wav = np.array(wav, dtype=np.float32)
                        audio_segments.append(wav)
                    else:
                        logger.error(f"TTS returned None for sentence: {sentence}")
                except Exception as e:
                    logger.error(f"Error generating audio for sentence '{sentence}': {e}")
                    continue
            
            if not audio_segments:
                logger.error("No valid audio segments generated.")
                return None
            
            final_audio = np.concatenate(audio_segments)
            
            if final_audio.size > 0:
                if final_audio.max() > 1.0 or final_audio.min() < -1.0:
                    final_audio = final_audio / max(abs(final_audio.max()), abs(final_audio.min()))
                return final_audio
            else:
                logger.error("Generated audio is empty")
                return None
            
        except Exception as e:
            logger.exception(f"Error generating audio: {e}")
            return None
            
    def generate_speech_stream(self, text):
        """
        Convert text to speech and return the audio data directly.
        
        Args:
            text (str): Text to convert to speech
            
        Returns:
            numpy.ndarray: Audio data as a numpy array
        """
        try:
            logger.info(f"Generating speech stream for text: '{text}'")
            wav = self._generate_audio(text)
            
            if wav is None:
                logger.error("Failed to generate audio - _generate_audio returned None")
                raise Exception("Failed to generate audio")
                
            logger.info(f"Speech stream generated successfully: shape={wav.shape}, dtype={wav.dtype}")
            return wav
        except Exception as e:
            logger.error(f"Error generating speech stream: {e}")
            raise
    
    async def play_speech(self, text: str) -> bool:
        """Play speech for the given text."""
        try:
            logger.info(f"Starting speech generation for text: '{text}'")
            
            # Generate speech stream
            audio_data = self.generate_speech_stream(text)
            if audio_data is None:
                logger.error("Failed to generate audio data")
                return False
            
            # Ensure audio data is valid
            if not isinstance(audio_data, np.ndarray) or audio_data.size == 0:
                logger.error("Invalid audio data generated")
                return False

            # Ensure audio data is float32
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            # Normalize audio if needed
            if audio_data.max() > 1.0 or audio_data.min() < -1.0:
                audio_data = audio_data / max(abs(audio_data.max()), abs(audio_data.min()))

            # Log audio data properties
            logger.info(f"Generated audio data: shape={audio_data.shape}, dtype={audio_data.dtype}, "
                       f"range=[{audio_data.min():.2f}, {audio_data.max():.2f}]")

            # Play the audio
            sd.play(audio_data, self.sample_rate)
            logger.info("Audio playback started")
            sd.wait()  # Wait for playback to finish
            logger.info("Audio playback completed")
            return True
        
        except Exception as e:
            logger.error(f"Error in play_speech: {e}")
            return False 