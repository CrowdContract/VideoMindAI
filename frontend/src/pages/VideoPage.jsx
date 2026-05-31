import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Download, Share2 } from "lucide-react";
import toast from "react-hot-toast";
import { getVideo, exportPdf } from "../lib/api";

import SummaryTab     from "../components/tabs/SummaryTab";
import TranscriptTab  from "../components/tabs/TranscriptTab";
import QuizTab        from "../components/tabs/QuizTab";
import FlashcardsTab  from "../components/tabs/FlashcardsTab";
import ChaptersTab    from "../components/tabs/ChaptersTab";
import ChatTab        from "../components/tabs/ChatTab";
import DifficultyTab  from "../components/tabs/DifficultyTab";

const TABS = ["Summary", "Transcript", "Quiz", "Flashcards", "Chapters", "Difficulty", "Chat"];

const TAB_ICONS = {
  Summary:    "📝 ",
  Transcript: "📄 ",
  Quiz:       "🧠 ",
  Flashcards: "🃏 ",
  Chapters:   "📚 ",
  Difficulty: "📊 ",
  Chat:       "💬 ",
};

export default function VideoPage() {
  const { videoId } = useParams();
  const [activeTab, setActiveTab] = useState("Summary");

  const { data: video, isLoading, error } = useQuery({
    queryKey: ["video", videoId],
    queryFn: () => getVideo(videoId),
  });

  const handleShare = () => {
    const url = `${window.location.origin}/share/${videoId}`;
    navigator.clipboard.writeText(url);
    toast.success("Share link copied!");
  };

  if (isLoading) return <LoadingState />;
  if (error)     return <ErrorState />;

  const diffLevel = video.difficulty || "Intermediate";
  const diffBadgeClass =
    diffLevel === "Beginner"     ? "badge-success" :
    diffLevel === "Advanced"     ? "badge-error"   : "badge-warning";

  return (
    <div style={{ maxWidth: 960, margin: "0 auto" }}>

      {/* ── Header ── */}
      <div className="fade-up" style={{ marginBottom: 28 }}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", gap: 8, marginBottom: 10, flexWrap: "wrap" }}>
              <span className="badge badge-brand">{video.language?.toUpperCase() || "EN"}</span>
              <span className={`badge ${diffBadgeClass}`}>{diffLevel}</span>
              <span className="badge badge-success">{video.processing_status}</span>
            </div>
            <h1 className="font-display" style={{ fontSize: "1.6rem", fontWeight: 700, lineHeight: 1.3, marginBottom: 6 }}>
              {video.title || "Untitled Video"}
            </h1>
            {video.channel && (
              <p className="text-muted" style={{ fontSize: "0.88rem" }}>
                {video.channel}
                {video.duration_seconds ? ` · ${Math.round(video.duration_seconds / 60)} min` : ""}
              </p>
            )}
          </div>

          <div style={{ display: "flex", gap: 8 }}>
            <a href={exportPdf(videoId)} target="_blank" rel="noreferrer">
              <button className="neu-btn" style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.85rem" }}>
                <Download size={15} /> PDF
              </button>
            </a>
            <button className="neu-btn" onClick={handleShare}
              style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.85rem" }}>
              <Share2 size={15} /> Share
            </button>
          </div>
        </div>
      </div>

      {/* ── Tabs ── */}
      <div className="fade-up" style={{ animationDelay: "0.1s", marginBottom: 24 }}>
        <div className="tab-list" style={{ overflowX: "auto" }}>
          {TABS.map((tab) => (
            <button
              key={tab}
              className={`tab-trigger ${activeTab === tab ? "active" : ""}`}
              onClick={() => setActiveTab(tab)}
            >
              {TAB_ICONS[tab]}{tab}
            </button>
          ))}
        </div>
      </div>

      {/* ── Tab content ── */}
      <div className="fade-up" style={{ animationDelay: "0.15s" }}>
        {activeTab === "Summary"    && <SummaryTab    video={video} />}
        {activeTab === "Transcript" && <TranscriptTab video={video} />}
        {activeTab === "Quiz"       && <QuizTab       video={video} />}
        {activeTab === "Flashcards" && <FlashcardsTab video={video} />}
        {activeTab === "Chapters"   && <ChaptersTab   video={video} />}
        {activeTab === "Difficulty" && <DifficultyTab video={video} />}
        {activeTab === "Chat"       && <ChatTab       videoId={videoId} />}
      </div>

    </div>
  );
}

function LoadingState() {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "60vh", gap: 16 }}>
      <div style={{ width: 48, height: 48, borderRadius: "50%", border: "3px solid var(--brand)", borderTopColor: "transparent" }} className="spin" />
      <p className="text-muted">Loading video data...</p>
    </div>
  );
}

function ErrorState() {
  return (
    <div style={{ textAlign: "center", padding: 60 }}>
      <p style={{ fontSize: "2rem", marginBottom: 12 }}>😕</p>
      <p style={{ fontWeight: 600, marginBottom: 8 }}>Video not found</p>
      <p className="text-muted">This video may still be processing or doesn't exist.</p>
    </div>
  );
}
