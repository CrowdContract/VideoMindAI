import base64
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import requests
from utils.audio_processor import process_input

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")
SARVAM_TRANSLATE_URL = os.getenv("SARVAM_TRANSLATE_URL", "https://api.sarvam.ai/v1/audio/translate")
_model = None


def load_model():
    global _model
    try:
        import whisper
    except ImportError as exc:
        raise RuntimeError(
            "openai-whisper is not installed. Install it with `python -m pip install openai-whisper` "
            "or use `--sarvam` mode instead."
        ) from exc

    if _model is None:
        print(f"Loading Whisper model '{WHISPER_MODEL}'...")
        _model = whisper.load_model(WHISPER_MODEL)
    return _model


def sarvam_translate_audio(audio_path: str, target_lang: str = "en", output_audio: bool = True) -> dict:
    if SARVAM_API_KEY is None:
        raise RuntimeError("SARVAM_API_KEY is not set in the environment.")

    with open(audio_path, "rb") as audio_file:
        files = {"file": (os.path.basename(audio_path), audio_file, "audio/wav")}
        data = {
            "model": SARVAM_MODEL,
            "target_lang": target_lang,
            "response_format": "json",
            "output_audio": str(output_audio).lower(),
        }
        headers = {"Authorization": f"Bearer {SARVAM_API_KEY}"}
        response = requests.post(SARVAM_TRANSLATE_URL, headers=headers, data=data, files=files, timeout=120)
        response.raise_for_status()

    payload = response.json()
    text = payload.get("text") or payload.get("translated_text") or payload.get("translation") or payload.get("output_text")
    audio_path_out = None

    audio_data = payload.get("audio") or payload.get("audio_base64") or payload.get("output_audio")
    if audio_data and isinstance(audio_data, str):
        try:
            decoded_audio = base64.b64decode(audio_data)
            audio_path_out = os.path.splitext(audio_path)[0] + "_sarvam_output.mp3"
            with open(audio_path_out, "wb") as out_file:
                out_file.write(decoded_audio)
        except (ValueError, base64.binascii.Error):
            audio_path_out = None

    return {"text": text or "", "audio_path": audio_path_out, "payload": payload}


def transcribe_chunk(chunk_path: str, translate: bool = False, use_sarvam: bool = False, output_audio: bool = False) -> dict:
    if use_sarvam:
        target_lang = "en" if translate else "hi"
        result = sarvam_translate_audio(chunk_path, target_lang=target_lang, output_audio=output_audio)
        return result

    model = load_model()
    task = "translate" if translate else "transcribe"
    result = model.transcribe(chunk_path, task=task)
    return {"text": result["text"], "audio_path": None}


def transcribe_all(chunks: list, translate: bool = False, use_sarvam: bool = False, output_audio: bool = False):
    full_transcript = ""
    audio_paths = []

    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i+1}")
        result = transcribe_chunk(chunk, translate=translate, use_sarvam=use_sarvam, output_audio=output_audio)
        full_transcript += result["text"] + " "
        if output_audio and result.get("audio_path"):
            audio_paths.append(result["audio_path"])

    full_transcript = full_transcript.strip()
    print("Transcription completed")

    if output_audio and use_sarvam:
        return {"text": full_transcript, "audio_paths": audio_paths}
    return full_transcript


def transcribe(source: str, translate: bool = False, chunk_minutes: int = 1, use_sarvam: bool = False, output_audio: bool = False):
    chunks = process_input(source, chunk_minutes=chunk_minutes)
    return transcribe_all(chunks, translate=translate, use_sarvam=use_sarvam, output_audio=output_audio)


if __name__ == "__main__":
    import sys

    source = sys.argv[1] if len(sys.argv) > 1 else "https://www.youtube.com/watch?v=7HSSR1n8dgc"
    translate_flag = "--translate" in sys.argv
    use_sarvam = "--sarvam" in sys.argv
    output_audio = "--audio-output" in sys.argv
    transcript = transcribe(source, translate=translate_flag, chunk_minutes=1, use_sarvam=use_sarvam, output_audio=output_audio)
    print(transcript)

