// Vector Vault — Frontend Types
// Mirrors backend schemas 1:1. Source of truth: ../backend/app/interfaces/schemas/

// ── Chat (from chat.py) ──

export interface ChatRequest {
  message: string;
  conversation_id: string; // Required (not optional)
}

export interface DeliveryEventData {
  type: "token";
  content: string;
}

export interface SourceInfo {
  title: string | null;
  chunk_index: number | null;
  distance: number | null;
  snippet: string | null;
}

export interface SourcesEventData {
  type: "sources";
  sources: SourceInfo[];
}

export interface DoneEventData {
  type: "done";
  conversation_id: string | null;
}

export interface ErrorEventData {
  type: "error";
  message: string;
}

export type SSEEvent =
  | DeliveryEventData
  | SourcesEventData
  | DoneEventData
  | ErrorEventData;

// ── Documents (from documents.py + domain/documents.py) ──

export type DocumentType = ".md" | ".pdf";
export type DocumentStatus = "pending" | "processed" | "error";

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  file_type: DocumentType;
  title: string | null;
  status: DocumentStatus;
}

export interface DocumentInfo {
  id: string;
  title: string;
  filename: string;
  file_type: DocumentType;
  chunks_count: number;
  created_at: string;
  status: DocumentStatus;
  size_bytes: number;
}

export interface DocumentListResponse {
  documents: DocumentInfo[];
  total: number;
  page: number;
  limit: number;
}

// ── Health (from health.py) ──

export interface OllamaHealthResponse {
  connected: boolean;
  model: string;
  model_loaded: boolean;
  error: string | null;
}

export interface ChromadbHealthResponse {
  connected: boolean;
  collections_count: number;
  error: string | null;
}

export interface HealthResponse {
  status: string;
  ollama: OllamaHealthResponse;
  chromadb: ChromadbHealthResponse;
  embedding_model: string;
}

// ── Response Wrappers (from response.py) ──

export interface PaginationMetadata {
  current_page: number;
  per_page: number;
  total_items: number;
  total_pages: number;
}

export interface SuccessResponse<T> {
  message: string;
  data: T | null;
  pagination: PaginationMetadata | null;
}

export interface ErrorResponse {
  message: string;
  errors: unknown | null;
}
