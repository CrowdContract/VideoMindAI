import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Trash2 } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { chatWithVideo, getChatHistory, api } from "../../lib/api";
import ReactMarkdown from "react-markdown";

export default function ChatTab({ videoId }) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const bottomRef = useRef(null);
  const qc = useQueryClient();

  // Load history
  useQuery({
    queryKey: ["chat-history", videoId],
    queryFn: () => getChatHistory(videoId),
    onSuccess: (data) => { if (data.messages?.length) setMessages(data.messages); },
  });

  const { mutate: sendMsg, isLoading } = useMutation({
    mutationFn: (q) => chatWithVideo(videoId, q),
    onMutate: (q) => {
      setMessages((m) => [...m, { role: "user", content: q }]);
      setInput("");
    },
    onSuccess: (data) => {
      setMessages((m) => [...m, { role: "assistant", content: data.answer, timestamp: data.timestamp }]);
    },
    onError: () => {
      setMessages((m) => [...m, { role: "assistant", content: "Sorry, something went wrong. Please try again." }]);
    },
  });

  const clearHistory = async () => {
    await api.delete(`/api/videos/${videoId}/chat/history`);
    setMessages([]);
    qc.invalidateQueries(["chat-history", videoId]);
  };

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const handleSend = () => { if (input.trim() && !isLoading) sendMsg(input.trim()); };

  return (
    <div className="neu-card" style={{ display: "flex", flexDirection: "column", height: 600 }}>
      {/* Header */}
      <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--border)",
        display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontWeight: 600, fontSize: "0.95rem" }}>💬 Chat with Video</span>
        {messages.length > 0 && (
          <button className="neu-btn" onClick={clearHistory}
            style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.78rem", padding: "6px 12px", color: "var(--accent)" }}>
            <Trash2 size={13} /> Clear
          </button>
        )}
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "20px", display: "flex", flexDirection: "column", gap: 14 }}>
        {messages.length === 0 && (
          <div style={{ textAlign: "center", margin: "auto" }}>
            <p style={{ fontSize: "2rem", marginBottom: 8 }}>💬</p>
            <p className="text-muted" style={{ fontSize: "0.9rem" }}>Ask anything about this video</p>
            <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 20 }}>
              {SUGGESTIONS.map((s) => (
                <button key={s} className="neu-btn" onClick={() => sendMsg(s)}
                  style={{ fontSize: "0.83rem", padding: "8px 14px" }}>{s}</button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} style={{
            display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
          }}>
            <div style={{
              maxWidth: "80%", padding: "12px 16px", borderRadius: msg.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
              background: msg.role === "user"
                ? "linear-gradient(135deg, var(--brand), var(--brand-dark))"
                : "var(--bg-elevated)",
              color: msg.role === "user" ? "#fff" : "var(--text)",
              border: msg.role === "assistant" ? "1px solid var(--border)" : "none",
              fontSize: "0.9rem", lineHeight: 1.7,
              boxShadow: msg.role === "user" ? "0 4px 16px rgba(108,99,255,0.3)" : "var(--neu-shadow)",
            }}>
              <ReactMarkdown>{msg.content}</ReactMarkdown>
              {msg.timestamp && (
                <div style={{ fontSize: "0.7rem", opacity: 0.6, marginTop: 4, textAlign: "right" }}>
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
            <div style={{ width: 32, height: 32, borderRadius: "50%",
              background: "var(--bg-elevated)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              🧠
            </div>
            <div style={{ display: "flex", gap: 4 }}>
              {[0, 1, 2].map((i) => (
                <div key={i} style={{
                  width: 8, height: 8, borderRadius: "50%", background: "var(--brand)",
                  animation: `pulse-glow 1.2s ${i * 0.2}s infinite`,
                }} />
              ))}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{ padding: "16px 20px", borderTop: "1px solid var(--border)", display: "flex", gap: 10 }}>
        <input className="neu-input" placeholder="Ask about the video..."
          value={input} onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
          disabled={isLoading} />
        <button className="btn-brand" onClick={handleSend} disabled={isLoading || !input.trim()}
          style={{ padding: "12px 16px", flexShrink: 0 }}>
          {isLoading ? <Loader2 size={18} className="spin" /> : <Send size={18} />}
        </button>
      </div>
    </div>
  );
}

const SUGGESTIONS = [
  "What are the main topics covered?",
  "Summarize the key points in 3 bullets",
  "What action items were mentioned?",
];
