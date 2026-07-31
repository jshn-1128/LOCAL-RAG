"use client";

import { cn } from "@/lib/utils";

interface ConfidenceBadgeProps {
  level: string;
  reason?: string | null;
  conflicts?: string[] | null;
  className?: string;
}

const LEVEL_CONFIG: Record<string, { icon: string; label: string; color: string; bg: string }> = {
  HIGH: {
    icon: "●",
    label: "High confidence",
    color: "text-green-800 dark:text-green-400",
    bg: "bg-green-500/10 dark:bg-green-400/10 border-green-500/20 dark:border-green-400/20",
  },
  MEDIUM: {
    icon: "●",
    label: "Medium confidence",
    color: "text-yellow-800 dark:text-yellow-400",
    bg: "bg-yellow-500/10 dark:bg-yellow-400/10 border-yellow-500/20 dark:border-yellow-400/20",
  },
  LOW: {
    icon: "●",
    label: "Low confidence",
    color: "text-orange-800 dark:text-orange-400",
    bg: "bg-orange-500/10 dark:bg-orange-400/10 border-orange-500/20 dark:border-orange-400/20",
  },
  VERY_LOW: {
    icon: "●",
    label: "Very low confidence",
    color: "text-red-800 dark:text-red-400",
    bg: "bg-red-500/10 dark:bg-red-400/10 border-red-500/20 dark:border-red-400/20",
  },
};

export function ConfidenceBadge({ level, reason, conflicts, className }: ConfidenceBadgeProps) {
  const config = LEVEL_CONFIG[level] ?? LEVEL_CONFIG.VERY_LOW;

  return (
    <div className={cn("rounded-xl border px-3 py-2 space-y-1", config.bg, className)}>
      <div className="flex items-center gap-2">
        <span className={cn("text-xs", config.color)}>{config.icon}</span>
        <span className={cn("text-xs font-semibold", config.color)}>{config.label}</span>
      </div>
      {reason && (
        <p className="text-xs text-muted-foreground leading-relaxed">{reason}</p>
      )}
      {conflicts && conflicts.length > 0 && (
        <div className="pt-1 space-y-0.5">
          {conflicts.map((c, i) => (
            <p key={i} className="text-xs text-orange-800 dark:text-orange-400 leading-relaxed">
              ⚠ {c}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
