import ReactMarkdown from "react-markdown";
import { CheckCircle2, Lightbulb, AlertCircle } from "lucide-react";

export default function SummaryTab({ video }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Summary */}
      <div className="neu-card" style={{ padding: 28 }}>
        <h2 style={{ fontWeight: 700, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ color: "var(--brand)" }}>📝</span> Summary
        </h2>
        <div style={{ lineHeight: 1.8, color: "var(--text)", fontSize: "0.95rem" }}>
          <ReactMarkdown>{video.summary || "No summary available."}</ReactMarkdown>
        </div>
      </div>

      {/* Takeaways */}
      {video.takeaways?.length > 0 && (
        <div className="neu-card" style={{ padding: 28 }}>
          <h2 style={{ fontWeight: 700, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
            <Lightbulb size={18} color="var(--warning)" /> Key Takeaways
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {video.takeaways.map((t, i) => (
              <div key={i} style={{
                display: "flex", alignItems: "flex-start", gap: 10,
                padding: "12px 16px", borderRadius: 12,
                background: "var(--bg-elevated)", border: "1px solid var(--border)",
              }}>
                <CheckCircle2 size={16} color="var(--success)" style={{ marginTop: 2, flexShrink: 0 }} />
                <span style={{ fontSize: "0.9rem", lineHeight: 1.6 }}>{t}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Items + Key Decisions side by side */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        {video.action_items && (
          <div className="neu-card" style={{ padding: 24 }}>
            <h3 style={{ fontWeight: 700, marginBottom: 12, display: "flex", alignItems: "center", gap: 8, fontSize: "0.95rem" }}>
              <AlertCircle size={16} color="var(--accent)" /> Action Items
            </h3>
            <div style={{ fontSize: "0.88rem", lineHeight: 1.8, color: "var(--text)" }}>
              <ReactMarkdown>{video.action_items}</ReactMarkdown>
            </div>
          </div>
        )}
        {video.key_decisions && (
          <div className="neu-card" style={{ padding: 24 }}>
            <h3 style={{ fontWeight: 700, marginBottom: 12, display: "flex", alignItems: "center", gap: 8, fontSize: "0.95rem" }}>
              <span style={{ color: "var(--brand)" }}>🔑</span> Key Decisions
            </h3>
            <div style={{ fontSize: "0.88rem", lineHeight: 1.8, color: "var(--text)" }}>
              <ReactMarkdown>{video.key_decisions}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>

      {/* Open Questions */}
      {video.open_questions && (
        <div className="neu-card" style={{ padding: 24 }}>
          <h3 style={{ fontWeight: 700, marginBottom: 12, display: "flex", alignItems: "center", gap: 8, fontSize: "0.95rem" }}>
            <span style={{ color: "var(--warning)" }}>❓</span> Open Questions
          </h3>
          <div style={{ fontSize: "0.88rem", lineHeight: 1.8, color: "var(--text)" }}>
            <ReactMarkdown>{video.open_questions}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
