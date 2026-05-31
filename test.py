import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[0]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.audio_processor import process_input
from core.transcriber import transcribe_all

source = "downloads/ADK vs RAG： How to Choose the Right AI Stack.wav"

if not os.path.exists(source):
    print(f"Local WAV file not found: {source}")
    source = "https://www.youtube.com/watch?v=Lg-meK5IU8Q"
    print(f"Falling back to test URL: {source}")

chunks = process_input(source, chunk_minutes=1)
print("Created chunks:", chunks)

use_sarvam = os.getenv("SARVAM_API_KEY") is not None
if use_sarvam:
    print("Using Sarvam for transcription.")
else:
    print("SARVAM_API_KEY not set; using local Whisper if installed.")

print(transcribe_all(chunks, use_sarvam=use_sarvam))
