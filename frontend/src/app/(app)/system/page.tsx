"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Server,
  Cpu,
  Brain,
  Database,
  Activity,
  Layers,
  MemoryStick,
  Package,
  Zap,
} from "lucide-react";
import { getSystemStatus } from "@/services/api";
import { GlassCard } from "@/components/ui/glass-card";
import { GlassBadge } from "@/components/ui/glass-badge";

const sections = [
  {
    title: "Backend",
    icon: Server,
    color: "text-primary",
    bg: "bg-primary/10",
    fields: ["status", "version", "uptime", "timestamp"] as const,
    prefix: "health" as const,
  },
  {
    title: "Ollama",
    icon: Cpu,
    color: "text-accent",
    bg: "bg-accent/10",
    fields: ["available", "model", "host"] as const,
    prefix: "ollama",
  },
  {
    title: "Embedding Model",
    icon: Brain,
    color: "text-success",
    bg: "bg-success/10",
    fields: ["embedding_model"] as const,
  },
  {
    title: "LLM",
    icon: Zap,
    color: "text-warning",
    bg: "bg-warning/10",
    fields: ["llm_model"] as const,
  },
  {
    title: "Memory",
    icon: MemoryStick,
    color: "text-accent",
    bg: "bg-accent/10",
    fields: ["memory_type"] as const,
  },
  {
    title: "Vector Store",
    icon: Layers,
    color: "text-primary",
    bg: "bg-primary/10",
    fields: ["vector_store_type", "vector_count"] as const,
  },
  {
    title: "Documents",
    icon: Database,
    color: "text-success",
    bg: "bg-success/10",
    fields: ["document_count"] as const,
  },
  {
    title: "Application",
    icon: Package,
    color: "text-muted-foreground",
    bg: "bg-muted",
    fields: ["environment"] as const,
  },
];

function formatUptime(seconds: number): string {
  if (!seconds) return "—";
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const parts: string[] = [];
  if (d > 0) parts.push(`${d}d`);
  if (h > 0) parts.push(`${h}h`);
  if (m > 0) parts.push(`${m}m`);
  return parts.join(" ") || "<1m";
}

export default function SystemPage() {
  const { data: status, isLoading } = useQuery({
    queryKey: ["system-status"],
    queryFn: getSystemStatus,
    refetchInterval: 10_000,
  });

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight">System</h1>
        <p className="text-muted-foreground">
          System status and configuration
        </p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <div
              key={i}
              className="h-32 rounded-2xl bg-glass animate-pulse border border-glass-border"
            />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sections.map((section) => {
            const Icon = section.icon;
            return (
              <GlassCard key={section.title}>
                <div className="flex items-center gap-3 mb-4">
                  <div
                    className={`flex items-center justify-center w-10 h-10 rounded-xl ${section.bg}`}
                  >
                    <Icon className={`h-5 w-5 ${section.color}`} />
                  </div>
                  <h2 className="text-sm font-semibold">{section.title}</h2>
                </div>
                <div className="space-y-2">
                  {section.fields.map((field) => {
                    const key = section.prefix
                      ? `${section.prefix}.${field}`
                      : field;

                    const raw = status as unknown as Record<string, unknown>;
                    const nested = section.prefix
                      ? (raw[section.prefix] as Record<string, unknown> | undefined)
                      : undefined;
                    const value = section.prefix
                      ? nested?.[field]
                      : raw[field];

                    const isUnavailable = value == null || value === "" || value === "?";

                    let displayValue: string;
                    if (isUnavailable) {
                      const messages: Record<string, string> = {
                        embedding_model: "Not reported by backend",
                        memory_type: "Not reported by backend",
                        vector_store_type: "Not reported by backend",
                        llm_model: "Not configured",
                        environment: "Unknown",
                        version: "Unknown",
                        status: "Unknown",
                        host: "Unknown",
                      };
                      displayValue = messages[field] ?? "Not available";
                    } else if (field === "uptime" && typeof value === "number") {
                      displayValue = formatUptime(value);
                    } else if (field === "available") {
                      displayValue = value ? "Connected" : "Disconnected";
                    } else {
                      displayValue = String(value);
                    }

                    const isOk =
                      field === "available"
                        ? !!value
                        : field === "status"
                          ? String(value).toLowerCase() === "ok" ||
                            String(value).toLowerCase() === "healthy"
                          : null;

                    return (
                      <div
                        key={key}
                        className="flex items-center justify-between"
                      >
                        <span className="text-xs text-muted-foreground capitalize">
                          {field.replace(/_/g, " ")}
                        </span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-medium">
                            {displayValue}
                          </span>
                          {isOk !== null && (
                            <span
                              className={`inline-block w-1.5 h-1.5 rounded-full ${
                                isOk ? "bg-success" : "bg-danger"
                              }`}
                            />
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </GlassCard>
            );
          })}
        </div>
      )}

      {/* Overall Status */}
      <GlassCard className="md:col-span-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className={`flex items-center justify-center w-10 h-10 rounded-xl ${
                status?.health?.status === "ok" ||
                status?.health?.status === "healthy"
                  ? "bg-success/10"
                  : "bg-danger/10"
              }`}
            >
              <Activity
                className={`h-5 w-5 ${
                  status?.health?.status === "ok" ||
                  status?.health?.status === "healthy"
                    ? "text-success"
                    : "text-danger"
                }`}
              />
            </div>
            <div>
              <p className="text-sm font-medium">
                System{" "}
                {status?.health?.status === "ok" ||
                status?.health?.status === "healthy"
                  ? "Healthy"
                  : "Unhealthy"}
              </p>
              <p className="text-xs text-muted-foreground">
                {status?.environment === "production"
                  ? "Production"
                  : "Development"}{" "}
                · v{status?.health?.version || "?"}
              </p>
            </div>
          </div>
          <GlassBadge
            variant={
              status?.health?.status === "ok" ||
              status?.health?.status === "healthy"
                ? "success"
                : "danger"
            }
          >
            {status?.health?.status || "Unknown"}
          </GlassBadge>
        </div>
      </GlassCard>
    </div>
  );
}
