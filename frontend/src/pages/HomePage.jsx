import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Link2, Loader2, Video } from "lucide-react";
import toast from "react-hot-toast";
import { processVideo, getJobStatus } from "../lib/api";

const STEPS = ["pending", "downloading", "transcribing", "generating", "embedding", "completed"];
const STEP_LABELS = {
  pending: "Queued...",
  downloading: "Downloading audio...",
  transcribing: "Transcribing with Whisper...",
  generating: "Generating AI insights...",
  embedding: "Building vector store...",
  completed: "Done!",
  failed: "Failed",
};

export default function HomePage() {
  const navigate = useNavigate();
  const [url, setUrl] = useState("");
  const [language, setLanguage] = useState("english");
  const [jobId, setJobId] = useState(null);
  const [loading, setLoading] = useState(false);

  const { data: job } = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => getJobStatus(jobId),
    enabled: !!jobId,
    // React Query v5: refetchInterval receives the query object, not data directly
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "completed" || status === "failed" ? false : 3000;
    },
  });

  // React Query v5 removed onSuccess — use useEffect instead
  useEffect(() => {
    if (!job) return;
    if (job.status === "completed") {
      toast.success("Processing complete!");
      navigate(`/app/${job.video_id}`);
    }
    if (job.status === "failed") {
      toast.error(job.error || "Processing failed");
      setJobId(null);
      setLoading(false);
    }
  }, [job?.status]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    try {
      const { job_id } = await processVideo(url.trim(), language);
      setJobId(job_id);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to start processing");
      setLoading(false);
    }
  };

  const progress = job?.progress || 0;
  const isProcessing = loading || (job && job.status !== "completed" && job.status !== "failed");

  return (
    <div style={{ maxWidth: 680, margin: "0 auto" }}>
      <div className="fade-up" style={{ marginBottom: 40 }}>
        <h1 className="font-display" style={{ fontSize: "2rem", fontWeight: 700, marginBottom: 8 }}>
          Process a Video
        </h1>
        <p className="text-muted">Paste a YouTube URL and let AI do the rest.</p>
      </div>

      {/* ── Input card ── */}
      <div className="neu-card fade-up" style={{ padding: 32, marginBottom: 24, animationDelay: "0.1s" }}>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div style={{ position: "relative" }}>
            <Video size={18} style={{
              position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)",
              color: "var(--accent)",
            }} />
            <input
              className="neu-input"
              style={{ paddingLeft: 44 }}
              placeholder="https://www.youtube.com/watch?v=..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isProcessing}
            />
          </div>

          <div style={{ display: "flex", gap: 8 }}>
            {["english", "hinglish"].map((lang) => (
              <button key={lang} type="button"
                className={language === lang ? "btn-brand" : "neu-btn"}
                style={{ flex: 1, padding: "10px 0", fontSize: "0.85rem" }}
                onClick={() => setLanguage(lang)}
                disabled={isProcessing}>
                {lang.charAt(0).toUpperCase() + lang.slice(1)}
              </button>
            ))}
          </div>

          <button className="btn-brand" type="submit" disabled={isProcessing || !url.trim()}
            style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}>
            {isProcessing
              ? <><Loader2 size={18} className="spin" /> Processing...</>
              : <><Link2 size={18} /> Analyze Video</>}
          </button>
        </form>
      </div>

      {/* ── Progress ── */}
      {isProcessing && job && (
        <div className="neu-card fade-up" style={{ padding: 28 }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
            <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>
              {STEP_LABELS[job.status] || job.current_step}
            </span>
            <span className="text-brand" style={{ fontWeight: 700 }}>{progress}%</span>
          </div>
          <div className="progress-track">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <div style={{ display: "flex", gap: 6, marginTop: 16, flexWrap: "wrap" }}>
            {STEPS.map((step) => {
              const idx = STEPS.indexOf(step);
              const curIdx = STEPS.indexOf(job.status);
              const done = idx < curIdx;
              const active = idx === curIdx;
              return (
                <span key={step} style={{
                  fontSize: "0.72rem", padding: "3px 10px", borderRadius: 99,
                  background: done ? "rgba(67,217,173,0.15)" : active ? "rgba(108,99,255,0.2)" : "var(--bg-input)",
                  color: done ? "var(--success)" : active ? "var(--brand)" : "var(--text-muted)",
                  fontWeight: active ? 600 : 400,
                  border: active ? "1px solid var(--brand)" : "1px solid transparent",
                }}>
                  {done ? "✓ " : active ? "⟳ " : ""}{STEP_LABELS[step]}
                </span>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Tips ── */}
      {!isProcessing && (
        <div className="fade-up" style={{ animationDelay: "0.2s" }}>
          <p className="text-muted" style={{ fontSize: "0.82rem", marginBottom: 12 }}>Try these examples:</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {EXAMPLES.map((ex) => (
              <button key={ex.url} className="neu-btn" onClick={() => setUrl(ex.url)}
                style={{ textAlign: "left", padding: "10px 16px", fontSize: "0.85rem" }}>
                <span className="text-brand">▶</span> {ex.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

const EXAMPLES = [
  { url: "https://www.youtube.com/watch?v=7HSSR1n8dgc", label: "System Design Interview — Basics" },
  { url: "https://www.youtube.com/watch?v=Lg-meK5IU8Q", label: "ADK vs RAG: How to Choose" },
];
