import { useState } from "react";
import { Search } from "lucide-react";

export default function TranscriptTab({ video }) {
  const [search, setSearch] = useState("");
  const text = video.transcript || "";

  const highlighted = search.trim()
    ? text.replace(new RegExp(`(${search.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi"),
        '<mark style="background:rgba(108,99,255,0.3);color:var(--brand);border-radius:3px;padding:0 2px">$1</mark>')
    : text;

  return (
    <div className="neu-card" style={{ padding: 28 }}>
      <div style={{ position: "relative", marginBottom: 20 }}>
        <Search size={16} style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
        <input className="neu-input" style={{ paddingLeft: 38 }}
          placeholder="Search transcript..."
          value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>
      {text ? (
        <div
          style={{ lineHeight: 1.9, fontSize: "0.9rem", color: "var(--text)", maxHeight: 600, overflowY: "auto", paddingRight: 8 }}
          dangerouslySetInnerHTML={{ __html: highlighted.replace(/\n/g, "<br/>") }}
        />
      ) : (
        <p className="text-muted" style={{ textAlign: "center", padding: 32 }}>No transcript available.</p>
      )}
    </div>
  );
}
