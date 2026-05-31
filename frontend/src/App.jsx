import { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import { useStore } from "./store/useStore";
import { getMe } from "./lib/api";

import Layout from "./components/Layout";
import LandingPage from "./pages/LandingPage";
import HomePage from "./pages/HomePage";
import VideoPage from "./pages/VideoPage";
import HistoryPage from "./pages/HistoryPage";
import AuthCallbackPage from "./pages/AuthCallbackPage";
import SharePage from "./pages/SharePage";

const qc = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 60_000 } },
});

export default function App() {
  const { theme, setUser } = useStore();

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    getMe().then(setUser).catch(() => {});
  }, []);

  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/auth/callback" element={<AuthCallbackPage />} />
          <Route path="/share/:videoId" element={<SharePage />} />
          <Route element={<Layout />}>
            <Route path="/app" element={<HomePage />} />
            <Route path="/app/:videoId" element={<VideoPage />} />
            <Route path="/history" element={<HistoryPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "var(--bg-card)",
            color: "var(--text)",
            border: "1px solid var(--border)",
            boxShadow: "var(--neu-shadow)",
            borderRadius: "12px",
          },
        }}
      />
    </QueryClientProvider>
  );
}
