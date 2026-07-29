// ──────────────────────────────────────────────────
// Backend DTOs — exact shapes returned by FastAPI
// ──────────────────────────────────────────────────

export interface HealthDTO {
  status: string;
  version: string;
  environment: string;
  timestamp: number;
  uptime_seconds: number;
  app_name: string;
}

export interface DocumentListItemDTO {
  id: string;
  filename: string;
  file_type: string;
  checksum: string;
  loaded_at: string;
}

export interface DocumentListDTO {
  documents: DocumentListItemDTO[];
}

export interface DocumentDetailDTO {
  id: string;
  filename: string;
  title: string;
  file_type: string;
  mime_type: string;
  checksum: string;
  encoding: string;
  word_count: number;
  character_count: number;
  loaded_at: string;
}

export interface ChatResponseDTO {
  conversation_id: string;
  answer: string;
  sources: ChunkSourceDTO[];
  model: string;
  estimated_tokens: number;
}

export interface ChunkSourceDTO {
  chunk_id: string;
  document_id: string;
  content: string;
  index: number;
  score: number | null;
}

export interface ConversationListItemDTO {
  id: string;
  title: string | null;
  message_count: number;
  created_at: string;
  updated_at: string | null;
}

export interface ConversationListDTO {
  conversations: ConversationListItemDTO[];
}

export interface ConversationDetailDTO {
  conversation_id: string;
  messages: ChatMessageDTO[];
}

export interface ChatMessageDTO {
  role: string;
  content: string;
  timestamp: string;
}

export interface SearchResultItemDTO {
  chunk_id: string;
  document_id: string;
  content: string;
  index: number;
  score: number;
}

export interface SearchResponseDTO {
  query: string;
  results: SearchResultItemDTO[];
  total_results: number;
}

export interface IndexResponseDTO {
  document_id: string;
  filename: string;
  chunk_count: number;
  checksum: string;
  skipped?: boolean;
}

export interface DeleteResponseDTO {
  status: string;
  document_id: string;
}

export interface ErrorDTO {
  detail: string | unknown;
  request_id: string;
  timestamp?: number;
}

// ──────────────────────────────────────────────────
// Frontend Models — what components consume
// ──────────────────────────────────────────────────

export interface HealthStatus {
  status: string;
  version: string;
  uptime: number;
  timestamp: number;
}

export interface OllamaStatus {
  available: boolean;
  model: string;
  host: string;
}

export interface SystemStatus {
  health: HealthStatus;
  ollama: OllamaStatus;
  document_count: number;
  vector_count: number;
  embedding_model: string | null;
  llm_model: string | null;
  environment: string;
  memory_type: string | null;
  vector_store_type: string | null;
}

export interface Document {
  id: string;
  filename: string;
  checksum: string;
  file_type: string;
  loaded_at: string;
  source_path?: string;
  title?: string;
  mime_type?: string;
  encoding?: string;
  content?: string;
  created_at?: string | null;
  modified_at?: string | null;
  chunk_count?: number;
}

export interface Chunk {
  id: string;
  document_id: string;
  content: string;
  index: number;
  score?: number;
  metadata?: Record<string, unknown>;
}

export interface RetrievalResult {
  query_id: string;
  chunks: Chunk[];
  scores: number[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResult {
  query_id: string;
  conversation_id: string;
  answer: string;
  sources: Chunk[];
  model: string;
  prompt_tokens: number;
}

export interface Conversation {
  id: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at?: string;
  title?: string;
  message_count?: number;
}

export interface SearchResponse {
  query: string;
  results: RetrievalResult;
}

export interface IndexingResult {
  document_id: string;
  filename: string;
  chunk_count: number;
  checksum: string;
  skipped: boolean;
}

export interface Settings {
  theme: "dark" | "light";
  backend_url: string;
  temperature: number;
  top_k: number;
  score_threshold: number;
  preferred_model: string;
}
