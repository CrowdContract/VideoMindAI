export default function ChaptersTab({ video }) {
  const chapters = video.chapters || [];
  if (!chapters.length) return <Empty />;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {chapters.map((ch, i) => (
        <div key={i} className="neu-card" style={{ padding: 20, display: "flex", gap: 16, alignItems: "flex-start" }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10, flexShrink: 0,
            background: "linear-gradient(135deg, var(--brand), var(--brand-dark))",
            display: "flex", alignItems: "center", justifyContent: "center",
            color: "#fff", fontWeight: 700, fontSize: "0.85rem",
            boxShadow: "var(--glow)",
          }}>
            {i + 1}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6, flexWrap: "wrap" }}>
              <span style={{ fontWeight: 600, fontSize: "0.95rem" }}>{ch.title}</span>
              {ch.start_time && (
                <span className="badge badge-brand" style={{ fontSize: "0.7rem" }}>
                  {ch.start_time} – {ch.end_time}
                </span>
              )}
            </div>
            {ch.summary && (
              <p className="text-muted" style={{ fontSize: "0.87rem", lineHeight: 1.6 }}>{ch.summary}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function Empty() {
  return (
    <div className="neu-card" style={{ padding: 48, textAlign: "center" }}>
      <p style={{ fontSize: "2rem", marginBottom: 8 }}>📚</p>
      <p className="text-muted">No chapters detected yet.</p>
    </div>
  );
}
