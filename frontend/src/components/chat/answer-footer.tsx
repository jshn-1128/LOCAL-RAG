"use client";

import { useState } from "react";
import { FileText, Search, ChevronDown, ChevronRight } from "lucide-react";
import { ConfidenceBadge } from "./confidence-badge";
import { SupportingSource } from "./supporting-source";
import type { ConfidenceDTO, AttributedSourceDTO } from "@/types";

interface AnswerFooterProps {
  confidence: ConfidenceDTO | null | undefined;
  attributedSources: AttributedSourceDTO[] | null | undefined;
  onOpenInspector?: () => void;
}

export function AnswerFooter({
  confidence,
  attributedSources,
  onOpenInspector,
}: AnswerFooterProps) {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const sourcesRegionId = "supporting-sources";
  const hasSources = attributedSources && attributedSources.length > 0;
  const hasConfidence = confidence && confidence.level !== "VERY_LOW";

  return (
    <div className="mt-4 space-y-2">
      {hasConfidence && (
        <ConfidenceBadge
          level={confidence.level}
          reason={confidence.reason}
          conflicts={confidence.conflicts}
        />
      )}

      {hasSources && (
        <div className="rounded-xl border border-glass-border overflow-hidden">
          <button
            onClick={() => setSourcesOpen(!sourcesOpen)}
            aria-expanded={sourcesOpen}
            aria-controls={sourcesRegionId}
            aria-label={`${sourcesOpen ? "Hide" : "Show"} supporting sources (${attributedSources.length})`}
            className="flex items-center gap-2 w-full text-left px-3 py-2.5 hover:bg-muted/50 transition-colors text-sm font-medium text-muted-foreground"
          >
            {sourcesOpen ? (
              <ChevronDown className="h-4 w-4" aria-hidden="true" />
            ) : (
              <ChevronRight className="h-4 w-4" aria-hidden="true" />
            )}
            <FileText className="h-4 w-4" aria-hidden="true" />
            <span>Supporting Sources ({attributedSources.length})</span>
          </button>
          {sourcesOpen && (
            <div id={sourcesRegionId} className="px-3 pb-3 space-y-2">
              {attributedSources.map((src) => (
                <SupportingSource key={src.chunk_id} source={src} />
              ))}
            </div>
          )}
        </div>
      )}

      {onOpenInspector && (
        <button
          onClick={onOpenInspector}
          className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors px-1"
        >
          <Search className="h-3.5 w-3.5" aria-hidden="true" />
          Search Inspector
        </button>
      )}
    </div>
  );
}
