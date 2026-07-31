"use client";

import * as Select from "@radix-ui/react-select";
import { ChevronDown, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { forwardRef } from "react";

interface GlassSelectProps {
  value: string;
  onValueChange: (value: string) => void;
  options: { value: string; label: string }[];
  placeholder?: string;
  label?: string;
  className?: string;
  disabled?: boolean;
}

export function GlassSelect({
  value,
  onValueChange,
  options,
  placeholder = "Select...",
  label,
  className,
  disabled,
}: GlassSelectProps) {
  return (
    <div className="space-y-1.5">
      {label && (
        <label className="text-sm font-medium text-muted-foreground">
          {label}
        </label>
      )}
      <Select.Root disabled={disabled} value={value} onValueChange={onValueChange}>
        <Select.Trigger
          className={cn(
            "flex h-10 w-full items-center justify-between rounded-xl border bg-glass backdrop-blur-xl px-3 py-2 text-sm",
            "border-glass-border text-foreground",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
            "transition-all duration-200",
            className,
          )}
        >
          <Select.Value placeholder={placeholder} />
          <Select.Icon>
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          </Select.Icon>
        </Select.Trigger>
        <Select.Portal>
          <Select.Content
            className={cn(
              "z-50 min-w-[8rem] overflow-hidden rounded-xl border bg-card border-border shadow-xl",
              "animate-in fade-in-80 slide-in-from-top-1",
            )}
          >
            <Select.Viewport className="p-1">
              {options.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </Select.Viewport>
          </Select.Content>
        </Select.Portal>
      </Select.Root>
    </div>
  );
}

const SelectItem = forwardRef<
  React.ElementRef<typeof Select.Item>,
  React.ComponentPropsWithoutRef<typeof Select.Item>
>(({ className, children, ...props }, ref) => {
  return (
    <Select.Item
      ref={ref}
      className={cn(
        "relative flex cursor-default select-none items-center rounded-lg px-3 py-2 text-sm outline-none",
        "focus:bg-muted data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
        "transition-colors duration-150",
        className,
      )}
      {...props}
    >
      <Select.ItemText>{children}</Select.ItemText>
      <Select.ItemIndicator className="absolute right-2">
        <Check className="h-4 w-4" />
      </Select.ItemIndicator>
    </Select.Item>
  );
});
SelectItem.displayName = "SelectItem";
