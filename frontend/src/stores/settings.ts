import { create } from "zustand";
import type { Settings } from "@/types";

export interface SettingsState extends Settings {
  dirty: boolean;
  hydrated: boolean;
  setTheme: (theme: "dark" | "light") => void;
  setBackendUrl: (url: string) => void;
  setTemperature: (temp: number) => void;
  setTopK: (k: number) => void;
  setScoreThreshold: (threshold: number) => void;
  setPreferredModel: (model: string) => void;
  save: () => void;
  reset: () => void;
  hydrate: () => void;
}

const STORAGE_KEY = "local-rag-settings";
const defaults = {
  theme: "dark" as const,
  backend_url: "http://localhost:8000",
  temperature: 0.7,
  top_k: 4,
  score_threshold: 0.0,
  preferred_model: "llama3.2",
};

function readStorage(): Partial<Settings> | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function writeStorage(state: SettingsState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      theme: state.theme,
      backend_url: state.backend_url,
      temperature: state.temperature,
      top_k: state.top_k,
      score_threshold: state.score_threshold,
      preferred_model: state.preferred_model,
    }));
  } catch {}
}

export const useSettings = create<SettingsState>((set, get) => ({
  ...defaults,
  dirty: false,
  hydrated: false,
  hydrate: () => {
    if (get().hydrated) return;
    const stored = readStorage();
    if (stored) {
      set({ ...stored, hydrated: true });
    } else {
      set({ hydrated: true });
      writeStorage(get());
    }
  },
  setTheme: (theme) => {
    set({ theme });
    writeStorage({ ...get(), theme });
  },
  setBackendUrl: (backend_url) => {
    set({ backend_url });
    writeStorage({ ...get(), backend_url });
  },
  setTemperature: (temperature) => {
    set({ temperature, dirty: true });
    writeStorage({ ...get(), temperature, dirty: true });
  },
  setTopK: (top_k) => {
    set({ top_k, dirty: true });
    writeStorage({ ...get(), top_k, dirty: true });
  },
  setScoreThreshold: (score_threshold) => {
    set({ score_threshold, dirty: true });
    writeStorage({ ...get(), score_threshold, dirty: true });
  },
  setPreferredModel: (preferred_model) => {
    set({ preferred_model, dirty: true });
    writeStorage({ ...get(), preferred_model, dirty: true });
  },
  save: () => {
    set({ dirty: false });
    writeStorage({ ...get(), dirty: false });
  },
  reset: () => {
    localStorage.removeItem(STORAGE_KEY);
    set({ ...defaults, dirty: false, hydrated: true });
  },
}));
