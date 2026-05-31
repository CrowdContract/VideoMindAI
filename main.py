import os
import sys
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question


load_dotenv()


def run_pipeline(source: str, language: str = "english") -> dict:
    print("starting AI Video Assistant")

    chunks = process_input(source)

    language = language.strip().lower()
    if language not in ["english", "hinglish"]:
        print("Unsupported language input, defaulting to english.")
        language = "english"

    translate = language == "hinglish"
    use_sarvam = translate and bool(os.getenv("SARVAM_API_KEY"))
    if translate and not use_sarvam:
        print("SARVAM_API_KEY not configured. Using local Whisper translation if available.")

    transcript = transcribe_all(chunks, translate=translate, use_sarvam=use_sarvam)
    print(f"raw transcription (first 300 characters ) {transcript[:300]}")

    title = generate_title(transcript)
    summary = summarize(transcript)
    action_items = extract_action_items(transcript)
    decisions = extract_key_decisions(transcript)
    questions = extract_questions(transcript)
    rag_chain = build_rag_chain(transcript)

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }


def run_chat_loop(rag_chain):
    print("\nChat with your meeting (type 'exit' to quit)\n")
    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break
        if not question:
            continue
        answer = ask_question(rag_chain, question)
        print(f"\n🧠 Assistant: {answer}\n")


if __name__ == "__main__":
    source = input("Enter YouTube URL or local file path: ").strip()
    language = input("Language (english/hinglish): ").strip() or "english"
    try:
        result = run_pipeline(source, language)
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(f"🚀 Title: {result['title']}")
    print(f"\n📝 Summary:\n{result['summary']}")
    print(f"\n✅ Action Items:\n{result['action_items']}")
    print(f"\n🔑 Key Decisions:\n{result['key_decisions']}")
    print(f"\n❓ Open Questions:\n{result['open_questions']}")
    print("=" * 60)

    if result["rag_chain"] is not None:
        run_chat_loop(result["rag_chain"])
    else:
        print("\nRAG Chat is unavailable because the required RAG dependencies or vector store support are not installed.")
