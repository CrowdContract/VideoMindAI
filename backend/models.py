"""Pydantic models for request/response validation."""
from __future__ import annotations
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field


# ── Video ─────────────────────────────────────────────────────────────────────
class VideoBase(BaseModel):
    url: str
    language: str = "english"


class VideoProcessRequest(VideoBase):
    pass


class TranscriptChunk(BaseModel):
    text: str
    start: float
    end: float
    chunk_index: int


class VideoData(BaseModel):
    video_id: str
    url: str
    title: str = ""
    channel: str = ""
    duration_seconds: int = 0
    thumbnail_url: str = ""
    transcript: str = ""
    transcript_chunks: List[TranscriptChunk] = []
    summary: str = ""
    takeaways: List[str] = []
    action_items: str = ""
    quiz: List[dict] = []
    flashcards: List[dict] = []
    chapters: List[dict] = []
    open_questions: str = ""
    difficulty: str = "Intermediate"
    language: str = "en"
    processing_status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ── Job ───────────────────────────────────────────────────────────────────────
class JobStatus(BaseModel):
    job_id: str
    status: str  # pending|downloading|transcribing|embedding|generating|completed|failed
    progress: int = 0
    current_step: str = ""
    error: Optional[str] = None
    video_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ── Chat ──────────────────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str  # user | assistant
    content: str
    sources: List[dict] = []
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict] = []
    timestamp: Optional[str] = None


# ── Quiz / Flashcard ──────────────────────────────────────────────────────────
class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_index: int
    difficulty: str = "medium"
    explanation: str = ""


class Flashcard(BaseModel):
    front: str
    back: str
    chapter: str = ""


# ── User ──────────────────────────────────────────────────────────────────────
class UserPublic(BaseModel):
    id: str
    email: str
    name: str
    picture: str = ""
    plan: str = "free"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Generic ───────────────────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    redis: bool
    db: bool
    version: str = "1.0.0"
