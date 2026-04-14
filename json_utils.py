"""
json_utils.py

Load, save, validate dialogue JSON and chunk long dialogues.
"""
import json
from typing import List, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

DEFAULTS = {
    "speed": 1.0,
    "volume": 1.0,
    "pause_after": 0
}

def save_dialogues(dialogues: List[Dict[str, Any]], path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dialogues, f, ensure_ascii=False, indent=2)

def load_dialogues(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def validate_dialogue(item: Dict[str, Any]) -> bool:
    if not isinstance(item, dict):
        return False
    if "speaker" not in item or "text" not in item:
        return False
    return True

def apply_defaults(item: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(item)
    for k, v in DEFAULTS.items():
        out.setdefault(k, v)
    # normalize keys
    out.setdefault("pause_after", out.get("pause", out.get("pause_after", 0)))
    return out


def chunk_text(text: str, max_chars: int = 1500) -> List[str]:
    """Naive chunker: split on sentence boundaries if possible, else hard split."""
    if len(text) <= max_chars:
        return [text]
    sentences = text.replace("\n", " ").split('. ')
    chunks = []
    current = ""
    for s in sentences:
        part = (s.strip() + (". " if not s.endswith('.') else ""))
        if len(current) + len(part) <= max_chars:
            current += part
        else:
            if current:
                chunks.append(current.strip())
            if len(part) > max_chars:
                # hard split
                for i in range(0, len(part), max_chars):
                    chunks.append(part[i:i+max_chars].strip())
                current = ""
            else:
                current = part
    if current:
        chunks.append(current.strip())
    return chunks
