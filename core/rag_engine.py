"""RAG engine — per-video vector store, LangChain 1.x invoke API."""
import os
from core.vector_store import (
    build_vector_store, load_vector_store,
    vector_store_exists, get_retriever,
)


def get_llm():
    from langchain_mistralai import ChatMistralAI
    return ChatMistralAI(
        model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.3,
    )


def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])


def _build_chain(retriever, llm):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough, RunnableLambda

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an expert video learning assistant. Answer the user's question based ONLY on "
            "the video transcript context provided below.\n\n"
            "If the answer is not found in the context, say: "
            "'I could not find this information in the video transcript.'\n\n"
            "Be concise and precise. If referencing a specific moment, mention it clearly.\n\n"
            "Context from video transcript:\n{context}"
        )),
        ("human", "{question}"),
    ])

    return (
        {"context": retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


def build_rag_chain(transcript: str, video_id: str = "default"):
    """Build (or reuse) a per-video RAG chain."""
    try:
        # Reuse existing store if already built for this video
        if vector_store_exists(video_id):
            vs = load_vector_store(video_id)
        else:
            vs = build_vector_store(transcript, video_id)
        retriever = get_retriever(vs, k=4)
        llm = get_llm()
        return _build_chain(retriever, llm)
    except Exception as exc:
        print(f"[RAG disabled for {video_id}] {exc}")
        return None


def ask_question(rag_chain, question: str) -> str:
    if rag_chain is None:
        return "RAG not available."
    return rag_chain.invoke(question)
