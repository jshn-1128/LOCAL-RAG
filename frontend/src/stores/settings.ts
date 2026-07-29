import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Settings } from "@/types";

interface SettingsState extends Settings {
  setTheme: (theme: "dark" | "light") => void;
  setBackendUrl: (url: string) => void;
  setTemperature: (temp: number) => void;
  setTopK: (k: number) => void;
  setScoreThreshold: (threshold: number) => void;
  setPreferredModel: (model: string) => void;
  reset: () => void;
}

const defaults = {
  theme: "dark" as const,
  backend_url: "http://localhost:8000",
  temperature: 0.7,
  top_k: 4,
  score_threshold: 0.0,
  preferred_model: "llama3.2",
};

export const useSettings = create<SettingsState>()(
  persist(
    (set) => ({
      ...defaults,
      setTheme: (theme) => set({ theme }),
      setBackendUrl: (backend_url) => set({ backend_url }),
      setTemperature: (temperature) => set({ temperature }),
      setTopK: (top_k) => set({ top_k }),
      setScoreThreshold: (score_threshold) => set({ score_threshold }),
      setPreferredModel: (preferred_model) => set({ preferred_model }),
      reset: () => {
        useSettings.persist.clearStorage();
        set({ ...defaults });
      },
    }),
    {
      name: "local-rag-settings",
      partialize: (state) => ({
        theme: state.theme,
        backend_url: state.backend_url,
        temperature: state.temperature,
        top_k: state.top_k,
        score_threshold: state.score_threshold,
        preferred_model: state.preferred_model,
      }),
    },
  ),
);
