"use client";

import * as Switch from "@radix-ui/react-switch";
import { cn } from "@/lib/utils";

interface GlassSwitchProps {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  label?: string;
  className?: string;
}

export function GlassSwitch({
  checked,
  onCheckedChange,
  label,
  className,
}: GlassSwitchProps) {
  return (
    <label
      className={cn(
        "flex items-center gap-3 cursor-pointer",
        className,
      )}
    >
      <Switch.Root
        checked={checked}
        onCheckedChange={onCheckedChange}
        className={cn(
          "peer inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full border border-glass-border",
          "transition-colors duration-200",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
          checked ? "bg-primary" : "bg-glass",
        )}
      >
        <Switch.Thumb
          className={cn(
            "pointer-events-none block h-3.5 w-3.5 rounded-full bg-foreground shadow-sm",
            "transition-transform duration-200",
            checked ? "translate-x-[18px]" : "translate-x-[3px]",
          )}
        />
      </Switch.Root>
      {label && (
        <span className="text-sm text-muted-foreground">{label}</span>
      )}
    </label>
  );
}
