"""
audio_utils.py

Utilities to manipulate pydub.AudioSegment audio: speed change, volume, pause insertion, merge, save.
"""
from pydub import AudioSegment
import os
import uuid
import logging
import math
import tempfile

logger = logging.getLogger(__name__)

def change_speed(sound: AudioSegment, speed: float) -> AudioSegment:
    if speed <= 0 or speed == 1.0:
        return sound
    # Change frame_rate to change speed, then set back
    new_frame_rate = int(sound.frame_rate * speed)
    faster = sound._spawn(sound.raw_data, overrides={"frame_rate": new_frame_rate})
    return faster.set_frame_rate(sound.frame_rate)

def change_volume(sound: AudioSegment, volume: float) -> AudioSegment:
    # volume is multiplicative factor; pydub works in dB
    if volume <= 0:
        # silence
        return AudioSegment.silent(duration=len(sound))
    try:
        db_change = 20 * math.log10(volume)
    except Exception:
        db_change = 0
    return sound + db_change

def make_pause(milliseconds: int) -> AudioSegment:
    if milliseconds <= 0:
        return AudioSegment.silent(duration=0)
    return AudioSegment.silent(duration=milliseconds)

def merge_segments(segments: list) -> AudioSegment:
    if not segments:
        return AudioSegment.silent(duration=0)
    output = segments[0]
    for seg in segments[1:]:
        output += seg
    return output

def save_audio(segment: AudioSegment, out_path: str, format: str = "wav"):
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    segment.export(out_path, format=format)

def temp_filename(ext: str = ".wav") -> str:
    return os.path.join(tempfile.gettempdir(), f"temp_{uuid.uuid4().hex}{ext}")


def cleanup_temp_files(prefix: str = "temp_"):
    """Remove temp files created by temp_filename in the system temp dir."""
    tmpdir = tempfile.gettempdir()
    for name in os.listdir(tmpdir):
        if name.startswith(prefix):
            try:
                os.remove(os.path.join(tmpdir, name))
            except Exception:
                pass
