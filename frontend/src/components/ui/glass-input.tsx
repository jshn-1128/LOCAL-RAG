"use client";

import { type InputHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

interface GlassInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const GlassInput = forwardRef<HTMLInputElement, GlassInputProps>(
  ({ className, label, error, id, ...props }, ref) => {
    const errorId = id ? `${id}-error` : undefined;
    return (
      <div className="space-y-1.5">
        {label && (
          <label
            htmlFor={id}
            className="text-sm font-medium text-muted-foreground"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={id}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? errorId : undefined}
          className={cn(
            "flex h-10 w-full rounded-xl border bg-glass backdrop-blur-xl px-3 py-2 text-sm",
            "border-glass-border placeholder:text-muted-foreground/50",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
            "disabled:cursor-not-allowed disabled:opacity-50",
            "transition-all duration-200",
            error && "border-danger focus-visible:ring-danger",
            className,
          )}
          {...props}
        />
        {error && <p id={errorId} className="text-xs text-danger" role="alert">{error}</p>}
      </div>
    );
  },
);
GlassInput.displayName = "GlassInput";

export { GlassInput };
