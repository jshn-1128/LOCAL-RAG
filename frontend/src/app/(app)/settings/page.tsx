"use client";

import { useQuery } from "@tanstack/react-query";
import { useSettings } from "@/stores/settings";
import { GlassCard } from "@/components/ui/glass-card";
import { GlassButton } from "@/components/ui/glass-button";
import { GlassInput } from "@/components/ui/glass-input";
import { GlassSlider } from "@/components/ui/glass-slider";
import { GlassSelect } from "@/components/ui/glass-select";
import { GlassTooltip } from "@/components/ui/glass-tooltip";
import { useToast } from "@/components/ui/glass-toast";
import { getOllamaModels } from "@/services/api";
import {
  Sun,
  Moon,
  Globe,
  Cpu,
  RotateCcw,
  Save,
  ChevronDown,
  ChevronRight,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import { useState } from "react";

const TOOLTIPS = {
  temperature:
    "Controls randomness in responses. Lower values (0.1) make output more focused and deterministic; higher values (1.5+) make it more creative and varied.",
  top_k:
    "Limits how many document chunks are retrieved per query. Higher values provide more context but may include noise; lower values are more precise.",
};

export default function SettingsPage() {
  const settings = useSettings();
  const toast = useToast();
  const [advancedOpen, setAdvancedOpen] = useState(false);

  const { data: modelsData, isLoading: modelsLoading, error: modelsError } = useQuery({
    queryKey: ["ollama-models"],
    queryFn: getOllamaModels,
    refetchOnWindowFocus: false,
    staleTime: 60_000,
  });

  const modelOptions = (modelsData?.models ?? []).map((m) => ({
    value: m,
    label: m,
  }));

  const activeModel = modelsData?.current ?? settings.preferred_model;

  const handleSave = () => {
    settings.save();
    toast.show({ title: "Settings saved", variant: "success" });
  };

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
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            Configure your Local RAG experience
          </p>
        </div>
        {settings.dirty && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-warning/10 border border-warning/20">
            <span className="w-2 h-2 rounded-full bg-warning animate-pulse-soft" />
            <span className="text-xs font-medium text-warning">Unsaved changes</span>
          </div>
        )}
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
          {modelsLoading ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground py-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading installed models...
            </div>
          ) : modelsError || modelsData?.error ? (
            <div className="flex items-start gap-2 text-sm text-danger py-2">
              <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
              <div>
                <p className="font-medium">Could not fetch models</p>
                <p className="text-muted-foreground text-xs mt-1">
                  {modelsData?.error ?? "Ollama might not be running."}
                </p>
              </div>
            </div>
          ) : modelOptions.length === 0 ? (
            <div className="text-sm text-muted-foreground py-2 space-y-1">
              <p>No installed models found.</p>
              <p className="text-xs">
                Run <code className="px-1 py-0.5 rounded bg-muted">ollama pull gemma3:1b</code> to get started.
              </p>
            </div>
          ) : (
            <>
              <GlassSelect
                value={activeModel}
                onValueChange={settings.setPreferredModel}
                options={modelOptions}
                label="Active Model"
                disabled
              />
              <p className="text-xs text-muted-foreground -mt-2">
                Model switching is not yet implemented. The current model is set on the backend.
              </p>
            </>
          )}

          {/* Advanced toggle */}
          <button
            onClick={() => setAdvancedOpen(!advancedOpen)}
            className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors pt-2"
          >
            {advancedOpen ? (
              <ChevronDown className="h-3.5 w-3.5" />
            ) : (
              <ChevronRight className="h-3.5 w-3.5" />
            )}
            Advanced settings
          </button>

          {advancedOpen && (
            <div className="space-y-4 pl-2 border-l-2 border-glass-border">
              <GlassTooltip content={TOOLTIPS.temperature}>
                <GlassSlider
                  value={[settings.temperature]}
                  onValueChange={([v]) => settings.setTemperature(v)}
                  min={0}
                  max={2}
                  step={0.1}
                  label="Temperature"
                  formatValue={(v) => v.toFixed(1)}
                />
              </GlassTooltip>
              <GlassTooltip content={TOOLTIPS.top_k}>
                <GlassSlider
                  value={[settings.top_k]}
                  onValueChange={([v]) => settings.setTopK(v)}
                  min={1}
                  max={20}
                  step={1}
                  label="Top-K Retrieval"
                  formatValue={(v) => String(v)}
                />
              </GlassTooltip>
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <label className="text-sm font-medium text-muted-foreground">
                      Score Threshold
                    </label>
                    <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-full bg-muted text-muted-foreground">
                      Coming Soon
                    </span>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {settings.score_threshold.toFixed(2)}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground">
                  Not yet wired to the backend. No effect on retrieval or chat.
                </p>
              </div>
            </div>
          )}
        </div>
      </GlassCard>

      {/* Actions */}
      <div className="flex items-center justify-between">
        <GlassButton
          variant="ghost"
          size="sm"
          onClick={handleReset}
          icon={<RotateCcw className="h-4 w-4" />}
        >
          Reset to Defaults
        </GlassButton>
        <div className="flex items-center gap-3">
          {settings.dirty && (
            <span className="text-xs text-muted-foreground">
              Unsaved changes
            </span>
          )}
          <GlassButton
            variant={settings.dirty ? "primary" : "secondary"}
            size="md"
            onClick={handleSave}
            icon={<Save className="h-4 w-4" />}
            disabled={!settings.dirty}
          >
            Save Settings
          </GlassButton>
        </div>
      </div>
    </div>
  );
}
