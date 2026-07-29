"use client";

import { useEffect, type ReactNode } from "react";
import { useSettings } from "@/stores/settings";

export function ThemeProvider({ children }: { children: ReactNode }) {
  const theme = useSettings((s) => s.theme);

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("light", "dark");
    root.classList.add(theme);
  }, [theme]);

  return <>{children}</>;
}
