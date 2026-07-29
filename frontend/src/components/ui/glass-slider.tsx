"use client";

import * as Slider from "@radix-ui/react-slider";
import { cn } from "@/lib/utils";

interface GlassSliderProps {
  value: number[];
  onValueChange: (value: number[]) => void;
  min?: number;
  max?: number;
  step?: number;
  label?: string;
  formatValue?: (value: number) => string;
  className?: string;
}

export function GlassSlider({
  value,
  onValueChange,
  min = 0,
  max = 1,
  step = 0.01,
  label,
  formatValue,
  className,
}: GlassSliderProps) {
  return (
    <div className={cn("space-y-2", className)}>
      {label && (
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-muted-foreground">
            {label}
          </label>
          <span className="text-sm text-foreground">
            {formatValue ? formatValue(value[0]) : value[0]}
          </span>
        </div>
      )}
      <Slider.Root
        className="relative flex h-5 w-full touch-none items-center"
        value={value}
        onValueChange={onValueChange}
        min={min}
        max={max}
        step={step}
      >
        <Slider.Track className="relative h-1.5 w-full grow rounded-full bg-glass border border-glass-border">
          <Slider.Range className="absolute h-full rounded-full bg-primary" />
        </Slider.Track>
        <Slider.Thumb
          className={cn(
            "block h-4 w-4 rounded-full border border-glass-border bg-card shadow-sm",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
            "hover:bg-muted transition-colors",
          )}
        />
      </Slider.Root>
    </div>
  );
}
