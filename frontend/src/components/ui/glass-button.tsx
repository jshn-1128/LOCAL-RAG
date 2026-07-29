"use client";

import { forwardRef } from "react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

interface GlassButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  icon?: React.ReactNode;
  tooltip?: string;
}

const GlassButton = forwardRef<HTMLButtonElement, GlassButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "md",
      loading,
      icon,
      children,
      disabled,
      type = "button",
      tooltip,
      ...props
    },
    ref,
  ) => {
    return (
      <motion.button
        ref={ref}
        type={type}
        disabled={disabled || loading}
        aria-busy={loading || undefined}
        aria-label={props["aria-label"] ?? (icon && !children ? tooltip : undefined)}
        whileHover={{ scale: disabled ? 1 : 1.01 }}
        whileTap={{ scale: disabled ? 1 : 0.98 }}
        className={cn(
          "relative inline-flex items-center justify-center gap-2 rounded-xl font-medium transition-all duration-200",
          "border backdrop-blur-xl",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
          size === "sm" && "px-3 py-1.5 text-xs",
          size === "md" && "px-4 py-2 text-sm",
          size === "lg" && "px-6 py-3 text-base",
          variant === "primary" &&
            "bg-primary text-primary-foreground border-primary/20 hover:bg-primary/90 shadow-sm shadow-primary/10",
          variant === "secondary" &&
            "glass glass-hover text-foreground border-glass-border",
          variant === "ghost" &&
            "bg-transparent border-transparent text-muted-foreground hover:text-foreground hover:bg-muted/50",
          variant === "danger" &&
            "bg-danger/10 text-danger border-danger/20 hover:bg-danger/20",
          className,
        )}
      >
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : icon ? (
          icon
        ) : null}
        {children}
      </motion.button>
    );
  },
);
GlassButton.displayName = "GlassButton";

export { GlassButton };
