"use client";

import { type ReactNode } from "react";
import { Sidebar } from "./sidebar";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Background blobs */}
      <div className="gradient-blob gradient-blob-1" aria-hidden="true" />
      <div className="gradient-blob gradient-blob-2" aria-hidden="true" />
      <div className="gradient-blob gradient-blob-3" aria-hidden="true" />

      <Sidebar />

      <main className="flex-1 overflow-y-auto scrollbar-thin relative z-10">
        <div className="min-h-screen">{children}</div>
      </main>
    </div>
  );
}
