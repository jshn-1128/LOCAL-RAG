"use client";

import { useState, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  FileText,
  Trash2,
  RefreshCw,
  Search,
  Upload,
  Clock,
  Hash,
  FileUp,
} from "lucide-react";
import {
  getDocuments,
  deleteDocument,
  uploadDocument,
} from "@/services/api";
import { GlassCard } from "@/components/ui/glass-card";
import { GlassButton } from "@/components/ui/glass-button";
import { GlassInput } from "@/components/ui/glass-input";
import { GlassBadge } from "@/components/ui/glass-badge";
import { GlassProgress } from "@/components/ui/glass-progress";
import { GlassDialog } from "@/components/ui/glass-dialog";
import { useToast } from "@/components/ui/glass-toast";
import { formatDate, cn } from "@/lib/utils";

export default function DocumentsPage() {
  const queryClient = useQueryClient();
  const toast = useToast();
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const { data: documents = [], isLoading } = useQuery({
    queryKey: ["documents"],
    queryFn: getDocuments,
    refetchInterval: 10_000,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      toast.show({ title: "Document deleted", variant: "success" });
    },
    onError: () => {
      toast.show({ title: "Failed to delete", variant: "error" });
    },
  });

  const filtered = documents.filter(
    (doc) =>
      doc.filename.toLowerCase().includes(search.toLowerCase()) ||
      (doc.title && doc.title.toLowerCase().includes(search.toLowerCase())),
  );

  const handleDelete = async (id: string) => {
    deleteMutation.mutate(id);
    setSelected((prev) => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  };

  const handleDeleteSelected = () => {
    selected.forEach((id) => deleteMutation.mutate(id));
    setSelected(new Set());
  };

  const handleSelect = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleFileDrop = useCallback(
    async (fileList: FileList) => {
      setDragOver(false);
      setUploading(true);

      const files = Array.from(fileList);

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        try {
          setUploadProgress(((i + 1) / files.length) * 100);
          await uploadDocument(file);
          toast.show({
            title: `Uploaded ${file.name}`,
            variant: "success",
          });
        } catch (err) {
          toast.show({
            title: `Failed to upload ${file.name}`,
            description: err instanceof Error ? err.message : "Unknown error",
            variant: "error",
          });
        }
      }

      setUploading(false);
      setUploadProgress(0);
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
    [queryClient, toast],
  );

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => setDragOver(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      handleFileDrop(e.dataTransfer.files);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">Documents</h1>
          <p className="text-muted-foreground">
            {documents.length} document{documents.length !== 1 ? "s" : ""}{" "}
            indexed
          </p>
        </div>
        <div className="flex items-center gap-2">
          {selected.size > 0 && (
            <GlassButton
              variant="danger"
              size="sm"
              onClick={handleDeleteSelected}
              icon={<Trash2 className="h-4 w-4" />}
            >
              Delete {selected.size}
            </GlassButton>
          )}
          <GlassButton
            variant="secondary"
            size="sm"
            onClick={() =>
              queryClient.invalidateQueries({ queryKey: ["documents"] })
            }
            icon={<RefreshCw className="h-4 w-4" />}
          >
            Refresh
          </GlassButton>
        </div>
      </div>

      {/* Upload Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          "relative rounded-2xl border-2 border-dashed transition-all duration-200 p-8 text-center",
          dragOver
            ? "border-primary bg-primary/5"
            : "border-glass-border hover:border-muted-foreground/30",
        )}
      >
        {uploading ? (
          <div className="space-y-3">
            <Upload className="h-8 w-8 mx-auto text-primary animate-bounce" />
            <p className="text-sm font-medium">Uploading documents...</p>
            <GlassProgress value={uploadProgress} className="max-w-xs mx-auto" />
          </div>
        ) : (
          <div className="space-y-3">
            <FileUp className="h-10 w-10 mx-auto text-muted-foreground/50" />
            <div>
              <p className="text-sm font-medium">
                Drop files here or click to upload
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Supports PDF, TXT, DOCX, MD — up to 50MB per file
              </p>
            </div>
            <label className="inline-flex cursor-pointer">
              <span className="inline-flex items-center justify-center gap-2 rounded-xl border backdrop-blur-xl px-4 py-2 text-sm font-medium glass glass-hover text-foreground border-glass-border transition-all duration-200">
                Choose Files
              </span>
              <input
                type="file"
                multiple
                accept=".pdf,.txt,.docx,.md"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files?.length) {
                    handleFileDrop(e.target.files);
                  }
                  e.target.value = "";
                }}
              />
            </label>
          </div>
        )}
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <GlassInput
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search documents..."
          className="pl-9"
        />
      </div>

      {/* Document List */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="h-20 rounded-2xl bg-glass animate-pulse border border-glass-border"
            />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <GlassCard className="text-center py-16">
          <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground/30" />
          <h3 className="text-lg font-medium mb-1">No documents found</h3>
          <p className="text-sm text-muted-foreground">
            {search
              ? "Try a different search term"
              : "Upload documents to get started"}
          </p>
        </GlassCard>
      ) : (
        <div className="space-y-2">
          {filtered.map((doc, idx) => (
            <motion.div
              key={doc.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.03 }}
              className={cn(
                "glass rounded-2xl border transition-all duration-200",
                selected.has(doc.id)
                  ? "border-primary/40 bg-primary/5"
                  : "border-glass-border hover:border-muted-foreground/20",
              )}
            >
              <div className="p-4 flex items-center gap-4">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selected.has(doc.id)}
                    onChange={() => handleSelect(doc.id)}
                    className="rounded border-glass-border text-primary focus:ring-primary"
                  />
                </label>
                <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-primary/10 shrink-0">
                  <FileText className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{doc.filename}</p>
                  <p className="text-xs text-muted-foreground truncate mt-0.5">
                    {doc.title || "Untitled"}
                  </p>
                </div>
                <div className="hidden md:flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Hash className="h-3 w-3" />
                    {doc.checksum ? doc.checksum.slice(0, 8) : "—"}...
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {doc.loaded_at ? formatDate(doc.loaded_at) : "—"}
                  </span>
                </div>
                <GlassBadge variant="default" size="sm">
                  {doc.file_type || "—"}
                </GlassBadge>
                <button
                  onClick={() => setDeleteTarget(doc.id)}
                  className="p-2 rounded-xl text-muted-foreground hover:text-danger hover:bg-danger/10 transition-colors"
                  aria-label={`Delete ${doc.filename}`}
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}
      <GlassDialog
        open={deleteTarget !== null}
        onOpenChange={(open) => { if (!open) setDeleteTarget(null); }}
        title="Delete document"
        description={
          deleteTarget
            ? `Are you sure you want to delete "${documents.find(d => d.id === deleteTarget)?.filename ?? "this document"}"? This action cannot be undone.`
            : ""
        }
      >
        <div className="flex justify-end gap-2">
          <GlassButton
            variant="secondary"
            size="sm"
            onClick={() => setDeleteTarget(null)}
          >
            Cancel
          </GlassButton>
          <GlassButton
            variant="danger"
            size="sm"
            onClick={() => {
              if (deleteTarget) handleDelete(deleteTarget);
              setDeleteTarget(null);
            }}
          >
            Delete
          </GlassButton>
        </div>
      </GlassDialog>
    </div>
  );
}
