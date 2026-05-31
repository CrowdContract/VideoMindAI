"""Summarization helpers — compatible with LangChain 1.x (invoke API)."""

from __future__ import annotations

import os
import re
import typing as t

try:
    from langchain_mistralai import ChatMistralAI
except Exception:
    ChatMistralAI = None

try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
except Exception:
    ChatPromptTemplate = None
    StrOutputParser = None

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except Exception:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except Exception:
        RecursiveCharacterTextSplitter = None


def get_llm():
    if ChatMistralAI is None:
        return None
    return ChatMistralAI(
        model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.7,
    )


def _call_llm(llm, messages: list) -> str:
    """Call LLM using the modern .invoke() API and return string output."""
    response = llm.invoke(messages)
    if hasattr(response, "content"):
        return response.content
    return str(response)


def split_transcript(transcript: str) -> t.List[str]:
    if not transcript:
        return []
    if RecursiveCharacterTextSplitter is not None:
        splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
        return splitter.split_text(transcript)
    # Fallback
    chunk_size, overlap, chunks, start = 3000, 200, [], 0
    length = len(transcript)
    while start < length:
        end = min(start + chunk_size, length)
        chunks.append(transcript[start:end])
        start = end - overlap
        if start >= length:
            break
    return chunks


def summarize(transcript: str) -> str:
    if not transcript:
        return ""

    chunks = split_transcript(transcript)
    llm = get_llm()

    if llm is not None:
        partials: t.List[str] = []
        for chunk in chunks:
            try:
                out = _call_llm(llm, [
                    ("system", "Summarize this portion of a video transcript concisely."),
                    ("human", chunk),
                ])
                partials.append(out)
            except Exception:
                partials.append(chunk.strip()[:300])

        combined = "\n\n".join(partials)
        try:
            final = _call_llm(llm, [
                ("system", (
                    "You are an expert video content summarizer. Combine these partial summaries "
                    "into one final professional summary in bullet points."
                )),
                ("human", combined),
            ])
            return final
        except Exception:
            return combined

    # Local extractive fallback
    summaries: t.List[str] = []
    for chunk in chunks:
        sentences = re.split(r'(?<=[.!?])\s+', chunk.strip())
        summaries.append(" ".join(sentences[:2])[:400] if sentences else chunk[:300])
    return "\n\n".join(summaries)[:2000]


def generate_title(transcript: str) -> str:
    if not transcript:
        return ""

    llm = get_llm()
    if llm is not None:
        try:
            out = _call_llm(llm, [
                ("system", (
                    "Based on the video transcript, generate a short professional video title "
                    "(max 8 words). Only return the title, nothing else."
                )),
                ("human", transcript[:2000]),
            ])
            return out.strip().split("\n")[0].strip()
        except Exception:
            pass

    cleaned = re.sub(r"\s+", " ", transcript.replace("\n", " ")).strip()
    return " ".join(cleaned.split()[:8])
