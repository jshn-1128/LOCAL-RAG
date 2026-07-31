"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronRight, FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import type { AttributedSourceDTO } from "@/types";

const ROLE_LABELS: Record<string, string> = {
  PRIMARY: "Primary Source",
  SUPPORTING: "Supporting Source",
  BACKGROUND: "Background",
};

const ROLE_COLORS: Record<string, string> = {
  PRIMARY:
    "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20",
  SUPPORTING:
    "bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20",
  BACKGROUND:
    "bg-muted text-muted-foreground border-glass-border",
};

const SIMILARITY_COLORS: Record<string, string> = {
  High: "text-green-800 dark:text-green-400",
  Medium: "text-yellow-800 dark:text-yellow-400",
  Low: "text-orange-800 dark:text-orange-400",
  "Very Low": "text-red-800 dark:text-red-400",
};

interface SupportingSourceProps {
  source: AttributedSourceDTO;
  defaultExpanded?: boolean;
}

export function SupportingSource({ source, defaultExpanded = false }: SupportingSourceProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const regionId = `evidence-${source.chunk_id}`;

  return (
    <div className="rounded-xl border border-glass-border bg-card/50 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
        aria-controls={regionId}
        aria-label={`${ROLE_LABELS[source.role] ?? source.role}: ${source.document_filename || "document"}${source.page != null ? `, page ${source.page}` : ""}${expanded ? ". Collapse evidence" : ". Show evidence"}`}
        className="flex items-start gap-2 w-full text-left p-3 hover:bg-muted/30 transition-colors"
      >
        {expanded ? (
          <ChevronDown className="h-3.5 w-3.5 mt-0.5 shrink-0 text-muted-foreground" aria-hidden="true" />
        ) : (
          <ChevronRight className="h-3.5 w-3.5 mt-0.5 shrink-0 text-muted-foreground" aria-hidden="true" />
        )}
        <div className="flex-1 min-w-0 space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <FileText className="h-3.5 w-3.5 text-muted-foreground shrink-0" aria-hidden="true" />
            <span className="text-sm font-medium truncate">
              {source.document_filename || `Document ${source.document_id.slice(0, 8)}`}
            </span>
            <span className={cn(
              "text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-full border font-medium",
              ROLE_COLORS[source.role] ?? ROLE_COLORS.BACKGROUND,
            )}>
              {ROLE_LABELS[source.role] ?? source.role}
            </span>
          </div>
          <div className="flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
            <span className={SIMILARITY_COLORS[source.similarity_label] ?? ""}>
              Similarity: {source.similarity_label}
            </span>
            {source.document_type && (
              <span className="uppercase tracking-wider">{source.document_type}</span>
            )}
            {source.page != null && <span>Page {source.page}</span>}
            {source.section && <span className="truncate max-w-[16rem]">{source.section}</span>}
            <span>Chunk #{source.chunk_index + 1}</span>
          </div>
        </div>
      </button>
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div id={regionId} className="px-3 pb-3 pt-0">
              <div className="p-3 rounded-lg bg-muted/40 border border-glass-border">
                <p className="text-xs text-muted-foreground leading-relaxed whitespace-pre-wrap">
                  {source.content}
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
