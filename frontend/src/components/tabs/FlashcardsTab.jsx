import { useState } from "react";
import { ChevronLeft, ChevronRight, RotateCcw } from "lucide-react";

export default function FlashcardsTab({ video }) {
  const cards = video.flashcards || [];
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [learned, setLearned] = useState(new Set());

  if (!cards.length) return <Empty />;

  const card = cards[index];
  const prev = () => { setIndex((i) => (i - 1 + cards.length) % cards.length); setFlipped(false); };
  const next = () => { setIndex((i) => (i + 1) % cards.length); setFlipped(false); };
  const toggleLearned = () => setLearned((s) => { const n = new Set(s); n.has(index) ? n.delete(index) : n.add(index); return n; });

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 24 }}>
      {/* Progress */}
      <div style={{ width: "100%", maxWidth: 560 }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8, fontSize: "0.85rem" }}>
          <span className="text-muted">{index + 1} / {cards.length}</span>
          <span className="text-success">{learned.size} learned</span>
        </div>
        <div className="progress-track">
          <div className="progress-fill" style={{ width: `${((index + 1) / cards.length) * 100}%` }} />
        </div>
      </div>

      {/* Card */}
      <div onClick={() => setFlipped(!flipped)} style={{
        width: "100%", maxWidth: 560, minHeight: 240, cursor: "pointer",
        perspective: 1000,
      }}>
        <div style={{
          position: "relative", width: "100%", height: 240,
          transformStyle: "preserve-3d",
          transform: flipped ? "rotateY(180deg)" : "rotateY(0deg)",
          transition: "transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)",
        }}>
          {/* Front */}
          <div className="neu-card" style={{
            position: "absolute", inset: 0, backfaceVisibility: "hidden",
            display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
            padding: 32, textAlign: "center",
          }}>
            {card.chapter && <span className="badge badge-brand" style={{ marginBottom: 12 }}>{card.chapter}</span>}
            <p style={{ fontSize: "1.1rem", fontWeight: 600, lineHeight: 1.6 }}>{card.front}</p>
            <p className="text-muted" style={{ fontSize: "0.78rem", marginTop: 16 }}>Click to reveal answer</p>
          </div>
          {/* Back */}
          <div className="neu-card" style={{
            position: "absolute", inset: 0, backfaceVisibility: "hidden",
            transform: "rotateY(180deg)",
            display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
            padding: 32, textAlign: "center",
            background: "var(--bg-elevated)",
            border: "1px solid rgba(108,99,255,0.3)",
          }}>
            <p style={{ fontSize: "1rem", lineHeight: 1.7, color: "var(--text)" }}>{card.back}</p>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <button className="neu-btn" onClick={prev} style={{ padding: "10px 14px" }}><ChevronLeft size={18} /></button>
        <button className="neu-btn" onClick={() => setFlipped(!flipped)}
          style={{ display: "flex", alignItems: "center", gap: 6, padding: "10px 20px" }}>
          <RotateCcw size={15} /> Flip
        </button>
        <button className={learned.has(index) ? "btn-brand" : "neu-btn"} onClick={toggleLearned}
          style={{ padding: "10px 20px", fontSize: "0.85rem" }}>
          {learned.has(index) ? "✓ Learned" : "Mark Learned"}
        </button>
        <button className="neu-btn" onClick={next} style={{ padding: "10px 14px" }}><ChevronRight size={18} /></button>
      </div>
    </div>
  );
}

function Empty() {
  return (
    <div className="neu-card" style={{ padding: 48, textAlign: "center" }}>
      <p style={{ fontSize: "2rem", marginBottom: 8 }}>🃏</p>
      <p className="text-muted">No flashcards generated yet.</p>
    </div>
  );
}
