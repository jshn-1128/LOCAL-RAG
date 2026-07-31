"use client";

import { useQuery } from "@tanstack/react-query";
import {
  getSystemStatus,
  getDocuments,
  getVectorCount,
} from "@/services/api";
import { GlassCard } from "@/components/ui/glass-card";
import { GlassBadge } from "@/components/ui/glass-badge";
import { GlassButton } from "@/components/ui/glass-button";
import {
  Brain,
  FileText,
  Layers,
  MessageSquare,
  Activity,
  Cpu,
  Database,
  HardDrive,
  ArrowRight,
  BookOpen,
  Search,
} from "lucide-react";
import Link from "next/link";
import { formatDate } from "@/lib/utils";

export default function DashboardPage() {
  const { data: status, isLoading } = useQuery({
    queryKey: ["system-status"],
    queryFn: getSystemStatus,
    refetchInterval: 15_000,
  });

  const { data: documents } = useQuery({
    queryKey: ["documents"],
    queryFn: getDocuments,
  });

  const { data: vectorCount } = useQuery({
    queryKey: ["vector-count"],
    queryFn: getVectorCount,
  });

  const stats = [
    {
      label: "Documents",
      value: documents?.length ?? status?.document_count ?? 0,
      icon: FileText,
      href: "/documents",
      color: "text-primary",
      bg: "bg-primary/10",
    },
    {
      label: "Vector Index",
      value: vectorCount ?? status?.vector_count ?? 0,
      icon: Layers,
      href: "/documents",
      color: "text-accent",
      bg: "bg-accent/10",
    },
    {
      label: "Model",
      value: status?.llm_model ?? "—",
      icon: Cpu,
      href: "/system",
      color: "text-success",
      bg: "bg-success/10",
    },
    {
      label: "Status",
      value: status?.health?.status ?? "checking",
      icon: Activity,
      href: "/system",
      color:
        status?.health?.status === "ok" || status?.health?.status === "healthy"
          ? "text-success"
          : "text-warning",
      bg:
        status?.health?.status === "ok" || status?.health?.status === "healthy"
          ? "bg-success/10"
          : "bg-warning/10",
    },
  ];

  const recentDocs = documents?.slice(0, 5) ?? [];

  return (
    <div className="p-6 space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Your local knowledge base overview
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Link key={stat.label} href={stat.href}>
              <GlassCard className="p-5 glass-hover cursor-pointer">
                <div className="flex items-center gap-3">
                  <div
                    className={`flex items-center justify-center w-10 h-10 rounded-xl ${stat.bg}`}
                  >
                    <Icon className={`h-5 w-5 ${stat.color}`} />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs text-muted-foreground">
                      {stat.label}
                    </p>
                    <p className="text-xl font-semibold truncate">
                      {isLoading ? "..." : String(stat.value)}
                    </p>
                  </div>
                </div>
              </GlassCard>
            </Link>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link href="/chat">
            <GlassCard className="p-5 glass-hover cursor-pointer group">
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-primary/10">
                  <MessageSquare className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium">Start Chat</p>
                  <p className="text-xs text-muted-foreground">
                    Ask questions about your documents
                  </p>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
              </div>
            </GlassCard>
          </Link>
          <Link href="/documents">
            <GlassCard className="p-5 glass-hover cursor-pointer group">
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-accent/10">
                  <BookOpen className="h-5 w-5 text-accent" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium">Manage Documents</p>
                  <p className="text-xs text-muted-foreground">
                    Upload and index new files
                  </p>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-accent transition-colors" />
              </div>
            </GlassCard>
          </Link>
          <Link href="/search">
            <GlassCard className="p-5 glass-hover cursor-pointer group">
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-success/10">
                  <Search className="h-5 w-5 text-success" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium">Search Inspector</p>
                  <p className="text-xs text-muted-foreground">
                    Inspect the RAG pipeline
                  </p>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-success transition-colors" />
              </div>
            </GlassCard>
          </Link>
        </div>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <GlassCard>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Database className="h-5 w-5 text-primary" />
            System Status
          </h2>
          <div className="space-y-3">
            <StatusRow
              label="Backend"
              value={status?.health?.status ?? "checking"}
              ok={status?.health?.status === "ok" || status?.health?.status === "healthy"}
            />
            <StatusRow
              label="Ollama"
              value={status?.ollama?.available ? "Connected" : "Disconnected"}
              ok={!!status?.ollama?.available}
            />
            <StatusRow
              label="Vector Store"
              value={status?.vector_store_type ?? "—"}
              ok
            />
            <StatusRow
              label="Environment"
              value={status?.environment ?? "—"}
              ok
            />
          </div>
        </GlassCard>

        <GlassCard>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <HardDrive className="h-5 w-5 text-accent" />
            Recent Documents
          </h2>
          {recentDocs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No documents indexed yet</p>
              <Link href="/documents">
                <GlassButton variant="secondary" size="sm" className="mt-3">
                  Upload Documents
                </GlassButton>
              </Link>
            </div>
          ) : (
            <div className="space-y-2">
              {recentDocs.map((doc) => (
                <Link
                  key={doc.id}
                  href="/documents"
                  className="flex items-center gap-3 p-2 rounded-xl hover:bg-muted/50 transition-colors group cursor-pointer"
                >
                  <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                    <FileText className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate group-hover:text-primary transition-colors">
                      {doc.filename}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {doc.loaded_at ? formatDate(doc.loaded_at) : "—"}
                    </p>
                  </div>
                  <GlassBadge variant="default" size="sm">
                    {doc.file_type}
                  </GlassBadge>
                </Link>
              ))}
            </div>
          )}
        </GlassCard>
      </div>
    </div>
  );
}

function StatusRow({
  label,
  value,
  ok,
}: {
  label: string;
  value: string;
  ok: boolean;
}) {
  return (
    <div className="flex items-center justify-between py-1">
      <span className="text-sm text-muted-foreground">{label}</span>
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">{value}</span>
        <span
          className={`inline-block w-2 h-2 rounded-full ${
            ok ? "bg-success" : "bg-danger"
          }`}
        />
      </div>
    </div>
  );
}
