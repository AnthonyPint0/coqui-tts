"""
gui.py

Gradio-based GUI for creating dialogues, previewing, exporting JSON, uploading JSON, and generating audiobook.
"""
import gradio as gr
import json
import os
import logging
from typing import List, Dict, Any
from tts_engine import TTSEngine
from audio_utils import change_speed, change_volume, make_pause, merge_segments, save_audio, temp_filename
from json_utils import save_dialogues, load_dialogues, apply_defaults, chunk_text
from tqdm import tqdm
from pydub import AudioSegment

logger = logging.getLogger(__name__)

# Simple in-memory dialogue store
DIALOGUES: List[Dict[str, Any]] = []

# Initialize default TTS engine lazily
DEFAULT_TTS = None

def get_engine(model_name: str = None) -> TTSEngine:
    global DEFAULT_TTS
    if DEFAULT_TTS is None:
        DEFAULT_TTS = TTSEngine(model_name=model_name)
    return DEFAULT_TTS


def add_dialogue(speaker: str, text: str, speed: float = 1.0, volume: float = 1.0, pause_after: int = 0, emotion: str = None):
    if not speaker or not text:
        return "Speaker and text required", DIALOGUES
    item = {
        "speaker": speaker,
        "text": text,
        "speed": speed,
        "volume": volume,
        "pause_after": pause_after
    }
    if emotion:
        item["emotion"] = emotion
    DIALOGUES.append(item)
    return "Added.", DIALOGUES


def clear_dialogues():
    global DIALOGUES
    DIALOGUES = []
    return DIALOGUES


def preview_dialogue(idx: int, model_name: str = None):
    if idx < 0 or idx >= len(DIALOGUES):
        return None
    item = DIALOGUES[idx]
    engine = get_engine(model_name)
    seg = engine.synthesize(item["text"], speaker=item.get("speaker"))
    seg = change_speed(seg, item.get("speed", 1.0))
    seg = change_volume(seg, item.get("volume", 1.0))
    # save to temp
    tmp = temp_filename()
    seg.export(tmp, format="wav")
    return tmp


def export_json(filename: str = "dialogues.json"):
    path = os.path.abspath(filename)
    save_dialogues(DIALOGUES, path)
    return f"Saved to {path}"


def generate_audiobook_from_json(json_path: str, out_path: str = "final_story.wav", model_name: str = None):
    engine = get_engine(model_name)
    dialogues = load_dialogues(json_path)
    segments = []
    total = len(dialogues)
    for item in tqdm(dialogues, desc="Dialogues"):
        if not apply_defaults(item):
            logger.error("Invalid dialogue item: %s", item)
            continue
        item = apply_defaults(item)
        chunks = chunk_text(item["text"])  # list of strings
        for c in chunks:
            try:
                seg = engine.synthesize(c, speaker=item.get("speaker"))
                seg = change_speed(seg, item.get("speed", 1.0))
                seg = change_volume(seg, item.get("volume", 1.0))
                if item.get("pause_after", 0) > 0:
                    seg += make_pause(item.get("pause_after"))
                segments.append(seg)
            except Exception as e:
                logger.exception("TTS failed for chunk")
    final = merge_segments(segments)
    save_audio(final, out_path)
    return os.path.abspath(out_path)


def build_gradio_app():
    with gr.Blocks() as demo:
        gr.Markdown("# Advanced TTS Audiobook Generator")
        with gr.Row():
            model_name = gr.Textbox(label="TTS Model Name (optional)")
            speaker = gr.Textbox(label="Speaker ID")
            text = gr.Textbox(label="Dialogue text", lines=4)
            with gr.Row():
                speed = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, step=0.05, label="Speed")
                volume = gr.Slider(minimum=0.0, maximum=2.0, value=1.0, step=0.05, label="Volume")
                pause_after = gr.Number(value=0, label="Pause after (ms)")

            add_btn = gr.Button("Add Dialogue")
            clear_btn = gr.Button("Clear Dialogues")
            export_btn = gr.Button("Export JSON")
            preview_btn = gr.Button("Preview Last")
            file_output = gr.Textbox(label="Status")
            list_out = gr.Dataframe(headers=["speaker","text","speed","volume","pause_after"], interactive=False)
            export_name = gr.Textbox(value="dialogues.json", label="Export filename")

            def _add(speaker_, text_, speed_, volume_, pause_, model_):
                msg, data = add_dialogue(speaker_, text_, speed_, volume_, int(pause_), None)
                return msg, data

            add_btn.click(_add, inputs=[speaker, text, speed, volume, pause_after, model_name], outputs=[file_output, list_out])

            def _clear():
                clear_dialogues()
                return "Cleared", []

            clear_btn.click(_clear, outputs=[file_output, list_out])
            export_btn.click(lambda name: export_json(name), inputs=[export_name], outputs=[file_output])
            preview_btn.click(lambda m: preview_dialogue(len(DIALOGUES)-1, m), inputs=[model_name], outputs=[gr.Audio()])

            gr.Markdown("## Import JSON and Generate Audiobook")
            upload = gr.File(label="Upload JSON")
            outpath = gr.Textbox(value="final_story.wav", label="Output filename")
            gen_btn = gr.Button("Generate Audiobook")
            prog = gr.Progress()

            def _gen(file, outp, model_):
                if not file:
                    yield "No file uploaded"
                    return
                path = file.name
                try:
                    # load dialogues to get count
                    dialogues = load_dialogues(path)
                except Exception as e:
                    yield f"Failed to read JSON: {e}"
                    return

                total = len(dialogues)
                yield f"Starting generation: {total} dialogues"
                segments = []
                engine = get_engine(model_)
                i = 0
                for item in dialogues:
                    i += 1
                    yield f"Processing dialogue {i}/{total}"
                    try:
                        item = apply_defaults(item)
                        chunks = chunk_text(item["text"])  # list of strings
                        for c in chunks:
                            seg = engine.synthesize(c, speaker=item.get("speaker"))
                            seg = change_speed(seg, item.get("speed", 1.0))
                            seg = change_volume(seg, item.get("volume", 1.0))
                            if item.get("pause_after", 0) > 0:
                                seg += make_pause(item.get("pause_after"))
                            segments.append(seg)
                    except Exception as e:
                        yield f"Error synthesizing dialogue {i}: {e}"
                if not segments:
                    yield "No audio generated."
                    return
                yield "Merging segments..."
                final = merge_segments(segments)
                try:
                    save_audio(final, outp)
                    yield f"Saved audiobook to {os.path.abspath(outp)}"
                except Exception as e:
                    yield f"Failed to save audio: {e}"

            gen_btn.click(_gen, inputs=[upload, outpath, model_name], outputs=[file_output])

        return demo


if __name__ == "__main__":
    app = build_gradio_app()
    app.launch()
