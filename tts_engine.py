"""
tts_engine.py

Wrapper around Coqui TTS.api to generate pydub.AudioSegment objects.
"""
from TTS.api import TTS
from pydub import AudioSegment
import io
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

class TTSEngine:
    def __init__(self, model_name: str = None):
        """Initialize the TTS engine. If model_name is None, use the default installed model."""
        self.model_name = model_name
        self.tts = None
        self._load_model()

    def _load_model(self):
        try:
            if self.model_name:
                logger.info(f"Loading TTS model: {self.model_name}")
                self.tts = TTS(self.model_name)
            else:
                logger.info("Loading default TTS model")
                self.tts = TTS()
        except Exception as e:
            logger.exception("Failed to load TTS model")
            raise

    def list_speakers(self):
        try:
            speakers = getattr(self.tts, "speakers", None)
            if speakers is None:
                # Some models expose voices differently
                return []
            return speakers
        except Exception:
            return []

    def validate_speaker(self, speaker: str) -> bool:
        if not speaker:
            return False
        speakers = self.list_speakers()
        if not speakers:
            # cannot validate; assume valid
            return True
        return speaker in speakers

    def synthesize(self, text: str, speaker: str = None, sample_rate: int = 22050, **kwargs) -> AudioSegment:
        """Synthesize text to a pydub.AudioSegment.

        kwargs can contain: speed, volume, emotion/style, etc. These are model-dependent.
        """
        if not self.tts:
            self._load_model()

        # Validate speaker if possible
        if speaker and not self.validate_speaker(speaker):
            logger.error("Unknown speaker id: %s", speaker)
            raise ValueError(f"Unknown speaker id: {speaker}")

        # Use a temporary file to store the TTS output
        fd, out_wav = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        try:
            # TTS.api.tts_to_file supports speaker and other kwargs
            self.tts.tts_to_file(text=text, speaker=speaker, file_path=out_wav, **kwargs)
            seg = AudioSegment.from_file(out_wav)
            return seg
        finally:
            try:
                if os.path.exists(out_wav):
                    os.remove(out_wav)
            except Exception:
                pass
