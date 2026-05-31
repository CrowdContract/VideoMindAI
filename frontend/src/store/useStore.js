import { create } from "zustand";

export const useStore = create((set) => ({
  user: null,
  theme: localStorage.getItem("theme") || "dark",
  setUser: (user) => set({ user }),
  setTheme: (theme) => {
    localStorage.setItem("theme", theme);
    set({ theme });
  },
}));
