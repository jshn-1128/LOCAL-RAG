"use client";

import { GlassCard } from "@/components/ui/glass-card";
import { GlassButton } from "@/components/ui/glass-button";
import { AlertTriangle } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex items-center justify-center min-h-screen bg-background p-6">
      <GlassCard className="max-w-md w-full text-center space-y-4">
        <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-danger/10 mx-auto">
          <AlertTriangle className="h-7 w-7 text-danger" />
        </div>
        <h2 className="text-xl font-semibold">Something went wrong</h2>
        <p className="text-sm text-muted-foreground">
          {error.message || "An unexpected error occurred"}
        </p>
        <GlassButton onClick={reset} variant="primary">
          Try again
        </GlassButton>
      </GlassCard>
    </div>
  );
}
