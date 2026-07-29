"use client";

import * as Progress from "@radix-ui/react-progress";
import { cn } from "@/lib/utils";

interface GlassProgressProps {
  value: number;
  max?: number;
  className?: string;
  variant?: "default" | "success" | "warning" | "danger";
}

export function GlassProgress({
  value,
  max = 100,
  className,
  variant = "default",
}: GlassProgressProps) {
  const pct = max <= 0 ? 0 : Math.min(Math.max((value / max) * 100, 0), 100);

  return (
    <Progress.Root
      className={cn(
        "relative h-2 w-full overflow-hidden rounded-full bg-glass border border-glass-border",
        className,
      )}
      value={value}
      max={max}
    >
      <Progress.Indicator
        className={cn(
          "h-full w-full flex-1 rounded-full transition-all duration-500 ease-out",
          variant === "default" && "bg-primary",
          variant === "success" && "bg-success",
          variant === "warning" && "bg-warning",
          variant === "danger" && "bg-danger",
        )}
        style={{ transform: `translateX(-${100 - pct}%)` }}
      />
    </Progress.Root>
  );
}
