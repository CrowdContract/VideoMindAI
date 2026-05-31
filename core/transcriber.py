"""Transcriber — uses faster-whisper (pre-built wheels, works on all platforms)."""
import base64
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import requests
from utils.audio_processor import process_input

WHISPER_MODEL   = os.getenv("WHISPER_MODEL", "base")
SARVAM_API_KEY  = os.getenv("SARVAM_API_KEY")
SARVAM_MODEL    = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")
SARVAM_TRANSLATE_URL = os.getenv("SARVAM_TRANSLATE_URL", "https://api.sarvam.ai/v1/audio/translate")

_model = None


def load_model():
    global _model
    if _model is None:
        try:
            from faster_whisper import WhisperModel
            print(f"Loading faster-whisper model '{WHISPER_MODEL}'...")
            _model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        except ImportError:
            # Fallback to openai-whisper if faster-whisper not available
            import whisper
            print(f"Loading openai-whisper model '{WHISPER_MODEL}'...")
            _model = whisper.load_model(WHISPER_MODEL)
    return _model


def _transcribe_faster_whisper(chunk_path: str, translate: bool = False) -> str:
    model = load_model()
    task = "translate" if translate else "transcribe"
    # faster-whisper returns segments iterator
    if hasattr(model, "transcribe") and hasattr(model, "feature_extractor"):
        # faster-whisper API
        segments, _ = model.transcribe(chunk_path, task=task)
        return " ".join(seg.text for seg in segments).strip()
    else:
        # openai-whisper API
        result = model.transcribe(chunk_path, task=task)
        return result["text"]


def sarvam_translate_audio(audio_path: str, target_lang: str = "en") -> dict:
    if SARVAM_API_KEY is None:
        raise RuntimeError("SARVAM_API_KEY is not set.")
    with open(audio_path, "rb") as f:
        files = {"file": (os.path.basename(audio_path), f, "audio/wav")}
        data  = {"model": SARVAM_MODEL, "target_lang": target_lang,
                 "response_format": "json", "output_audio": "false"}
        headers = {"Authorization": f"Bearer {SARVAM_API_KEY}"}
        resp = requests.post(SARVAM_TRANSLATE_URL, headers=headers,
                             data=data, files=files, timeout=120)
        resp.raise_for_status()
    payload = resp.json()
    text = (payload.get("text") or payload.get("translated_text")
            or payload.get("translation") or payload.get("output_text") or "")
    return {"text": text, "audio_path": None}


def transcribe_chunk(chunk_path: str, translate: bool = False,
                     use_sarvam: bool = False) -> dict:
    if use_sarvam:
        return sarvam_translate_audio(chunk_path, target_lang="en" if translate else "hi")
    return {"text": _transcribe_faster_whisper(chunk_path, translate=translate),
            "audio_path": None}


def transcribe_all(chunks: list, translate: bool = False,
                   use_sarvam: bool = False, **kwargs) -> str:
    parts = []
    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i + 1}/{len(chunks)}")
        result = transcribe_chunk(chunk, translate=translate, use_sarvam=use_sarvam)
        parts.append(result["text"])
    transcript = " ".join(parts).strip()
    print("Transcription complete.")
    return transcript


def transcribe(source: str, translate: bool = False,
               chunk_minutes: int = 1, use_sarvam: bool = False) -> str:
    chunks = process_input(source, chunk_minutes=chunk_minutes)
    return transcribe_all(chunks, translate=translate, use_sarvam=use_sarvam)


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "https://www.youtube.com/watch?v=7HSSR1n8dgc"
    print(transcribe(src, chunk_minutes=1))
