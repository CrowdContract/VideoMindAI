"""Meeting information extractor — compatible with LangChain 1.x (invoke API)."""

from __future__ import annotations

import os

try:
    from langchain_mistralai import ChatMistralAI
except Exception:
    ChatMistralAI = None


def get_llm():
    if ChatMistralAI is None:
        return None
    return ChatMistralAI(
        model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
    )


def _call_llm(llm, system: str, text: str) -> str:
    """Call LLM with system + human messages using the modern .invoke() API."""
    response = llm.invoke([("system", system), ("human", text)])
    if hasattr(response, "content"):
        return response.content
    return str(response)


def extract_action_items(transcript: str) -> str:
    llm = get_llm()
    system = (
        "You are an expert video content analyst. From the video transcript, "
        "extract all action items. For each provide:\n"
        "- Task description\n- Owner (who is responsible)\n"
        "- Deadline (if mentioned, else write 'Not specified')\n"
        "Format as a numbered list. If none found say 'No action items found.'"
    )
    if llm is None:
        return "[LLM unavailable] Cannot extract action items."
    try:
        return _call_llm(llm, system, transcript)
    except Exception as e:
        return f"[Error extracting action items: {e}]"


def extract_key_decisions(transcript: str) -> str:
    llm = get_llm()
    system = (
        "You are an expert video content analyst. From the video transcript, "
        "extract all key decisions or conclusions made. Format as a numbered list. "
        "If none found say 'No key decisions found.'"
    )
    if llm is None:
        return "[LLM unavailable] Cannot extract key decisions."
    try:
        return _call_llm(llm, system, transcript)
    except Exception as e:
        return f"[Error extracting key decisions: {e}]"


def extract_questions(transcript: str) -> str:
    llm = get_llm()
    system = (
        "From the video transcript, extract all unresolved questions or "
        "topics that need further exploration. Format as a numbered list. "
        "If none found say 'No open questions found.'"
    )
    if llm is None:
        return "[LLM unavailable] Cannot extract questions."
    try:
        return _call_llm(llm, system, transcript)
    except Exception as e:
        return f"[Error extracting questions: {e}]"


__all__ = ["get_llm", "extract_action_items", "extract_key_decisions", "extract_questions"]
