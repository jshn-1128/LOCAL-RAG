"use client";

import * as TooltipPrimitive from "@radix-ui/react-tooltip";
import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

export const TooltipProvider = TooltipPrimitive.Provider;

interface GlassTooltipProps {
  content: string;
  children: ReactNode;
  side?: "top" | "bottom" | "left" | "right";
  className?: string;
}

export function GlassTooltip({
  content,
  children,
  side = "top",
  className,
}: GlassTooltipProps) {
  return (
    <TooltipPrimitive.Root>
      <TooltipPrimitive.Trigger asChild>{children}</TooltipPrimitive.Trigger>
      <TooltipPrimitive.Portal>
        <TooltipPrimitive.Content
          side={side}
          sideOffset={4}
          className={cn(
            "z-50 max-w-xs rounded-xl border border-glass-border bg-glass/95 backdrop-blur-xl px-3 py-2",
            "text-xs text-foreground shadow-lg shadow-black/5",
            "animate-in fade-in-0 zoom-in-95",
            className,
          )}
        >
          {content}
          <TooltipPrimitive.Arrow className="fill-glass-border" />
        </TooltipPrimitive.Content>
      </TooltipPrimitive.Portal>
    </TooltipPrimitive.Root>
  );
}
