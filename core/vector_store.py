"""Per-video Chroma vector store — each video gets its own collection."""
import os
import typing as t

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
except Exception:
    try:
        from langchain.embeddings import HuggingFaceEmbeddings
    except Exception:
        HuggingFaceEmbeddings = None

try:
    from langchain_community.vectorstores import Chroma
except Exception:
    try:
        from langchain.vectorstores import Chroma
    except Exception:
        Chroma = None

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except Exception:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except Exception:
        RecursiveCharacterTextSplitter = None

try:
    from langchain_core.documents import Document
except Exception:
    try:
        from langchain.docstore.document import Document
    except Exception:
        Document = None

CHROMA_BASE_DIR = "vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_embeddings_cache = None


def _require(name: str, obj: t.Any) -> None:
    if obj is None:
        raise ImportError(f"{name} is not available.")


def get_embeddings():
    global _embeddings_cache
    if _embeddings_cache is None:
        _require("HuggingFaceEmbeddings", HuggingFaceEmbeddings)
        _embeddings_cache = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
        )
    return _embeddings_cache


def _collection_name(video_id: str) -> str:
    """Sanitize video_id into a valid Chroma collection name."""
    import re
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", video_id)[:60]
    return f"vid_{safe}"


def _persist_dir(video_id: str) -> str:
    path = os.path.join(CHROMA_BASE_DIR, video_id)
    os.makedirs(path, exist_ok=True)
    return path


def build_vector_store(transcript: str, video_id: str = "default"):
    """Build and persist a per-video Chroma vector store."""
    _require("Chroma", Chroma)
    _require("RecursiveCharacterTextSplitter", RecursiveCharacterTextSplitter)
    _require("Document", Document)

    print(f"Building vector store for video: {video_id}")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(transcript)

    docs = [
        Document(page_content=chunk, metadata={"chunk_index": i, "video_id": video_id})
        for i, chunk in enumerate(chunks)
    ]
    embeddings = get_embeddings()
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=_collection_name(video_id),
        persist_directory=_persist_dir(video_id),
    )
    return vector_store


def load_vector_store(video_id: str = "default"):
    """Load an existing persisted per-video Chroma vector store."""
    _require("Chroma", Chroma)
    embeddings = get_embeddings()
    return Chroma(
        collection_name=_collection_name(video_id),
        embedding_function=embeddings,
        persist_directory=_persist_dir(video_id),
    )


def vector_store_exists(video_id: str) -> bool:
    """Check if a vector store already exists for this video."""
    persist_dir = os.path.join(CHROMA_BASE_DIR, video_id)
    return os.path.isdir(persist_dir) and len(os.listdir(persist_dir)) > 0


def get_retriever(vector_store, k: int = 4):
    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})


__all__ = [
    "build_vector_store", "load_vector_store",
    "vector_store_exists", "get_retriever", "get_embeddings",
]
