# Advanced TTS Audiobook Generator

Browser-based Gradio app for generating TTS previews and longer audiobook-style output with Coqui TTS.

## Features

- Dynamic TTS model dropdown populated from available Coqui models
- Speaker dropdown that updates after model selection
- Voice preview generation from selected model and speaker
- Saved preview browser for `.wav` files in `outputs/previews/`
- Dialogue builder, JSON import/export, and audiobook generation
- Automatic GPU/CUDA use when PyTorch reports CUDA is available

## Requirements

- Python 3.10+
- Packages listed in `requirements.txt`
- A working Coqui TTS installation and model access

## Quick Start

1. Create a virtual environment and install dependencies:

```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Launch the app:

```pwsh
python main.py
```

The UI opens in your browser. If CUDA is available, the engine uses GPU automatically; otherwise it falls back to CPU.

## How To Use

1. Select a TTS model from the dropdown.
2. Wait for the speaker list to load, then choose a speaker if the model supports multiple voices.
3. Use the preview controls to generate short samples.
4. Browse saved previews from `outputs/previews/` and play them in the audio player.
5. Build dialogues or import JSON to generate longer audio files.

## Project Structure

- `gui.py` - Gradio app for model selection, previews, and audiobook generation
- `tts_engine.py` - Coqui TTS wrapper with CUDA auto-detection
- `audio_utils.py` - audio manipulation and merging helpers
- `json_utils.py` - dialogue JSON loading, saving, and validation
- `main.py` - application entry point

## Output Folders

- `outputs/previews/` - saved voice preview `.wav` files
- `temp_audio/` - temporary audio files used during synthesis

## Troubleshooting

- If no models appear, click Refresh Models in the UI.
- If speaker selection stays disabled, the chosen model is probably single-speaker.
- If CUDA is installed but not used, verify that PyTorch sees your GPU.
- If Coqui model downloads fail, check network access and local permissions.

## Notes

- Model availability depends on your environment and network access.
- The app runs on CPU when CUDA is unavailable.
