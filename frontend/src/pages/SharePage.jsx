import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import SummaryTab from "../components/tabs/SummaryTab";

export default function SharePage() {
  const { videoId } = useParams();
  const { data, isLoading } = useQuery({
    queryKey: ["share", videoId],
    queryFn: () => api.get(`/api/share/${videoId}/public`).then((r) => r.data),
  });

  if (isLoading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh" }}>
      <div style={{ width: 40, height: 40, borderRadius: "50%", border: "3px solid var(--brand)", borderTopColor: "transparent" }} className="spin" />
    </div>
  );

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "40px 24px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 32 }}>
        <div style={{ width: 32, height: 32, borderRadius: 8,
          background: "linear-gradient(135deg, var(--brand), var(--accent))",
          display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16 }}>🧠</div>
        <span className="font-display" style={{ fontWeight: 700, fontSize: "1.1rem" }}>VideoMind AI</span>
        <span className="badge badge-brand" style={{ marginLeft: "auto" }}>Public Share</span>
      </div>
      <h1 className="font-display" style={{ fontSize: "1.8rem", fontWeight: 700, marginBottom: 24 }}>
        {data?.title || "Shared Video"}
      </h1>
      {data && <SummaryTab video={data} />}
    </div>
  );
}
