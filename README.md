# VideoMind AI 🧠

> Turn any YouTube video into structured knowledge — transcribe, summarize, quiz, chat, and export.

**Live Demo:** [video-mind-ai.vercel.app](https://video-mind-ai.vercel.app) &nbsp;|&nbsp; **API:** [videomindai.onrender.com](https://videomindai.onrender.com/health)

---

## What it does

Paste a YouTube URL and VideoMind AI will:

- 🎙️ **Transcribe** the audio using local Whisper (supports Hindi → English via Sarvam AI)
- 📝 **Summarize** with key takeaways, action items, and key decisions
- 🧠 **Generate a Quiz** — 8 MCQs with difficulty levels and explanations
- 🃏 **Create Flashcards** — spaced-repetition Q&A pairs
- 📚 **Detect Chapters** — auto-segment the video into logical sections with timestamps
- 📊 **Estimate Difficulty** — Beginner / Intermediate / Advanced with prerequisites
- 💬 **Chat with the Video** — RAG-powered Q&A over the transcript (Mistral + ChromaDB)
- 📄 **Export PDF** — full report with summary, quiz, flashcards, chapters, and transcript
- 🔗 **Share** — public read-only link for any processed video

---

## Tech Stack

### Frontend
| Tech | Purpose |
|---|---|
| React + Vite | UI framework |
| TanStack Query | Server state + polling |
| Zustand | Client state (auth, theme) |
| React Router v6 | Routing |
| Lucide React | Icons |
| CSS Variables | Neumorphism + shadow design system |

### Backend
| Tech | Purpose |
|---|---|
| FastAPI | REST API |
| Celery + Redis | Async background job queue |
| Motor (async PyMongo) | MongoDB async driver |
| faster-whisper | Local audio transcription |
| LangChain + Mistral AI | LLM summarization, extraction, RAG |
| ChromaDB + HuggingFace | Vector store for RAG |
| python-jose | JWT authentication |
| reportlab | PDF generation |

### Infrastructure
| Service | Platform |
|---|---|
| Frontend | Vercel (free) |
| Backend API | Render (free) |
| Celery Worker | Render Background Worker |
| Database | MongoDB Atlas M0 (free) |
| Cache / Queue | Upstash Redis (free) |

---

## Architecture

```
Browser (React)
      │
      ▼
FastAPI (Render)  ──────────────────────────────────────────┐
      │                                                      │
      ├── POST /api/process ──► Celery Worker (Render)       │
      │                              │                       │
      │                    ┌─────────▼──────────┐           │
      │                    │  yt-dlp (download) │           │
      │                    │  faster-whisper    │           │
      │                    │  Mistral AI (LLM)  │           │
      │                    │  ChromaDB (RAG)    │           │
      │                    └─────────┬──────────┘           │
      │                              │                       │
      │                    MongoDB Atlas ◄────────────────────┘
      │                    Upstash Redis (cache + queue)
      │
      ├── GET /api/videos/{id}  ──► Redis cache → MongoDB
      ├── POST /api/videos/{id}/chat  ──► RAG chain
      └── GET /api/videos/{id}/export/pdf  ──► reportlab
```

---

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- ffmpeg (`winget install ffmpeg`)
- Redis (local or Upstash)
- MongoDB (local or Atlas)

### Setup

```bash
# Clone
git clone https://github.com/CrowdContract/VideoMindAI.git
cd VideoMindAI

# Python environment
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Environment variables

Copy `.env.example` to `.env` and fill in:

```env
MISTRAL_API_KEY=your_key
MONGODB_URI=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379
JWT_SECRET=your_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FRONTEND_URL=http://localhost:5173
```

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

### Run

```bash
# Terminal 1 — Backend API
.venv\Scripts\uvicorn.exe backend.main:app --reload --port 8000

# Terminal 2 — Celery Worker
.venv\Scripts\celery.exe -A backend.worker.celery_app worker --loglevel=info --pool=solo

# Terminal 3 — Frontend
cd frontend && npm run dev
```

Open http://localhost:5173

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/process` | Submit YouTube URL for processing |
| `GET` | `/api/jobs/{id}/status` | Poll job progress |
| `GET` | `/api/videos/{id}` | Get all video data |
| `GET` | `/api/videos/{id}/summary` | Summary + takeaways |
| `GET` | `/api/videos/{id}/quiz` | Quiz questions |
| `GET` | `/api/videos/{id}/flashcards` | Flashcards |
| `GET` | `/api/videos/{id}/chapters` | Chapter list |
| `GET` | `/api/videos/{id}/transcript` | Full transcript |
| `POST` | `/api/videos/{id}/chat` | RAG chat |
| `GET` | `/api/videos/{id}/export/pdf` | Download PDF |
| `GET` | `/api/share/{id}/public` | Public share view |
| `GET` | `/api/history` | User video history |
| `GET` | `/health` | Health check |

---

## Deployment

### Render (Backend + Worker)

1. Connect GitHub repo to Render
2. Create **Web Service** with:
   - Build: `chmod +x build.sh && ./build.sh`
   - Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
3. Create **Background Worker** with:
   - Start: `celery -A backend.worker.celery_app worker --loglevel=info --pool=solo --concurrency=1`
4. Add all environment variables from `.env`

### Vercel (Frontend)

1. Import repo → set Root Directory to `frontend`
2. Add env var: `VITE_API_URL=https://your-render-url.onrender.com`
3. Deploy

---

## Resume Description

> Built a full-stack AI video learning platform using React + FastAPI, processing YouTube videos into structured learning materials (summaries, quizzes, flashcards). Implemented RAG pipeline using faster-whisper transcription, LangChain + Mistral AI, and ChromaDB vector search for timestamped Q&A over video content. Designed async job processing with Celery + Redis, reducing perceived wait time and enabling parallel LLM task execution. Deployed on Vercel + Render with MongoDB Atlas and Upstash Redis.

---

## Project Structure

```
VideoMindAI/
├── backend/
│   ├── main.py          # FastAPI routes
│   ├── worker.py        # Celery tasks
│   ├── generators.py    # Quiz, flashcards, chapters, difficulty
│   ├── pdf_export.py    # PDF generation
│   ├── auth.py          # JWT + Google OAuth
│   ├── database.py      # MongoDB + Redis
│   ├── models.py        # Pydantic models
│   └── config.py        # Settings
├── core/
│   ├── transcriber.py   # faster-whisper
│   ├── summarize.py     # LangChain summarization
│   ├── extractor.py     # Action items, decisions, questions
│   ├── rag_engine.py    # RAG chain
│   └── vector_store.py  # Per-video ChromaDB
├── utils/
│   └── audio_processor.py  # yt-dlp + ffmpeg
├── frontend/
│   ├── src/
│   │   ├── pages/       # Landing, Home, Video, History, Share
│   │   ├── components/  # Layout, tabs (Summary, Quiz, Chat...)
│   │   ├── lib/api.js   # Axios client
│   │   └── store/       # Zustand store
│   └── vercel.json
├── build.sh             # Render build script
├── render.yaml          # Render config
└── requirements.txt
```

---

## License

MIT
