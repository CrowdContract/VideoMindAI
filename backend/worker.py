"""Celery worker — async background job processing."""
import asyncio
import glob
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from celery import Celery
from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from backend.config import get_settings

settings = get_settings()

celery_app = Celery("videomind")

# Upstash uses rediss:// (TLS). Celery 5.3 requires ssl_cert_reqs in the URL itself.
def _make_celery_url(url: str) -> str:
    if url.startswith("rediss://") and "ssl_cert_reqs" not in url:
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}ssl_cert_reqs=CERT_NONE"
    return url

_broker_url  = _make_celery_url(settings.REDIS_URL)
_backend_url = _make_celery_url(settings.REDIS_URL)

celery_app.conf.update(
    broker_url=_broker_url,
    result_backend=_backend_url,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_track_started=True,
    broker_connection_retry_on_startup=True,
    broker_transport_options={"visibility_timeout": 3600},
)


def _run(coro):
    """Run an async coroutine from a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _update_job(db, job_id: str, **kwargs):
    await db.jobs.update_one({"job_id": job_id}, {"$set": kwargs})


def _extract_video_id(url: str) -> str:
    """Extract the 11-char YouTube video ID from a URL."""
    match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else re.sub(r"[^A-Za-z0-9_-]", "_", url)[:32]


def _cleanup_audio(chunks: list, wav_path: str | None = None):
    """Delete all temporary audio files after processing."""
    for chunk in chunks:
        try:
            if os.path.exists(chunk):
                os.remove(chunk)
        except Exception:
            pass
    if wav_path and os.path.exists(wav_path):
        try:
            os.remove(wav_path)
        except Exception:
            pass


@celery_app.task(bind=True, name="process_video")
def process_video_task(self, job_id: str, url: str, language: str, user_id: str | None):
    from motor.motor_asyncio import AsyncIOMotorClient
    from core.summarize import summarize, generate_title
    from core.extractor import extract_action_items, extract_key_decisions, extract_questions
    from core.rag_engine import build_rag_chain
    from backend.generators import (
        generate_quiz, generate_flashcards,
        generate_chapters, generate_takeaways,
        estimate_difficulty,
    )
    from utils.audio_processor import process_input
    from core.transcriber import transcribe_all

    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB]
    chunks = []

    async def run():
        nonlocal chunks
        try:
            video_id = _extract_video_id(url)

            # ── Step 1: Download ──────────────────────────────────────────
            await _update_job(db, job_id, status="downloading", progress=5,
                              current_step="Downloading audio...")
            chunks = process_input(url)

            # ── Step 2: Transcribe ────────────────────────────────────────
            await _update_job(db, job_id, status="transcribing", progress=20,
                              current_step="Transcribing audio with Whisper...")
            translate = language.lower() == "hinglish"
            use_sarvam = translate and bool(settings.SARVAM_API_KEY)
            transcript = transcribe_all(chunks, translate=translate, use_sarvam=use_sarvam)

            # ── Step 3: Parallel LLM generation ──────────────────────────
            await _update_job(db, job_id, status="generating", progress=45,
                              current_step="Generating AI insights in parallel...")

            (
                title, summary, action_items, decisions, questions,
                quiz, flashcards, chapters, takeaways, difficulty,
            ) = await asyncio.gather(
                asyncio.to_thread(generate_title, transcript),
                asyncio.to_thread(summarize, transcript),
                asyncio.to_thread(extract_action_items, transcript),
                asyncio.to_thread(extract_key_decisions, transcript),
                asyncio.to_thread(extract_questions, transcript),
                asyncio.to_thread(generate_quiz, transcript),
                asyncio.to_thread(generate_flashcards, transcript),
                asyncio.to_thread(generate_chapters, transcript),
                asyncio.to_thread(generate_takeaways, transcript),
                asyncio.to_thread(estimate_difficulty, transcript),
                return_exceptions=True,
            )

            def safe(val, default):
                return default if isinstance(val, Exception) else val

            difficulty_data = safe(difficulty, {})
            difficulty_level = difficulty_data.get("level", "Intermediate") if isinstance(difficulty_data, dict) else "Intermediate"

            # ── Step 4: Build vector store (per-video) ────────────────────
            await _update_job(db, job_id, status="embedding", progress=82,
                              current_step="Building vector store...")
            build_rag_chain(transcript, video_id=video_id)

            # ── Step 5: Save to MongoDB ───────────────────────────────────
            await _update_job(db, job_id, status="embedding", progress=92,
                              current_step="Saving to database...")

            doc = {
                "video_id": video_id,
                "url": url,
                "title": safe(title, "Untitled"),
                "transcript": transcript,
                "summary": safe(summary, ""),
                "action_items": safe(action_items, ""),
                "key_decisions": safe(decisions, ""),
                "open_questions": safe(questions, ""),
                "quiz": safe(quiz, []),
                "flashcards": safe(flashcards, []),
                "chapters": safe(chapters, []),
                "takeaways": safe(takeaways, []),
                "difficulty": difficulty_level,
                "difficulty_detail": safe(difficulty_data, {}),
                "language": language,
                "processing_status": "completed",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            await db.videos.update_one(
                {"video_id": video_id}, {"$set": doc}, upsert=True
            )
            if user_id:
                await db.user_videos.update_one(
                    {"user_id": user_id, "video_id": video_id},
                    {"$setOnInsert": {
                        "user_id": user_id, "video_id": video_id,
                        "created_at": datetime.utcnow(),
                    }},
                    upsert=True,
                )

            await _update_job(db, job_id, status="completed", progress=100,
                              current_step="Done!", video_id=video_id)

        except Exception as exc:
            await _update_job(db, job_id, status="failed", error=str(exc),
                              current_step="Failed")
            raise
        finally:
            # Always clean up temp audio files
            _cleanup_audio(chunks)
            client.close()

    _run(run())
