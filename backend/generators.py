"""Parallel LLM generators — quiz, flashcards, chapters, takeaways, difficulty."""
from __future__ import annotations
import json
import os
import re
from typing import List

try:
    from langchain_mistralai import ChatMistralAI
except Exception:
    ChatMistralAI = None

from backend.config import get_settings

settings = get_settings()


def _llm():
    if ChatMistralAI is None:
        raise RuntimeError("langchain_mistralai not installed")
    return ChatMistralAI(
        model=settings.MISTRAL_MODEL,
        mistral_api_key=settings.MISTRAL_API_KEY,
        temperature=0.4,
    )


def _call(system: str, human: str) -> str:
    resp = _llm().invoke([("system", system), ("human", human)])
    return resp.content if hasattr(resp, "content") else str(resp)


def _parse_json(text: str, fallback):
    """Extract first JSON array/object from LLM output."""
    match = re.search(r"(\[.*?\]|\{.*?\})", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    # Try the whole text as JSON
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    return fallback


def generate_quiz(transcript: str) -> List[dict]:
    system = """You are an expert educator. Generate 8 multiple-choice questions from this video transcript.
Return ONLY a valid JSON array. Each item must have exactly these keys:
{"question": "...", "options": ["A","B","C","D"], "correct_index": 0, "difficulty": "easy|medium|hard", "explanation": "..."}
No markdown, no explanation outside the JSON."""
    try:
        raw = _call(system, transcript[:6000])
        return _parse_json(raw, [])
    except Exception:
        return []


def generate_flashcards(transcript: str) -> List[dict]:
    system = """Create 10 flashcards for spaced repetition from this video transcript.
Return ONLY a valid JSON array. Each item: {"front": "question/term", "back": "answer/definition", "chapter": "topic"}
No markdown, no explanation outside the JSON."""
    try:
        raw = _call(system, transcript[:6000])
        return _parse_json(raw, [])
    except Exception:
        return []


def generate_chapters(transcript: str) -> List[dict]:
    system = """Detect logical chapters/sections in this video transcript.
Return ONLY a valid JSON array. Each item: {"title": "...", "start_time": "MM:SS", "end_time": "MM:SS", "summary": "1-2 sentences"}
No markdown, no explanation outside the JSON."""
    try:
        raw = _call(system, transcript[:8000])
        return _parse_json(raw, [])
    except Exception:
        return []


def generate_takeaways(transcript: str) -> List[str]:
    system = """Extract 5-7 key takeaways from this video transcript as a JSON array of strings.
Return ONLY a valid JSON array like: ["Takeaway 1", "Takeaway 2", ...]
No markdown, no explanation outside the JSON."""
    try:
        raw = _call(system, transcript[:6000])
        result = _parse_json(raw, [])
        return result if isinstance(result, list) else []
    except Exception:
        return []


def estimate_difficulty(transcript: str) -> dict:
    """Rate video complexity as Beginner / Intermediate / Advanced with explanation."""
    system = """You are an expert educator. Analyze this video transcript and rate its difficulty level.
Return ONLY a valid JSON object with exactly these keys:
{
  "level": "Beginner|Intermediate|Advanced",
  "score": 1-10,
  "explanation": "2-3 sentences explaining why",
  "prerequisites": ["topic1", "topic2"],
  "target_audience": "who this video is for"
}
No markdown, no explanation outside the JSON."""
    try:
        raw = _call(system, transcript[:5000])
        result = _parse_json(raw, {})
        if isinstance(result, dict) and "level" in result:
            return result
        return {"level": "Intermediate", "score": 5, "explanation": "Could not estimate difficulty.", "prerequisites": [], "target_audience": "General audience"}
    except Exception:
        return {"level": "Intermediate", "score": 5, "explanation": "Could not estimate difficulty.", "prerequisites": [], "target_audience": "General audience"}
