import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Brain, Zap, MessageSquare, FileText, BookOpen, BarChart3 } from "lucide-react";
import { useStore } from "../store/useStore";
import { api } from "../lib/api";

const GOOGLE_AUTH_URL = `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/auth/google`;

export default function LandingPage() {
  const navigate = useNavigate();
  const { user } = useStore();

  useEffect(() => {
    if (user) navigate("/app");
  }, [user]);

  const handleGoogle = async () => {
    const { data } = await api.get("/auth/google");
    window.location.href = data.url;
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", overflow: "hidden" }}>
      {/* ── Hero ── */}
      <div style={{ position: "relative", textAlign: "center", padding: "100px 24px 60px" }}>
        {/* Glow orbs */}
        <div style={{
          position: "absolute", top: 80, left: "50%", transform: "translateX(-50%)",
          width: 600, height: 600, borderRadius: "50%",
          background: "radial-gradient(circle, rgba(108,99,255,0.12) 0%, transparent 70%)",
          pointerEvents: "none",
        }} />

        <div className="fade-up" style={{ display: "inline-flex", alignItems: "center", gap: 8,
          background: "rgba(108,99,255,0.1)", border: "1px solid rgba(108,99,255,0.3)",
          borderRadius: 99, padding: "6px 16px", marginBottom: 24, fontSize: "0.85rem", color: "var(--brand)" }}>
          <Zap size={14} /> AI-Powered Video Learning Platform
        </div>

        <h1 className="font-display fade-up" style={{
          fontSize: "clamp(2.5rem, 6vw, 4.5rem)", fontWeight: 700,
          lineHeight: 1.1, marginBottom: 20, animationDelay: "0.1s",
        }}>
          Turn Any YouTube Video<br />
          <span style={{ background: "linear-gradient(135deg, var(--brand), var(--accent))",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            Into Structured Knowledge
          </span>
        </h1>

        <p className="fade-up text-muted" style={{
          fontSize: "1.15rem", maxWidth: 560, margin: "0 auto 40px",
          lineHeight: 1.7, animationDelay: "0.2s",
        }}>
          Transcribe, summarize, quiz yourself, chat with the video, and export everything as PDF — powered by Whisper + Mistral AI.
        </p>

        <div className="fade-up" style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap", animationDelay: "0.3s" }}>
          <button className="btn-brand pulse-glow" onClick={handleGoogle}
            style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "1rem", padding: "14px 32px" }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Continue with Google
          </button>
          <button className="neu-btn" onClick={() => navigate("/app")}
            style={{ fontSize: "1rem", padding: "14px 32px" }}>
            Try as Guest →
          </button>
        </div>
      </div>

      {/* ── Features ── */}
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "0 24px 80px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 20 }}>
          {FEATURES.map((f, i) => (
            <div key={i} className="neu-card fade-up" style={{ padding: 28, animationDelay: `${0.1 * i}s` }}>
              <div style={{
                width: 48, height: 48, borderRadius: 14, marginBottom: 16,
                background: `linear-gradient(135deg, ${f.color}22, ${f.color}44)`,
                display: "flex", alignItems: "center", justifyContent: "center",
                boxShadow: `0 4px 16px ${f.color}33`,
              }}>
                <f.icon size={22} color={f.color} />
              </div>
              <h3 style={{ fontWeight: 600, marginBottom: 8, fontSize: "1rem" }}>{f.title}</h3>
              <p className="text-muted" style={{ fontSize: "0.88rem", lineHeight: 1.6 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const FEATURES = [
  { icon: Brain, color: "#6C63FF", title: "AI Transcription", desc: "Local Whisper model transcribes any YouTube video with high accuracy. Supports Hindi → English translation." },
  { icon: FileText, color: "#43D9AD", title: "Smart Summary", desc: "Mistral AI generates concise bullet-point summaries, key takeaways, action items, and chapter detection." },
  { icon: MessageSquare, color: "#FF6584", title: "Chat with Video", desc: "RAG-powered chat lets you ask any question about the video content with timestamped source references." },
  { icon: BookOpen, color: "#FFB347", title: "Quiz & Flashcards", desc: "Auto-generated MCQs with difficulty levels and spaced-repetition flashcards to reinforce learning." },
  { icon: BarChart3, color: "#6C63FF", title: "Difficulty Estimator", desc: "AI rates video complexity as Beginner / Intermediate / Advanced with a detailed explanation." },
  { icon: FileText, color: "#43D9AD", title: "PDF Export", desc: "One-click export of summary, quiz, flashcards, chapters, and full transcript as a polished PDF." },
];
