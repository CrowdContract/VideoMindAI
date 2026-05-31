"""FastAPI application entry point."""
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.auth import (
    create_access_token, create_refresh_token,
    exchange_google_code, get_current_user,
    require_user, upsert_google_user, decode_token,
)
from backend.config import get_settings
from backend.database import ensure_indexes, get_db, get_redis
from backend.models import (
    ChatRequest, HealthResponse, JobStatus,
    TokenResponse, VideoProcessRequest,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Non-blocking startup — don't crash if DB/Redis is slow to connect
    try:
        await ensure_indexes()
    except Exception as e:
        print(f"[startup] Index creation skipped: {e}")
    yield


app = FastAPI(title="VideoMind AI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health():
    redis_ok, db_ok = False, False
    try:
        r = await get_redis()
        await r.ping()
        redis_ok = True
    except Exception:
        pass
    try:
        db = get_db()
        await db.command("ping")
        db_ok = True
    except Exception:
        pass
    return HealthResponse(status="ok", redis=redis_ok, db=db_ok)


# ── Auth ──────────────────────────────────────────────────────────────────────
@app.get("/auth/google")
async def google_auth_redirect():
    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback"
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
    )
    return {"url": url}


@app.post("/auth/google/callback")
async def google_callback(payload: dict, response: Response):
    code = payload.get("code")
    redirect_uri = payload.get("redirect_uri", f"{settings.FRONTEND_URL}/auth/callback")
    profile = await exchange_google_code(code, redirect_uri)
    user = await upsert_google_user(profile)
    access = create_access_token(user["_id"])
    refresh = create_refresh_token(user["_id"])
    response.set_cookie("refresh_token", refresh, httponly=True, samesite="lax", max_age=604800)
    return TokenResponse(access_token=access)


@app.post("/auth/refresh")
async def refresh_token(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    access = create_access_token(payload["sub"])
    return TokenResponse(access_token=access)


@app.get("/api/me")
async def get_me(user=Depends(require_user)):
    return {
        "id": user["_id"], "email": user["email"],
        "name": user["name"], "picture": user.get("picture", ""),
        "plan": user.get("plan", "free"),
    }


# ── Video Processing ──────────────────────────────────────────────────────────
@app.post("/api/process", status_code=202)
async def process_video(
    req: VideoProcessRequest,
    user=Depends(get_current_user),
):
    # Validate YouTube URL
    import re
    if not re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", req.url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    job_id = str(uuid.uuid4())
    db = get_db()
    await db.jobs.insert_one({
        "job_id": job_id,
        "user_id": user["_id"] if user else None,
        "url": req.url,
        "status": "pending",
        "progress": 0,
        "current_step": "Queued...",
        "error": None,
        "video_id": None,
        "created_at": datetime.utcnow(),
    })
    # Lazy import to avoid slow startup
    from backend.worker import process_video_task
    process_video_task.delay(job_id, req.url, req.language, user["_id"] if user else None)
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}/status", response_model=JobStatus)
async def job_status(job_id: str):
    db = get_db()
    job = await db.jobs.find_one({"job_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job["id"] = str(job["_id"])
    return JobStatus(**{k: v for k, v in job.items() if k != "_id"})


@app.get("/api/videos/{video_id}")
async def get_video(video_id: str, user=Depends(get_current_user)):
    db = get_db()
    # Check Redis cache first
    redis = await get_redis()
    cached = await redis.get(f"video:{video_id}")
    if cached:
        import json
        return json.loads(cached)
    video = await db.videos.find_one({"video_id": video_id}, {"_id": 0})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    import json
    await redis.setex(f"video:{video_id}", 259200, json.dumps(video, default=str))  # 3 days
    return video


@app.delete("/api/videos/{video_id}")
async def delete_video(video_id: str, user=Depends(require_user)):
    db = get_db()
    await db.user_videos.delete_one({"user_id": user["_id"], "video_id": video_id})
    redis = await get_redis()
    await redis.delete(f"video:{video_id}")
    return {"deleted": True}


# ── Content endpoints ─────────────────────────────────────────────────────────
@app.get("/api/videos/{video_id}/summary")
async def get_summary(video_id: str):
    db = get_db()
    doc = await db.videos.find_one({"video_id": video_id}, {"summary": 1, "takeaways": 1})
    if not doc:
        raise HTTPException(status_code=404)
    return {"summary": doc.get("summary", ""), "takeaways": doc.get("takeaways", [])}


@app.get("/api/videos/{video_id}/quiz")
async def get_quiz(video_id: str):
    db = get_db()
    doc = await db.videos.find_one({"video_id": video_id}, {"quiz": 1})
    if not doc:
        raise HTTPException(status_code=404)
    return {"quiz": doc.get("quiz", [])}


@app.get("/api/videos/{video_id}/flashcards")
async def get_flashcards(video_id: str):
    db = get_db()
    doc = await db.videos.find_one({"video_id": video_id}, {"flashcards": 1})
    if not doc:
        raise HTTPException(status_code=404)
    return {"flashcards": doc.get("flashcards", [])}


@app.get("/api/videos/{video_id}/chapters")
async def get_chapters(video_id: str):
    db = get_db()
    doc = await db.videos.find_one({"video_id": video_id}, {"chapters": 1})
    if not doc:
        raise HTTPException(status_code=404)
    return {"chapters": doc.get("chapters", [])}


@app.get("/api/videos/{video_id}/transcript")
async def get_transcript(video_id: str):
    db = get_db()
    doc = await db.videos.find_one({"video_id": video_id}, {"transcript": 1, "transcript_chunks": 1})
    if not doc:
        raise HTTPException(status_code=404)
    return {"transcript": doc.get("transcript", ""), "chunks": doc.get("transcript_chunks", [])}


@app.post("/api/videos/{video_id}/generate")
async def regenerate(video_id: str, user=Depends(require_user)):
    """Force-regenerate all AI outputs for a video."""
    db = get_db()
    doc = await db.videos.find_one({"video_id": video_id}, {"transcript": 1, "url": 1})
    if not doc:
        raise HTTPException(status_code=404)
    job_id = str(uuid.uuid4())
    await db.jobs.insert_one({
        "job_id": job_id, "user_id": user["_id"],
        "url": doc["url"], "status": "pending",
        "progress": 0, "current_step": "Queued for regeneration...",
        "error": None, "video_id": video_id,
        "created_at": datetime.utcnow(),
    })
    process_video_task.delay(job_id, doc["url"], "english", user["_id"])
    return {"job_id": job_id}


# ── Chat (RAG) ────────────────────────────────────────────────────────────────
@app.post("/api/videos/{video_id}/chat")
async def chat(video_id: str, req: ChatRequest, user=Depends(get_current_user)):
    db = get_db()
    doc = await db.videos.find_one({"video_id": video_id}, {"transcript": 1})
    if not doc:
        raise HTTPException(status_code=404)

    from core.rag_engine import build_rag_chain, ask_question
    # Pass video_id so each video gets its own vector store
    rag = build_rag_chain(doc["transcript"], video_id=video_id)
    answer = ask_question(rag, req.question)

    # Persist chat history — guests use video_id as session key
    user_id = user["_id"] if user else f"guest_{video_id}"
    await db.chat_sessions.update_one(
        {"user_id": user_id, "video_id": video_id},
        {"$push": {"messages": {
            "$each": [
                {"role": "user", "content": req.question, "timestamp": datetime.utcnow().isoformat()},
                {"role": "assistant", "content": answer, "timestamp": datetime.utcnow().isoformat()},
            ]
        }}, "$setOnInsert": {"created_at": datetime.utcnow()}},
        upsert=True,
    )
    return {"answer": answer, "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/videos/{video_id}/chat/history")
async def chat_history(video_id: str, user=Depends(get_current_user)):
    db = get_db()
    # Works for both authenticated users and guests
    user_id = user["_id"] if user else f"guest_{video_id}"
    session = await db.chat_sessions.find_one(
        {"user_id": user_id, "video_id": video_id}, {"_id": 0}
    )
    return {"messages": session.get("messages", []) if session else []}


@app.delete("/api/videos/{video_id}/chat/history")
async def clear_chat(video_id: str, user=Depends(get_current_user)):
    db = get_db()
    user_id = user["_id"] if user else f"guest_{video_id}"
    await db.chat_sessions.delete_one({"user_id": user_id, "video_id": video_id})
    return {"cleared": True}


# ── History Dashboard ─────────────────────────────────────────────────────────
@app.get("/api/history")
async def get_history(user=Depends(require_user), page: int = 1, limit: int = 20):
    db = get_db()
    skip = (page - 1) * limit
    cursor = db.user_videos.find(
        {"user_id": user["_id"]},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit)
    items = await cursor.to_list(length=limit)
    # Enrich with video metadata
    video_ids = [i["video_id"] for i in items]
    videos = await db.videos.find(
        {"video_id": {"$in": video_ids}},
        {"video_id": 1, "title": 1, "thumbnail_url": 1, "duration_seconds": 1,
         "processing_status": 1, "created_at": 1, "_id": 0}
    ).to_list(length=limit)
    meta = {v["video_id"]: v for v in videos}
    for item in items:
        item.update(meta.get(item["video_id"], {}))
    total = await db.user_videos.count_documents({"user_id": user["_id"]})
    return {"items": items, "total": total, "page": page, "pages": (total + limit - 1) // limit}


# ── PDF Export ────────────────────────────────────────────────────────────────
@app.get("/api/videos/{video_id}/export/pdf")
async def export_pdf(video_id: str):
    db = get_db()
    redis = await get_redis()

    cached_pdf = await redis.get(f"pdf:{video_id}")
    if cached_pdf:
        import base64
        pdf_bytes = base64.b64decode(cached_pdf)
        return Response(content=pdf_bytes, media_type="application/pdf",
                        headers={"Content-Disposition": f"attachment; filename={video_id}.pdf"})

    doc = await db.videos.find_one({"video_id": video_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404)

    from backend.pdf_export import generate_pdf
    pdf_bytes = generate_pdf(doc)

    import base64
    await redis.setex(f"pdf:{video_id}", 3600, base64.b64encode(pdf_bytes).decode())
    return Response(content=pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename={video_id}.pdf"})


# ── Public Share ──────────────────────────────────────────────────────────────
@app.get("/api/share/{video_id}/public")
async def public_share(video_id: str):
    db = get_db()
    doc = await db.videos.find_one(
        {"video_id": video_id},
        {"transcript": 0, "_id": 0}  # exclude raw transcript for public view
    )
    if not doc:
        raise HTTPException(status_code=404)
    return doc
