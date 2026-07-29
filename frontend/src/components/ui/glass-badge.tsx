"use client";

import { type HTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

interface GlassBadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "danger" | "accent";
  size?: "sm" | "md";
}

const GlassBadge = forwardRef<HTMLSpanElement, GlassBadgeProps>(
  ({ className, variant = "default", size = "sm", children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(
          "inline-flex items-center gap-1.5 rounded-lg border font-medium backdrop-blur-xl",
          size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-sm",
          variant === "default" &&
            "bg-glass border-glass-border text-muted-foreground",
          variant === "success" &&
            "bg-success/10 border-success/20 text-success",
          variant === "warning" &&
            "bg-warning/10 border-warning/20 text-warning",
          variant === "danger" &&
            "bg-danger/10 border-danger/20 text-danger",
          variant === "accent" &&
            "bg-accent/10 border-accent/20 text-accent",
          className,
        )}
        {...props}
      >
        {children}
      </span>
    );
  },
);
GlassBadge.displayName = "GlassBadge";

export { GlassBadge };
