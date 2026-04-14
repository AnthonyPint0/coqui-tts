Advanced TTS Audiobook Generator

This project provides a browser-based GUI to create dialogues, export/import JSON scripts, and generate a merged audiobook using Coqui TTS.

Requirements
- Python 3.10+
- Packages listed in requirements.txt

Quick start
1. Create a virtualenv and install dependencies:

```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the GUI:

```pwsh
python main.py
```

Files
- `tts_engine.py` - wrapper around Coqui TTS.api
- `audio_utils.py` - manipulate and merge audio segments
- `json_utils.py` - load/save/validate dialogue JSON
- `gui.py` - Gradio app for creating dialogues and generating audiobooks
- `main.py` - entrypoint

Notes
- This is a starter scaffold. You must have Coqui TTS models available or allow the code to download them.
