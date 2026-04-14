"""
preview_voices_fallback.py

Try to run the provided Coqui TTS preview script if `TTS` package is available.
If not available (common on Windows due to package incompatibility), fall back to `pyttsx3`
which is a lightweight, offline TTS engine suitable for quick previews.

Usage:
    python preview_voices_fallback.py

This will write WAV files to `outputs/previews/`.
"""
import os
import sys
import wave
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

OUT_DIR = os.path.join("outputs", "previews")
os.makedirs(OUT_DIR, exist_ok=True)

try:
    # Try to import Coqui TTS
    from TTS.api import TTS  # type: ignore
    has_coqui = True
except Exception as e:
    logger.info("Coqui TTS not available: %s", e)
    has_coqui = False

if has_coqui:
    # Run the user's preview_voices.py logic here programmatically
    MODEL_NAME = "tts_models/en/vctk/vits"
    tts = TTS(model_name=MODEL_NAME)
    speakers = getattr(tts, "speakers", [])
    if not speakers:
        # Some TTS models expose voices as `voices` or similar; try fallback
        speakers = getattr(tts, "voices", []) or []

    if not speakers:
        # If there are no distinct speakers, use default single voice
        logger.info("No speaker list found in model; generating single preview")
        out_path = os.path.join(OUT_DIR, "default.wav")
        tts.tts_to_file(text="This is the default model voice.", file_path=out_path)
        logger.info("Wrote %s", out_path)
    else:
        for spk in speakers:
            logger.info("Generating preview for %s", spk)
            # sanitize speaker name
            safe_name = str(spk).strip().replace('\n', '_').replace('\r', '')
            for ch in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
                safe_name = safe_name.replace(ch, '_')
            out_path = os.path.join(OUT_DIR, f"{safe_name}.wav")
            try:
                tts.tts_to_file(text=f"This is {spk}, the speaker model for Coqui TTS.", file_path=out_path, speaker=spk)
            except Exception:
                # some models may not support speaker argument; fall back
                tts.tts_to_file(text=f"Preview for speaker {spk}.", file_path=out_path)
            logger.info("Wrote %s", out_path)

else:
    # Fall back to pyttsx3 to generate a single preview file per OS-available voice
    try:
        import pyttsx3
    except Exception as e:
        logger.error("pyttsx3 not installed. Install it with: pip install pyttsx3")
        sys.exit(1)

    engine = pyttsx3.init()
    voices = engine.getProperty('voices') or []
    if not voices:
        logger.error("No voices available in pyttsx3 on this system.")
        sys.exit(1)

    logger.info("Using pyttsx3 fallback with %d voices", len(voices))
    for idx, v in enumerate(voices):
        name = getattr(v, 'name', f'voice_{idx}')
        safe_name = str(name).strip().replace('\n', '_').replace('\r', '')
        for ch in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
            safe_name = safe_name.replace(ch, '_')
        fname = os.path.join(OUT_DIR, f"{safe_name}.wav")
        logger.info("Generating fallback preview for %s -> %s", name, fname)
        # pyttsx3 can save to file via the `save_to_file` method and runAndWait
        engine.setProperty('voice', v.id)
        engine.save_to_file(f"This is {name} using pyttsx3.", fname)
    engine.runAndWait()
    logger.info("Fallback previews written to %s", OUT_DIR)
