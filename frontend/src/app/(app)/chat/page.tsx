"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  StopCircle,
  Trash2,
  MessageSquare,
  Plus,
  FileText,
  ChevronDown,
  ChevronRight,
  Copy,
  Check,
  Sparkles,
  Search,
} from "lucide-react";
import {
  getConversations,
  getConversation,
  deleteConversation,
  sendChatMessage,
} from "@/services/api";
import { GlassCard } from "@/components/ui/glass-card";
import { GlassButton } from "@/components/ui/glass-button";
import { GlassBadge } from "@/components/ui/glass-badge";
import { useChatStore } from "@/stores/chat";
import { useSettings } from "@/stores/settings";
import { formatDate, cn } from "@/lib/utils";
import type { ChatMessage, Chunk, AttributedSourceDTO, ConfidenceDTO, PipelineInfoDTO } from "@/types";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AnswerFooter } from "@/components/chat/answer-footer";
import { SearchInspector } from "@/components/chat/search-inspector";

export default function ChatPage() {
  const {
    conversations,
    activeConversationId,
    isStreaming,
    streamingContent,
    setConversations,
    setActiveConversation,
    addConversation,
    addMessage,
    setIsStreaming,
    setStreamingContent,
    appendStreamingContent,
    removeConversation,
    updateConversationId,
  } = useChatStore();

  const settings = useSettings();
  const [input, setInput] = useState("");
  const [expandedSource, setExpandedSource] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [sources, setSources] = useState<Chunk[]>([]);
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  const { data: conversationDetail } = useQuery({
    queryKey: ["conversation", activeConversationId],
    queryFn: () => getConversation(activeConversationId!),
    enabled: !!activeConversationId && !conversations.find(
      (c) => c.id === activeConversationId,
    )?.messages.length,
  });

  const activeConversation = conversations.find(
    (c) => c.id === activeConversationId,
  );
  const localMessages = activeConversation?.messages ?? [];
  const messages =
    localMessages.length > 0
      ? localMessages
      : conversationDetail?.messages ?? [];
  const messagesLength = messages.length;
  const streamingContentLen = streamingContent.length;

  const { data: convList } = useQuery({
    queryKey: ["conversations"],
    queryFn: getConversations,
    refetchInterval: 10_000,
  });

  useEffect(() => {
    if (convList) {
      setConversations(convList);
    }
  }, [convList, setConversations]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messagesLength, streamingContentLen]);

  useEffect(() => {
    inputRef.current?.focus();
  }, [activeConversationId]);

  const sendMutation = useMutation({
    mutationFn: async (params: {
      query: string;
      conversation_id?: string;
      temperature?: number;
      top_k?: number;
      max_tokens?: number;
      signal?: AbortSignal;
    }) => {
      const { signal, ...rest } = params;
      return sendChatMessage(rest, signal);
    },
    onSuccess: (result) => {
      const convId = useChatStore.getState().activeConversationId;
      if (convId) {
        if (result.conversation_id && result.conversation_id !== convId) {
          updateConversationId(convId, result.conversation_id);
        }
        addMessage(useChatStore.getState().activeConversationId!, {
          role: "assistant",
          content: result.answer,
          confidence: result.confidence,
          attributed_sources: result.attributed_sources,
          pipeline: result.pipeline,
        });
        setSources(result.sources);
      }
      setIsStreaming(false);
    },
    onError: () => {
      setIsStreaming(false);
    },
  });

  const handleSend = useCallback(
    async (overrideText?: string) => {
      const text = (overrideText ?? input).trim();
      if (!text || isStreaming) return;

      setInput("");
      setSources([]);

      let convId = activeConversationId;

      if (!convId) {
        const newConv = {
          id: crypto.randomUUID(),
          messages: [],
          created_at: new Date().toISOString(),
          title: text.slice(0, 50),
        };
        addConversation(newConv);
        convId = newConv.id;
      }

      addMessage(convId, { role: "user", content: text });
      setIsStreaming(true);
      setStreamingContent("");

      const controller = new AbortController();
      abortRef.current = controller;

      sendMutation.mutate({
        query: text,
        conversation_id: convId,
        temperature: settings.temperature,
        top_k: settings.top_k,
        max_tokens: 2048,
        signal: controller.signal,
      });
    },
    [
      input,
      isStreaming,
      activeConversationId,
      addConversation,
      addMessage,
      setIsStreaming,
      setStreamingContent,
      sendMutation,
      settings.temperature,
      settings.top_k,
    ],
  );

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleNewChat = () => {
    setActiveConversation(null);
    setInput("");
    setSources([]);
    setStreamingContent("");
  };

  const handleDeleteConversation = async (id: string) => {
    try {
      await deleteConversation(id);
      removeConversation(id);
    } catch {
      // ignore
    }
  };

  const handleCopy = async (content: string, id: string) => {
    await navigator.clipboard.writeText(content);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleRegenerate = () => {
    if (messages.length >= 2) {
      const lastUserMsg = [...messages]
        .reverse()
        .find((m) => m.role === "user");
      if (lastUserMsg) {
        handleSend(lastUserMsg.content);
      }
    }
  };

  return (
    <div className="flex h-[calc(100vh-0px)]">
      {/* Sidebar: conversation list */}
      <div className="w-72 border-r border-glass-border bg-glass/30 backdrop-blur-xl flex flex-col shrink-0">
        <div className="p-3 border-b border-glass-border">
          <GlassButton
            onClick={handleNewChat}
            className="w-full"
            variant="secondary"
            size="sm"
            icon={<Plus className="h-4 w-4" />}
          >
            New Chat
          </GlassButton>
        </div>
        <div className="flex-1 overflow-y-auto scrollbar-thin p-2 space-y-1">
          {conversations.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <MessageSquare className="h-6 w-6 mx-auto mb-2 opacity-50" />
              <p className="text-xs">No conversations yet</p>
            </div>
          )}
          {conversations.map((conv) => (
            <div key={conv.id} className="group relative">
              <button
                onClick={() => {
                  setActiveConversation(conv.id);
                  setSources([]);
                  setStreamingContent("");
                }}
                className={cn(
                  "w-full text-left p-2.5 rounded-xl text-sm transition-all duration-200",
                  "hover:bg-muted/50",
                  activeConversationId === conv.id
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground",
                )}
              >
                <p className="truncate font-medium">
                  {conv.title || "New Chat"}
                </p>
                <p className="text-xs opacity-60 mt-0.5">
                  {conv.message_count ?? conv.messages.length} messages
                </p>
              </button>
              <button
                onClick={() => handleDeleteConversation(conv.id)}
                className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 p-1 rounded-lg text-muted-foreground hover:text-danger hover:bg-danger/10 transition-all"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className={cn("flex-1 flex flex-col min-w-0", inspectorOpen && "hidden lg:flex")}>
        {/* Messages */}
        <div className="flex-1 overflow-y-auto scrollbar-thin">
          <div className="max-w-3xl mx-auto p-6 space-y-6">
            {messages.length === 0 && !isStreaming && (
              <div className="flex flex-col items-center justify-center py-24 text-center">
                <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-6">
                  <Sparkles className="h-8 w-8 text-primary" />
                </div>
                <h2 className="text-2xl font-semibold mb-2">
                  Ask anything
                </h2>
                <p className="text-muted-foreground max-w-md">
                  Your documents never leave your machine. Ask questions
                  about your indexed knowledge base.
                </p>
              </div>
            )}

            <AnimatePresence initial={false}>
              {messages.map((msg, i) => (
                <motion.div
                  key={`${msg.role}-${i}`}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: i * 0.05 }}
                >
                  {msg.role === "user" ? (
                    <div className="flex justify-end">
                      <div className="max-w-[75%] px-4 py-3 rounded-2xl bg-primary/10 border border-primary/20 text-sm">
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="flex gap-3">
                      <div className="flex items-center justify-center w-8 h-8 rounded-xl bg-primary/10 shrink-0 mt-1">
                        <Sparkles className="h-4 w-4 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                          <GlassCard className="p-4 prose prose-sm dark:prose-invert max-w-none">
                            <ReactMarkdown
                              remarkPlugins={[remarkGfm]}
                              components={{
                                pre: ({ children }) => (
                                  <pre className="border border-glass-border rounded-xl overflow-hidden relative group/pre">
                                    {children}
                                  </pre>
                                ),
                                code: ({
                                  className,
                                  children,
                                  ...props
                                }) => {
                                  const match = /language-(\w+)/.exec(className || "");
                                  const isInline = !className;
                                  if (isInline) {
                                    return (
                                      <code
                                        className="px-1.5 py-0.5 rounded-md bg-muted text-sm"
                                        {...props}
                                      >
                                        {children}
                                      </code>
                                    );
                                  }
                                  return (
                                    <div className="relative">
                                      {match && (
                                        <div className="flex items-center justify-between px-4 py-1.5 border-b border-glass-border bg-muted/30">
                                          <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                                            {match[1]}
                                          </span>
                                        </div>
                                      )}
                                      <code
                                        className="block p-4 overflow-x-auto text-sm"
                                        {...props}
                                      >
                                        {children}
                                      </code>
                                    </div>
                                  );
                                },
                              }}
                            >
                            {msg.content}
                          </ReactMarkdown>
                        </GlassCard>

                        {/* Action buttons */}
                        <div className="flex items-center gap-1 mt-2 px-1">
                          <button
                            onClick={() => handleCopy(msg.content, `msg-${i}`)}
                            className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
                            title="Copy message"
                          >
                            {copiedId === `msg-${i}` ? (
                              <Check className="h-3.5 w-3.5 text-success" />
                            ) : (
                              <Copy className="h-3.5 w-3.5" />
                            )}
                          </button>
                          {i === messages.length - 1 && (
                            <button
                              onClick={handleRegenerate}
                              className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors text-xs"
                              title="Regenerate"
                            >
                              Regenerate
                            </button>
                          )}
                        </div>

                        {/* Answer Footer: confidence + sources */}
                        {i === messages.length - 1 && (
                          <AnswerFooter
                            confidence={(msg as any).confidence as ConfidenceDTO | null | undefined}
                            attributedSources={(msg as any).attributed_sources as AttributedSourceDTO[] | null | undefined}
                            onOpenInspector={() => setInspectorOpen(!inspectorOpen)}
                          />
                        )}
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Streaming response */}
            {isStreaming && streamingContent && (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-3"
              >
                <div className="flex items-center justify-center w-8 h-8 rounded-xl bg-primary/10 shrink-0 mt-1">
                  <Sparkles className="h-4 w-4 text-primary animate-pulse-soft" />
                </div>
                <div className="flex-1 min-w-0">
                  <GlassCard className="p-4 prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {streamingContent}
                    </ReactMarkdown>
                  </GlassCard>
                </div>
              </motion.div>
            )}

            {/* Typing indicator */}
            {isStreaming && !streamingContent && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex gap-3"
              >
                <div className="flex items-center justify-center w-8 h-8 rounded-xl bg-primary/10 shrink-0 mt-1">
                  <Sparkles className="h-4 w-4 text-primary" />
                </div>
                <div className="flex items-center gap-1.5 px-4 py-3 rounded-2xl glass">
                  <span className="w-2 h-2 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-2 h-2 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-2 h-2 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <div className="border-t border-glass-border bg-glass/30 backdrop-blur-xl">
          <div className="max-w-3xl mx-auto p-4">
            <div className="relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question about your documents..."
                rows={1}
                className="w-full resize-none rounded-2xl border border-glass-border bg-glass backdrop-blur-xl px-4 py-3 pr-24 text-sm placeholder:text-muted-foreground/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-all"
                style={{ minHeight: "48px", maxHeight: "200px" }}
                onInput={(e) => {
                  const target = e.currentTarget;
                  target.style.height = "auto";
                  target.style.height = `${Math.min(target.scrollHeight, 200)}px`;
                }}
                disabled={isStreaming}
              />
              <div className="absolute right-2 bottom-2 flex items-center gap-1">
                {isStreaming && (
                  <button
                    onClick={() => {
                      abortRef.current?.abort();
                      setIsStreaming(false);
                    }}
                    className="p-2 rounded-xl text-danger hover:bg-danger/10 transition-colors"
                    title="Stop generation"
                  >
                    <StopCircle className="h-4 w-4" />
                  </button>
                )}
                <button
                  onClick={() => handleSend()}
                  disabled={!input.trim() || isStreaming}
                  className="p-2 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Send message"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
            <p className="text-xs text-center text-muted-foreground/60 mt-2">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </div>
      </div>

      {/* Search Inspector Panel */}
      {inspectorOpen && (
        <div className="w-80 border-l border-glass-border bg-glass/30 backdrop-blur-xl flex flex-col shrink-0 overflow-y-auto">
          <div className="p-4 border-b border-glass-border flex items-center justify-between">
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <Search className="h-4 w-4" />
              Search Inspector
            </h3>
            <button
              onClick={() => setInspectorOpen(false)}
              className="p-1 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors text-xs"
            >
              Close
            </button>
          </div>
          <div className="p-4">
            {messages.length >= 2 && (() => {
              const lastAssistant = [...messages].reverse().find(m => m.role === "assistant");
              if (!lastAssistant) {
                return <p className="text-xs text-muted-foreground">No response yet.</p>;
              }
              return (
                <SearchInspector
                  pipeline={(lastAssistant as any).pipeline as PipelineInfoDTO | null | undefined}
                  attributedSources={(lastAssistant as any).attributed_sources as AttributedSourceDTO[] | null | undefined}
                  confidence={(lastAssistant as any).confidence as ConfidenceDTO | null | undefined}
                />
              );
            })()}
          </div>
        </div>
      )}
    </div>
  );
}
