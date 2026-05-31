import { Outlet, Link, useLocation } from "react-router-dom";
import { Moon, Sun, History, Home, LogOut, User } from "lucide-react";
import { useStore } from "../store/useStore";

export default function Layout() {
  const { theme, setTheme, user, setUser } = useStore();
  const loc = useLocation();

  const logout = () => {
    window.__accessToken = null;
    setUser(null);
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {/* ── Sidebar ── */}
      <aside style={{
        width: 220, background: "var(--bg-card)", borderRight: "1px solid var(--border)",
        display: "flex", flexDirection: "column", padding: "24px 16px", gap: 8,
        boxShadow: "4px 0 20px rgba(0,0,0,0.3)", position: "sticky", top: 0, height: "100vh",
      }}>
        <Link to="/app" style={{ textDecoration: "none", marginBottom: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: "linear-gradient(135deg, var(--brand), var(--accent))",
              display: "flex", alignItems: "center", justifyContent: "center",
              boxShadow: "var(--glow)", fontSize: 18,
            }}>🧠</div>
            <span className="font-display" style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text)" }}>
              VideoMind
            </span>
          </div>
        </Link>

        <NavItem to="/app" icon={<Home size={18} />} label="Process Video" active={loc.pathname === "/app"} />
        <NavItem to="/history" icon={<History size={18} />} label="History" active={loc.pathname === "/history"} />

        <div style={{ flex: 1 }} />

        {/* Theme toggle */}
        <button className="neu-btn" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          style={{ display: "flex", alignItems: "center", gap: 8, width: "100%", justifyContent: "flex-start" }}>
          {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
          {theme === "dark" ? "Light Mode" : "Dark Mode"}
        </button>

        {/* User */}
        {user ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <div className="neu-card" style={{ padding: "10px 12px", display: "flex", alignItems: "center", gap: 8 }}>
              {user.picture
                ? <img src={user.picture} alt="" style={{ width: 28, height: 28, borderRadius: "50%" }} />
                : <User size={18} />}
              <div style={{ overflow: "hidden" }}>
                <div style={{ fontSize: "0.8rem", fontWeight: 600, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{user.name}</div>
                <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>{user.plan}</div>
              </div>
            </div>
            <button className="neu-btn" onClick={logout}
              style={{ display: "flex", alignItems: "center", gap: 8, width: "100%", justifyContent: "flex-start", color: "var(--accent)" }}>
              <LogOut size={16} /> Sign Out
            </button>
          </div>
        ) : (
          <Link to="/" style={{ textDecoration: "none" }}>
            <button className="btn-brand" style={{ width: "100%" }}>Sign In</button>
          </Link>
        )}
      </aside>

      {/* ── Main ── */}
      <main style={{ flex: 1, overflow: "auto", padding: "32px 40px" }}>
        <Outlet />
      </main>
    </div>
  );
}

function NavItem({ to, icon, label, active }) {
  return (
    <Link to={to} style={{ textDecoration: "none" }}>
      <div style={{
        display: "flex", alignItems: "center", gap: 10,
        padding: "10px 14px", borderRadius: 12,
        background: active ? "var(--bg-elevated)" : "transparent",
        boxShadow: active ? "var(--neu-shadow)" : "none",
        color: active ? "var(--brand)" : "var(--text-muted)",
        fontWeight: active ? 600 : 400, fontSize: "0.9rem",
        transition: "all 0.2s", cursor: "pointer",
      }}>
        {icon} {label}
      </div>
    </Link>
  );
}
