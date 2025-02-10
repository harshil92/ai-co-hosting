import pytest
import numpy as np
from pathlib import Path
import sounddevice as sd
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from tts_engine import TTSEngine, AudioConfig, AudioCache, AudioProcessor, AudioDeviceManager

@pytest.fixture
def audio_config():
    return AudioConfig(
        sample_rate=22050,
        device_index=0,
        cache_dir=Path("./test_cache"),
        model_name="tts_models/en/ljspeech/vits"
    )

@pytest.fixture
def mock_tts():
    with patch('tts_engine.TTS') as mock:
        mock_instance = Mock()
        mock_instance.tts.return_value = np.zeros(22050, dtype=np.float32)
        mock_instance.speakers = None
        mock.return_value = mock_instance
        yield mock

@pytest.fixture
def audio_cache(tmp_path):
    cache_dir = tmp_path / "tts_cache"
    return AudioCache(cache_dir)

@pytest.fixture
def audio_processor():
    return AudioProcessor()

@pytest.fixture
def audio_device_manager():
    with patch('sounddevice.play'), patch('sounddevice.wait'):
        manager = AudioDeviceManager(22050, 0)
        yield manager

class TestAudioCache:
    def test_cache_creation(self, tmp_path):
        cache_dir = tmp_path / "tts_cache"
        cache = AudioCache(cache_dir)
        assert cache_dir.exists()
    
    def test_cache_audio(self, audio_cache):
        test_audio = np.zeros(22050, dtype=np.float32)
        audio_cache.cache_audio("test text", test_audio)
        cached = audio_cache.get_cached_audio("test text")
        assert np.array_equal(cached, test_audio)
    
    def test_invalid_cache(self, audio_cache):
        assert audio_cache.get_cached_audio("nonexistent") is None

class TestAudioProcessor:
    def test_normalize_audio(self, audio_processor):
        # Test audio that needs normalization
        audio = np.array([2.0, -3.0, 1.5], dtype=np.float32)
        normalized = audio_processor.normalize_audio(audio)
        assert np.max(np.abs(normalized)) <= 1.0
        
        # Test audio that doesn't need normalization
        audio = np.array([0.5, -0.3, 0.1], dtype=np.float32)
        normalized = audio_processor.normalize_audio(audio)
        assert np.array_equal(normalized, audio)
    
    def test_validate_audio(self, audio_processor):
        # Valid audio
        valid_audio = np.zeros(1000, dtype=np.float32)
        assert audio_processor.validate_audio(valid_audio)
        
        # Invalid cases
        assert not audio_processor.validate_audio(np.array([]))
        assert not audio_processor.validate_audio(np.array([np.nan]))

class TestAudioDeviceManager:
    @pytest.mark.asyncio
    async def test_play_audio(self, audio_device_manager):
        test_audio = np.zeros(22050, dtype=np.float32)
        success = await audio_device_manager.play_audio(test_audio)
        assert success

    def test_device_setup(self):
        with patch('sounddevice.query_devices') as mock_query:
            mock_query.return_value = [{
                'name': 'Test Device',
                'max_output_channels': 2
            }]
            manager = AudioDeviceManager(22050, 0)
            assert manager.sample_rate == 22050
            assert manager.device_index == 0

class TestTTSEngine:
    @pytest.fixture
    def tts_engine(self, audio_config, mock_tts):
        return TTSEngine(audio_config)
    
    def test_initialization(self, tts_engine):
        assert tts_engine.device in ["cuda", "cpu"]
        assert tts_engine.speaker is None
    
    @pytest.mark.asyncio
    async def test_play_speech(self, tts_engine):
        with patch.object(tts_engine.device_manager, 'play_audio', new_callable=AsyncMock) as mock_play:
            mock_play.return_value = True
            result = await tts_engine.play_speech("Test text")
            assert result
            mock_play.assert_called_once()
    
    def test_generate_audio_empty_text(self, tts_engine):
        assert tts_engine._generate_audio("") is None
        assert tts_engine._generate_audio("   ") is None
    
    def test_generate_audio_with_cache(self, tts_engine):
        # First generation
        audio1 = tts_engine._generate_audio("Test text")
        assert audio1 is not None
        
        # Should use cache
        with patch.object(tts_engine.tts, 'tts') as mock_tts:
            audio2 = tts_engine._generate_audio("Test text")
            assert not mock_tts.called
            assert np.array_equal(audio1, audio2)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, tts_engine):
        with patch.object(tts_engine, '_generate_audio', return_value=None):
            result = await tts_engine.play_speech("Test text")
            assert not result

if __name__ == '__main__':
    pytest.main([__file__]) 