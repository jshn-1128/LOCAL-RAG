import type {
  HealthStatus,
  SystemStatus,
  Document,
  IndexingResult,
  ChatResult,
  Conversation,
  SearchResponse,
  Chunk,
} from "@/types";
import type {
  HealthDTO,
  DocumentListDTO,
  DocumentDetailDTO,
  ChatResponseDTO,
  ConversationListDTO,
  ConversationDetailDTO,
  SearchResponseDTO,
  IndexResponseDTO,
  SearchResultItemDTO,
} from "@/types";

const DEFAULT_BASE_URL = "http://localhost:8000";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function getBaseUrl(): string {
  if (typeof window === "undefined") return DEFAULT_BASE_URL;
  return localStorage.getItem("backend_url") || DEFAULT_BASE_URL;
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${getBaseUrl()}${endpoint}`;

  const controller = options.signal
    ? null
    : new AbortController();
  const timeoutId = controller
    ? setTimeout(() => controller.abort(), 30000)
    : undefined;

  try {
    const response = await fetch(url, {
      ...options,
      signal: options.signal ?? controller?.signal,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const text = await response.text().catch(() => "Unknown error");
      throw new ApiError(response.status, text);
    }

    const text = await response.text();
    return text ? JSON.parse(text) : ({} as T);
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof ApiError) throw error;
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error(timeoutId ? "Request timed out" : "Request cancelled");
    }
    throw error;
  }
}

// ──────────────────────────────────────────────────
// Health
// ──────────────────────────────────────────────────

export async function getHealth(): Promise<HealthStatus> {
  const dto = await request<HealthDTO>("/health");
  return {
    status: dto.status,
    version: dto.version,
    uptime: dto.uptime_seconds,
    timestamp: dto.timestamp,
  };
}

// ──────────────────────────────────────────────────
// System
// ──────────────────────────────────────────────────

export async function getSystemStatus(): Promise<SystemStatus> {
  const [health, ollama, documents, count] = await Promise.all([
    getHealth().catch(() => null),
    getOllamaStatus().catch(() => null),
    getDocuments().catch<Document[]>(() => []),
    getVectorCount().catch(() => 0),
  ]);

  return {
    health: health || { status: "unreachable", version: "?", uptime: 0, timestamp: 0 },
    ollama: ollama || { available: false, model: "?", host: "?" },
    document_count: documents.length,
    vector_count: count,
    embedding_model: null,
    llm_model: ollama?.model || null,
    environment: process.env.NODE_ENV || "development",
    memory_type: null,
    vector_store_type: null,
  };
}

export async function getOllamaStatus(): Promise<{
  available: boolean;
  model: string;
  host: string;
}> {
  try {
    const dto = await request<HealthDTO>("/health");
    return {
      available: dto.status === "ok" || dto.status === "healthy",
      model: localStorage.getItem("preferred_model") || "llama3.2",
      host: getBaseUrl(),
    };
  } catch {
    return { available: false, model: "unreachable", host: "?" };
  }
}

// ──────────────────────────────────────────────────
// Documents
// ──────────────────────────────────────────────────

export async function getDocuments(): Promise<Document[]> {
  const dto = await request<DocumentListDTO>("/documents");
  return (dto.documents ?? []).map((item) => ({
    id: item.id,
    filename: item.filename,
    file_type: item.file_type,
    checksum: item.checksum,
    loaded_at: item.loaded_at,
  }));
}

export async function getDocument(id: string): Promise<Document | null> {
  try {
    const dto = await request<DocumentDetailDTO>(`/documents/${id}`);
    return {
      id: dto.id,
      filename: dto.filename,
      title: dto.title,
      file_type: dto.file_type,
      mime_type: dto.mime_type,
      checksum: dto.checksum,
      encoding: dto.encoding,
      loaded_at: dto.loaded_at,
    };
  } catch {
    return null;
  }
}

export async function deleteDocument(id: string): Promise<void> {
  await request(`/documents/${id}`, { method: "DELETE" });
}

export async function indexFile(filePath: string): Promise<IndexingResult> {
  const dto = await request<IndexResponseDTO>("/documents/index", {
    method: "POST",
    body: JSON.stringify({ path: filePath }),
  });
  return { ...dto, skipped: dto.skipped ?? false };
}

export async function uploadDocument(
  file: File,
  signal?: AbortSignal,
): Promise<IndexingResult> {
  const formData = new FormData();
  formData.append("file", file);

  const controller = signal ? null : new AbortController();
  const timeoutId = controller
    ? setTimeout(() => controller.abort(), 120000)
    : undefined;

  try {
    const response = await fetch(`${getBaseUrl()}/documents/upload`, {
      method: "POST",
      body: formData,
      signal: signal ?? controller?.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new ApiError(response.status, await response.text());
    }

    const dto: IndexResponseDTO = await response.json();
    return { ...dto, skipped: dto.skipped ?? false };
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof ApiError) throw error;
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("Upload timed out or was cancelled");
    }
    throw error;
  }
}

export async function indexDirectory(
  directory: string,
): Promise<IndexingResult[]> {
  const dtos = await request<IndexResponseDTO[]>("/documents/index", {
    method: "POST",
    body: JSON.stringify({ path: directory, recursive: true }),
  });
  return (Array.isArray(dtos) ? dtos : [dtos]).map((d) => ({
    ...d,
    skipped: d.skipped ?? false,
  }));
}

export async function getVectorCount(): Promise<number> {
  try {
    const data = await request<{ count: number }>("/documents/vector-count");
    return data.count;
  } catch {
    return 0;
  }
}

// ──────────────────────────────────────────────────
// Chat
// ──────────────────────────────────────────────────

function mapChunkSource(dto: { chunk_id: string; document_id: string; content: string; index: number; score?: number | null }): Chunk {
  return {
    id: dto.chunk_id,
    document_id: dto.document_id,
    content: dto.content,
    index: dto.index,
    score: dto.score ?? undefined,
  };
}

export async function sendChatMessage(
  params: {
    query: string;
    conversation_id?: string;
    temperature?: number;
    max_tokens?: number;
  },
  signal?: AbortSignal,
): Promise<ChatResult> {
  const dto = await request<ChatResponseDTO>("/chat", {
    method: "POST",
    body: JSON.stringify({
      message: params.query,
      conversation_id: params.conversation_id,
      temperature: params.temperature,
      max_tokens: params.max_tokens,
    }),
    signal,
  });

  return {
    query_id: "",
    conversation_id: dto.conversation_id,
    answer: dto.answer,
    sources: dto.sources.map(mapChunkSource),
    model: dto.model,
    prompt_tokens: dto.estimated_tokens,
  };
}

export async function sendChatMessageStream(
  params: {
    query: string;
    conversation_id?: string;
    temperature?: number;
    max_tokens?: number;
  },
  onChunk: (chunk: string) => void,
  onDone: (result: ChatResult) => void,
  onError: (error: Error) => void,
): Promise<AbortController> {
  const controller = new AbortController();

  try {
    const response = await fetch(`${getBaseUrl()}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: params.query,
        conversation_id: params.conversation_id,
        temperature: params.temperature,
        max_tokens: params.max_tokens,
        stream: true,
      }),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`Chat stream failed: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error("No response body");

    const decoder = new TextDecoder();
    let buffer = "";
    let fullAnswer = "";

    const processStream = async () => {
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6);
              if (data === "[DONE]") continue;
              try {
                const parsed = JSON.parse(data);
                if (parsed.token) {
                  fullAnswer += parsed.token;
                  onChunk(parsed.token);
                }
                if (parsed.done) {
                  const result: ChatResult = {
                    query_id: "",
                    conversation_id: params.conversation_id || "",
                    answer: fullAnswer,
                    sources: (parsed.result?.sources ?? []).map(mapChunkSource),
                    model: parsed.result?.model || "",
                    prompt_tokens: parsed.result?.estimated_tokens || 0,
                  };
                  onDone(parsed.result ? result : { ...result, answer: fullAnswer });
                }
              } catch {
                // skip malformed JSON
              }
            }
          }
        }

        onDone({
          query_id: "",
          conversation_id: params.conversation_id || "",
          answer: fullAnswer,
          sources: [],
          model: "",
          prompt_tokens: 0,
        });
      } catch (err) {
        if (!controller.signal.aborted) {
          onError(err instanceof Error ? err : new Error(String(err)));
        }
      }
    };

    processStream();
  } catch (err) {
    if (!controller.signal.aborted) {
      onError(err instanceof Error ? err : new Error(String(err)));
    }
  }

  return controller;
}

// ──────────────────────────────────────────────────
// Conversations
// ──────────────────────────────────────────────────

export async function getConversations(): Promise<Conversation[]> {
  const dto = await request<ConversationListDTO>("/chat");
  return (dto.conversations ?? []).map((item) => ({
    id: item.id,
    messages: [],
    created_at: item.created_at,
    updated_at: item.updated_at ?? undefined,
    title: item.title ?? undefined,
    message_count: item.message_count,
  }));
}

export async function getConversation(
  id: string,
): Promise<Conversation | null> {
  try {
    const dto = await request<ConversationDetailDTO>(`/chat/${id}`);
    return {
      id: dto.conversation_id,
      messages: dto.messages.map((m) => ({
        role: m.role as "user" | "assistant",
        content: m.content,
      })),
      created_at: dto.messages[0]?.timestamp ?? "",
      updated_at: dto.messages[dto.messages.length - 1]?.timestamp,
    };
  } catch {
    return null;
  }
}

export async function deleteConversation(id: string): Promise<void> {
  await request(`/chat/${id}`, { method: "DELETE" });
}

// ──────────────────────────────────────────────────
// Search
// ──────────────────────────────────────────────────

export async function searchInspector(
  query: string,
  top_k?: number,
): Promise<SearchResponse> {
  const dto = await request<SearchResponseDTO>("/search", {
    method: "POST",
    body: JSON.stringify({ query, top_k }),
  });

  return {
    query: dto.query,
    results: {
      query_id: "",
      chunks: dto.results.map((item: SearchResultItemDTO) => ({
        id: item.chunk_id,
        document_id: item.document_id,
        content: item.content,
        index: item.index,
        score: item.score,
      })),
      scores: dto.results.map((item: SearchResultItemDTO) => item.score),
    },
  };
}
