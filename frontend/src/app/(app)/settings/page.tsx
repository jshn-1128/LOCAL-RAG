"use client";

import { useSettings } from "@/stores/settings";
import { GlassCard } from "@/components/ui/glass-card";
import { GlassButton } from "@/components/ui/glass-button";
import { GlassInput } from "@/components/ui/glass-input";
import { GlassSlider } from "@/components/ui/glass-slider";
import { GlassSwitch } from "@/components/ui/glass-switch";
import { GlassSelect } from "@/components/ui/glass-select";
import { useToast } from "@/components/ui/glass-toast";
import {
  Sun,
  Moon,
  Monitor,
  Globe,
  Thermometer,
  ListOrdered,
  Target,
  Cpu,
  RotateCcw,
} from "lucide-react";

export default function SettingsPage() {
  const settings = useSettings();
  const toast = useToast();

  const modelOptions = [
    { value: "llama3.2", label: "Llama 3.2" },
    { value: "llama3.1", label: "Llama 3.1" },
    { value: "gemma3", label: "Gemma 3" },
    { value: "mistral", label: "Mistral" },
    { value: "phi3", label: "Phi-3" },
  ];

  const handleReset = () => {
    settings.reset();
    toast.show({ title: "Settings reset to defaults", variant: "info" });
  };

  const handleSaveBackendUrl = () => {
    const url = settings.backend_url.trim();
    if (!url) {
      toast.show({ title: "Backend URL cannot be empty", variant: "error" });
      return;
    }
    try {
      new URL(url);
    } catch {
      toast.show({ title: "Invalid URL format", variant: "error" });
      return;
    }
    toast.show({ title: "Backend URL saved", variant: "success" });
  };

  return (
    <div className="p-6 space-y-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Configure your Local RAG experience
        </p>
      </div>

      {/* Appearance */}
      <GlassCard>
        <div className="flex items-center gap-3 mb-4">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-primary/10">
            {settings.theme === "dark" ? (
              <Moon className="h-5 w-5 text-primary" />
            ) : (
              <Sun className="h-5 w-5 text-primary" />
            )}
          </div>
          <h2 className="text-sm font-semibold">Appearance</h2>
        </div>
        <div className="flex items-center gap-3">
          <GlassButton
            variant={settings.theme === "dark" ? "primary" : "secondary"}
            size="sm"
            onClick={() => settings.setTheme("dark")}
            icon={<Moon className="h-4 w-4" />}
          >
            Dark
          </GlassButton>
          <GlassButton
            variant={settings.theme === "light" ? "primary" : "secondary"}
            size="sm"
            onClick={() => settings.setTheme("light")}
            icon={<Sun className="h-4 w-4" />}
          >
            Light
          </GlassButton>
        </div>
      </GlassCard>

      {/* Backend */}
      <GlassCard>
        <div className="flex items-center gap-3 mb-4">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-accent/10">
            <Globe className="h-5 w-5 text-accent" />
          </div>
          <h2 className="text-sm font-semibold">Backend Connection</h2>
        </div>
        <div className="flex gap-3">
          <GlassInput
            value={settings.backend_url}
            onChange={(e) => settings.setBackendUrl(e.target.value)}
            placeholder="http://localhost:8000"
            className="flex-1"
          />
          <GlassButton onClick={handleSaveBackendUrl} size="md">
            Save
          </GlassButton>
        </div>
      </GlassCard>

      {/* Model Configuration */}
      <GlassCard>
        <div className="flex items-center gap-3 mb-4">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-success/10">
            <Cpu className="h-5 w-5 text-success" />
          </div>
          <h2 className="text-sm font-semibold">Model Configuration</h2>
        </div>
        <div className="space-y-4">
          <GlassSelect
            value={settings.preferred_model}
            onValueChange={settings.setPreferredModel}
            options={modelOptions}
            label="Preferred Model"
          />
          <GlassSlider
            value={[settings.temperature]}
            onValueChange={([v]) => settings.setTemperature(v)}
            min={0}
            max={2}
            step={0.1}
            label="Temperature"
            formatValue={(v) => v.toFixed(1)}
          />
          <GlassSlider
            value={[settings.top_k]}
            onValueChange={([v]) => settings.setTopK(v)}
            min={1}
            max={20}
            step={1}
            label="Top-K Retrieval"
            formatValue={(v) => String(v)}
          />
          <GlassSlider
            value={[settings.score_threshold]}
            onValueChange={([v]) => settings.setScoreThreshold(v)}
            min={0}
            max={1}
            step={0.05}
            label="Score Threshold"
            formatValue={(v) => v.toFixed(2)}
          />
        </div>
      </GlassCard>

      {/* Reset */}
      <div className="flex justify-end">
        <GlassButton
          variant="ghost"
          size="sm"
          onClick={handleReset}
          icon={<RotateCcw className="h-4 w-4" />}
        >
          Reset to Defaults
        </GlassButton>
      </div>
    </div>
  );
}
