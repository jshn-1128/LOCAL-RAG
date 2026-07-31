"use client";

import { ArrowDown, FileText, Search, Edit3, GitFork, Layers, MessageSquare } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { cn } from "@/lib/utils";
import type { PipelineInfoDTO, AttributedSourceDTO, ConfidenceDTO } from "@/types";

interface PipelineStageProps {
  icon: React.ReactNode;
  label: string;
  description: string;
  children?: React.ReactNode;
}

function PipelineStage({ icon, label, description, children }: PipelineStageProps) {
  return (
    <div className="flex gap-3">
      <div className="flex flex-col items-center">
        <div className="flex items-center justify-center w-7 h-7 rounded-full bg-primary/10 text-primary">
          {icon}
        </div>
        <div className="w-px flex-1 bg-border mt-1" />
      </div>
      <div className="flex-1 pb-4 min-w-0">
        <div className="space-y-0.5">
          <p className="text-sm font-medium">{label}</p>
          <p className="text-xs text-muted-foreground">{description}</p>
        </div>
        {children && <div className="mt-2">{children}</div>}
      </div>
    </div>
  );
}

interface SearchInspectorProps {
  pipeline: PipelineInfoDTO | null | undefined;
  attributedSources: AttributedSourceDTO[] | null | undefined;
  confidence: ConfidenceDTO | null | undefined;
}

export function SearchInspector({
  pipeline,
  attributedSources,
  confidence,
}: SearchInspectorProps) {
  if (!pipeline) return null;

  return (
    <div className="space-y-1">
      <PipelineStage
        icon={<Search className="h-3.5 w-3.5" />}
        label="Original Query"
        description={pipeline.original_query}
      >
        <div className="p-2 rounded-lg bg-muted/40 border border-glass-border">
          <p className="text-xs text-muted-foreground">{pipeline.original_query}</p>
        </div>
      </PipelineStage>

      {pipeline.rewritten_query && (
        <PipelineStage
          icon={<Edit3 className="h-3.5 w-3.5" />}
          label="Query Rewrite"
          description="Enhanced for better retrieval"
        >
          <div className="p-2 rounded-lg bg-muted/40 border border-glass-border">
            <p className="text-xs text-muted-foreground">{pipeline.rewritten_query}</p>
          </div>
        </PipelineStage>
      )}

      <PipelineStage
        icon={<Layers className="h-3.5 w-3.5" />}
        label="Retrieval"
        description={`Found ${pipeline.num_results} chunk${pipeline.num_results !== 1 ? "s" : ""} (top_k=${pipeline.top_k})`}
      >
        {attributedSources && attributedSources.length > 0 && (
          <div className="space-y-1">
            {attributedSources.map((src) => (
              <div
                key={src.chunk_id}
                className={cn(
                  "p-2 rounded-lg border text-xs",
                  src.role === "PRIMARY"
                    ? "bg-blue-500/5 border-blue-500/20"
                    : src.role === "SUPPORTING"
                      ? "bg-purple-500/5 border-purple-500/20"
                      : "bg-muted/30 border-glass-border",
                )}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium truncate">
                    {src.document_filename || "Unknown"}
                  </span>
                  <span className="text-muted-foreground shrink-0 ml-2">
                    {src.similarity_label}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </PipelineStage>

      <PipelineStage
        icon={<GitFork className="h-3.5 w-3.5" />}
        label="Evidence Selected"
        description={
          attributedSources
            ? `${attributedSources.filter((s) => s.role === "PRIMARY").length} primary, ${attributedSources.filter((s) => s.role === "SUPPORTING").length} supporting`
            : "None"
        }
      />

      <PipelineStage
        icon={<MessageSquare className="h-3.5 w-3.5" />}
        label="Response Generated"
        description={
          confidence
            ? `Confidence: ${confidence.level} (${(confidence.score * 100).toFixed(0)}%)`
            : "Completed"
        }
      />
    </div>
  );
}
