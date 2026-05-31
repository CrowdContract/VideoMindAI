import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: BASE, withCredentials: true });

// Attach access token from memory store
api.interceptors.request.use((config) => {
  const token = window.__accessToken;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-refresh on 401
api.interceptors.response.use(
  (r) => r,
  async (err) => {
    const status = err.response?.status;
    const url = err.config?.url || "";
    // Don't retry refresh endpoint itself, or /api/me, or /api/history
    const noRetry = url.includes("/auth/refresh") || url.includes("/api/me") || url.includes("/api/history");
    if (status === 401 && !err.config._retry && !noRetry) {
      err.config._retry = true;
      try {
        const { data } = await axios.post(`${BASE}/auth/refresh`, {}, { withCredentials: true });
        window.__accessToken = data.access_token;
        err.config.headers.Authorization = `Bearer ${data.access_token}`;
        return api(err.config);
      } catch {
        window.__accessToken = null;
      }
    }
    return Promise.reject(err);
  }
);

// ── API helpers ───────────────────────────────────────────────────────────────
export const processVideo = (url, language) =>
  api.post("/api/process", { url, language }).then((r) => r.data);

export const getJobStatus = (jobId) =>
  api.get(`/api/jobs/${jobId}/status`).then((r) => r.data);

export const getVideo = (videoId) =>
  api.get(`/api/videos/${videoId}`).then((r) => r.data);

export const getHistory = (page = 1) =>
  api.get(`/api/history?page=${page}`).then((r) => r.data);

export const chatWithVideo = (videoId, question) =>
  api.post(`/api/videos/${videoId}/chat`, { question }).then((r) => r.data);

export const getChatHistory = (videoId) =>
  api.get(`/api/videos/${videoId}/chat/history`).then((r) => r.data);

export const getMe = () => api.get("/api/me").then((r) => r.data);

export const googleCallback = (code, redirectUri) =>
  api.post("/auth/google/callback", { code, redirect_uri: redirectUri }).then((r) => r.data);

export const exportPdf = (videoId) =>
  `${BASE}/api/videos/${videoId}/export/pdf`;
