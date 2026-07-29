"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  TrendingUp,
  FileText,
  ArrowRight,
  Layers,
  MessageSquare,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import { searchInspector } from "@/services/api";
import { GlassCard } from "@/components/ui/glass-card";
import { GlassButton } from "@/components/ui/glass-button";
import { GlassInput } from "@/components/ui/glass-input";
import { GlassBadge } from "@/components/ui/glass-badge";
import { GlassProgress } from "@/components/ui/glass-progress";
import { useSettings } from "@/stores/settings";
import { cn } from "@/lib/utils";
import type { SearchResponse } from "@/types";

export default function SearchPage() {
  const settings = useSettings();
  const [query, setQuery] = useState("");
  const [expandedChunk, setExpandedChunk] = useState<string | null>(null);

  const searchMutation = useMutation({
    mutationFn: (q: string) => searchInspector(q, settings.top_k),
  });

  const handleSearch = () => {
    if (!query.trim()) return;
    searchMutation.mutate(query);
  };

  const result = searchMutation.data;

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight">
          Search Inspector
        </h1>
        <p className="text-muted-foreground">
          Inspect the RAG pipeline step by step
        </p>
      </div>

      {/* Search Input */}
      <div className="flex gap-3">
        <GlassInput
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter a question to inspect the RAG pipeline..."
          className="flex-1"
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
        />
        <GlassButton
          onClick={handleSearch}
          loading={searchMutation.isPending}
          icon={<Search className="h-4 w-4" />}
        >
          Inspect
        </GlassButton>
      </div>

      <AnimatePresence>
        {searchMutation.isError && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
          >
            <GlassCard className="border-danger/30 text-danger text-sm">
              Failed to inspect. Is the backend running?
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {!searchMutation.isIdle && searchMutation.isPending && (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="h-24 rounded-2xl bg-glass animate-pulse border border-glass-border"
            />
          ))}
        </div>
      )}

      {searchMutation.isIdle && !searchMutation.isPending && (
        <div className="text-center py-16">
          <Search className="h-12 w-12 mx-auto mb-4 text-muted-foreground/20" />
          <h3 className="text-lg font-medium mb-1">Inspect the RAG pipeline</h3>
          <p className="text-sm text-muted-foreground max-w-md mx-auto">
            Enter a question above to see exactly which chunks are retrieved, their similarity scores, and how they rank against your query.
          </p>
        </div>
      )}

      {result && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-6"
        >
          {/* Query */}
          <GlassCard>
            <div className="flex items-center gap-3 mb-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-primary/10">
                <MessageSquare className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Query</p>
                <p className="text-sm font-medium">{result.query}</p>
              </div>
            </div>
          </GlassCard>

          {/* Arrow */}
          <div className="flex justify-center">
            <ArrowRight className="h-6 w-6 text-muted-foreground" />
          </div>

          {/* Retrieved Chunks */}
          <GlassCard>
            <div className="flex items-center gap-3 mb-4">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-accent/10">
                <Layers className="h-5 w-5 text-accent" />
              </div>
              <div>
                <p className="text-sm font-medium">Retrieved Chunks</p>
                <p className="text-xs text-muted-foreground">
                  {result.results?.chunks?.length ?? 0} chunks retrieved
                </p>
              </div>
            </div>

            {(!result.results?.chunks || result.results.chunks.length === 0) ? (
              <div className="text-center py-8">
                <Layers className="h-8 w-8 mx-auto mb-2 text-muted-foreground/30" />
                <p className="text-sm text-muted-foreground">
                  No relevant chunks found. Try a different query.
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {result.results.chunks.map((chunk, i) => (
                  <div key={chunk.id}>
                    <button
                      onClick={() =>
                        setExpandedChunk(
                          expandedChunk === chunk.id ? null : chunk.id,
                        )
                      }
                      className={cn(
                        "w-full flex items-center gap-3 p-3 rounded-xl transition-colors",
                        "hover:bg-muted/50",
                      )}
                    >
                      <div
                        className={cn(
                          "flex items-center justify-center w-8 h-8 rounded-lg shrink-0",
                          "text-xs font-semibold",
                          i === 0
                            ? "bg-success/10 text-success"
                            : "bg-muted text-muted-foreground",
                        )}
                      >
                        #{i + 1}
                      </div>
                      <div className="flex-1 min-w-0 text-left">
                        <p className="text-sm truncate">{chunk.content}</p>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {result.results.scores[i] !== undefined && (
                          <span
                            className={cn(
                              "text-xs font-medium",
                              result.results.scores[i] > 0.3
                                ? "text-success"
                                : result.results.scores[i] > 0.2
                                  ? "text-warning"
                                  : "text-muted-foreground",
                            )}
                          >
                            {result.results.scores[i].toFixed(3)}
                          </span>
                        )}
                        {expandedChunk === chunk.id ? (
                          <ChevronDown className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <ChevronRight className="h-4 w-4 text-muted-foreground" />
                        )}
                      </div>
                    </button>
                    <AnimatePresence>
                      {expandedChunk === chunk.id && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="overflow-hidden"
                        >
                          <div className="ml-12 p-3 mb-2 rounded-xl bg-muted/30 border border-glass-border">
                            <p className="text-sm whitespace-pre-wrap">
                              {chunk.content}
                            </p>
                            <div className="mt-3 flex flex-wrap gap-2">
                              <GlassBadge size="sm" variant="default">
                                Index: {chunk.index}
                              </GlassBadge>
                              <GlassBadge size="sm" variant="default">
                                Document: {chunk.document_id.slice(0, 8)}...
                              </GlassBadge>
                              <GlassBadge
                                size="sm"
                                variant={
                                  result.results.scores[i] > 0.3
                                    ? "success"
                                    : result.results.scores[i] > 0.2
                                      ? "warning"
                                      : "default"
                                }
                              >
                                Score: {result.results.scores[i]?.toFixed(4) ?? "—"}
                              </GlassBadge>
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                ))}
              </div>
            )}
          </GlassCard>

          {/* Scores Visualization */}
          {result.results?.scores && result.results.scores.length > 0 && (
            <GlassCard>
              <div className="flex items-center gap-3 mb-4">
                <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-success/10">
                  <TrendingUp className="h-5 w-5 text-success" />
                </div>
                <div>
                  <p className="text-sm font-medium">Similarity Scores</p>
                  <p className="text-xs text-muted-foreground">
                    Top score:{" "}
                    {Math.max(...result.results.scores).toFixed(4)}
                  </p>
                </div>
              </div>
              <div className="space-y-2">
                {result.results.scores.map((score, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground w-6">
                      #{i + 1}
                    </span>
                    <GlassProgress
                      value={score * 100}
                      max={100}
                      className="flex-1"
                      variant={
                        score > 0.3
                          ? "success"
                          : score > 0.2
                            ? "warning"
                            : "default"
                      }
                    />
                    <span
                      className={cn(
                        "text-xs font-mono w-12 text-right",
                        score > 0.3
                          ? "text-success"
                          : score > 0.2
                            ? "text-warning"
                            : "text-muted-foreground",
                      )}
                    >
                      {score.toFixed(3)}
                    </span>
                  </div>
                ))}
              </div>
            </GlassCard>
          )}

          {/* Total Results */}
          {result.results.chunks.length > 0 && (
            <>
              <div className="flex justify-center">
                <ArrowRight className="h-6 w-6 text-muted-foreground" />
              </div>
              <GlassCard>
                <div className="flex items-center gap-3 mb-3">
                  <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-muted">
                    <p className="text-2xl font-bold">{result.results.chunks.length}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium">Total Results</p>
                    <p className="text-xs text-muted-foreground">
                      Retrieved from vector store
                    </p>
                  </div>
                </div>
              </GlassCard>
            </>
          )}
        </motion.div>
      )}
    </div>
  );
}
