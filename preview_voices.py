from TTS.api import TTS
import os

MODEL_NAME = "tts_models/en/vctk/vits"
tts = TTS(model_name=MODEL_NAME)
speakers = tts.speakers

os.makedirs("outputs/previews", exist_ok=True)

for spk in speakers:
    print(f"Generating preview for {spk}")
    # sanitize speaker name for filesystem
    safe_name = str(spk).strip().replace('\n', '_').replace('\r', '')
    # remove characters not allowed in Windows filenames
    for ch in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
        safe_name = safe_name.replace(ch, '_')
    out_path = os.path.join("outputs", "previews", f"{safe_name}.wav")
    tts.tts_to_file(
        text=f"This is {spk}, the speaker model for Coqui TTS.",
        file_path=out_path,
        speaker=spk
    )

print("\n✅ Voice previews generated in outputs/previews/")
