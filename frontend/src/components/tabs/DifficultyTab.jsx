const LEVEL_CONFIG = {
  Beginner:     { color: "var(--success)", emoji: "🟢", score_color: "#43D9AD" },
  Intermediate: { color: "var(--warning)", emoji: "🟡", score_color: "#FFB347" },
  Advanced:     { color: "var(--accent)",  emoji: "🔴", score_color: "#FF6584" },
};

export default function DifficultyTab({ video }) {
  const detail = video.difficulty_detail || {};
  const level  = video.difficulty || detail.level || "Intermediate";
  const cfg    = LEVEL_CONFIG[level] || LEVEL_CONFIG.Intermediate;
  const score  = detail.score ?? 5;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>

      {/* ── Level card ── */}
      <div className="neu-card" style={{ padding: 32, textAlign: "center" }}>
        <div style={{ fontSize: "3.5rem", marginBottom: 12 }}>{cfg.emoji}</div>
        <div className="font-display" style={{
          fontSize: "2.2rem", fontWeight: 700, color: cfg.color, marginBottom: 8,
        }}>
          {level}
        </div>
        <p className="text-muted" style={{ fontSize: "0.9rem", maxWidth: 480, margin: "0 auto", lineHeight: 1.7 }}>
          {detail.explanation || "Difficulty analysis not available."}
        </p>
      </div>

      {/* ── Score meter ── */}
      <div className="neu-card" style={{ padding: 28 }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
          <span style={{ fontWeight: 600 }}>Complexity Score</span>
          <span style={{ fontWeight: 700, color: cfg.color, fontSize: "1.1rem" }}>{score}/10</span>
        </div>
        <div className="progress-track">
          <div className="progress-fill" style={{
            width: `${score * 10}%`,
            background: `linear-gradient(90deg, var(--success), ${cfg.score_color})`,
          }} />
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 6 }}>
          <span className="text-muted" style={{ fontSize: "0.75rem" }}>Beginner</span>
          <span className="text-muted" style={{ fontSize: "0.75rem" }}>Advanced</span>
        </div>
      </div>

      {/* ── Target audience + prerequisites ── */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        {detail.target_audience && (
          <div className="neu-card" style={{ padding: 24 }}>
            <h3 style={{ fontWeight: 700, marginBottom: 12, fontSize: "0.95rem", display: "flex", alignItems: "center", gap: 8 }}>
              🎯 Target Audience
            </h3>
            <p style={{ fontSize: "0.9rem", lineHeight: 1.7, color: "var(--text)" }}>
              {detail.target_audience}
            </p>
          </div>
        )}

        {detail.prerequisites?.length > 0 && (
          <div className="neu-card" style={{ padding: 24 }}>
            <h3 style={{ fontWeight: 700, marginBottom: 12, fontSize: "0.95rem", display: "flex", alignItems: "center", gap: 8 }}>
              📋 Prerequisites
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {detail.prerequisites.map((p, i) => (
                <div key={i} style={{
                  display: "flex", alignItems: "center", gap: 8,
                  padding: "8px 12px", borderRadius: 10,
                  background: "var(--bg-elevated)", border: "1px solid var(--border)",
                  fontSize: "0.87rem",
                }}>
                  <span style={{ color: "var(--brand)" }}>•</span> {p}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

    </div>
  );
}
