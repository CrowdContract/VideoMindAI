import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Clock, Search, Trash2 } from "lucide-react";
import { getHistory } from "../lib/api";

export default function HistoryPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["history", page],
    queryFn: () => getHistory(page),
    retry: false,
    enabled: true,
  });

  const items = (data?.items || []).filter((v) =>
    !search || v.title?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div style={{ maxWidth: 800, margin: "0 auto" }}>
      <div className="fade-up" style={{ marginBottom: 32 }}>
        <h1 className="font-display" style={{ fontSize: "2rem", fontWeight: 700, marginBottom: 8 }}>History</h1>
        <p className="text-muted">Your processed videos</p>
      </div>

      <div className="fade-up" style={{ position: "relative", marginBottom: 24, animationDelay: "0.1s" }}>
        <Search size={16} style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
        <input className="neu-input" style={{ paddingLeft: 42 }}
          placeholder="Search videos..." value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>

      {isLoading ? (
        <div style={{ textAlign: "center", padding: 60 }}>
          <div style={{ width: 40, height: 40, borderRadius: "50%", border: "3px solid var(--brand)", borderTopColor: "transparent", margin: "0 auto" }} className="spin" />
        </div>
      ) : items.length === 0 ? (
        <div className="neu-card" style={{ padding: 60, textAlign: "center" }}>
          <p style={{ fontSize: "2.5rem", marginBottom: 12 }}>📭</p>
          <p style={{ fontWeight: 600, marginBottom: 8 }}>No videos yet</p>
          <p className="text-muted" style={{ marginBottom: 20 }}>Process your first YouTube video to see it here.</p>
          <Link to="/app"><button className="btn-brand">Process a Video</button></Link>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {items.map((v) => (
            <Link key={v.video_id} to={`/app/${v.video_id}`} style={{ textDecoration: "none" }}>
              <div className="neu-card" style={{ padding: 20, display: "flex", gap: 16, alignItems: "center",
                transition: "transform 0.2s", cursor: "pointer" }}
                onMouseEnter={(e) => e.currentTarget.style.transform = "translateX(4px)"}
                onMouseLeave={(e) => e.currentTarget.style.transform = "translateX(0)"}>
                {v.thumbnail_url ? (
                  <img src={v.thumbnail_url} alt="" style={{ width: 80, height: 52, borderRadius: 8, objectFit: "cover", flexShrink: 0 }} />
                ) : (
                  <div style={{ width: 80, height: 52, borderRadius: 8, background: "var(--bg-elevated)",
                    display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.5rem", flexShrink: 0 }}>
                    🎬
                  </div>
                )}
                <div style={{ flex: 1, overflow: "hidden" }}>
                  <p style={{ fontWeight: 600, fontSize: "0.95rem", marginBottom: 4,
                    whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {v.title || v.video_id}
                  </p>
                  <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                    <span className="badge badge-success">{v.processing_status}</span>
                    {v.duration_seconds && (
                      <span className="text-muted" style={{ fontSize: "0.78rem", display: "flex", alignItems: "center", gap: 4 }}>
                        <Clock size={12} /> {Math.round(v.duration_seconds / 60)} min
                      </span>
                    )}
                    {v.created_at && (
                      <span className="text-muted" style={{ fontSize: "0.78rem" }}>
                        {new Date(v.created_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
                <span className="text-brand" style={{ fontSize: "1.2rem" }}>→</span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination */}
      {data?.pages > 1 && (
        <div style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 24 }}>
          {Array.from({ length: data.pages }, (_, i) => i + 1).map((p) => (
            <button key={p} className={p === page ? "btn-brand" : "neu-btn"}
              onClick={() => setPage(p)} style={{ width: 36, height: 36, padding: 0 }}>
              {p}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
