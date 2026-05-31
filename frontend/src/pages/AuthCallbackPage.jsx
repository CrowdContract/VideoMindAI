import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { googleCallback } from "../lib/api";
import { useStore } from "../store/useStore";
import toast from "react-hot-toast";

export default function AuthCallbackPage() {
  const navigate = useNavigate();
  const { setUser } = useStore();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    if (!code) { navigate("/"); return; }

    googleCallback(code, `${window.location.origin}/auth/callback`)
      .then(({ access_token }) => {
        window.__accessToken = access_token;
        return fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/me`, {
          headers: { Authorization: `Bearer ${access_token}` },
        }).then((r) => r.json());
      })
      .then((user) => {
        setUser(user);
        toast.success(`Welcome, ${user.name}!`);
        navigate("/app");
      })
      .catch(() => {
        toast.error("Authentication failed");
        navigate("/");
      });
  }, []);

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh", flexDirection: "column", gap: 16 }}>
      <div style={{ width: 48, height: 48, borderRadius: "50%", border: "3px solid var(--brand)", borderTopColor: "transparent" }} className="spin" />
      <p className="text-muted">Signing you in...</p>
    </div>
  );
}
