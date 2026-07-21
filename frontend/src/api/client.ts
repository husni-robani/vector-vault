// Vector Vault — API Client
// Typed native fetch wrappers. No Axios.

import type {
  ChatRequest,
  SSEEvent,
  DocumentUploadResponse,
  DocumentListResponse,
  HealthResponse,
  SuccessResponse,
} from '@/types';

const API_BASE = 'http://localhost:8000/api';

/**
 * Send a chat message and stream the SSE response.
 * POST /api/chats → SSE stream yielding token, sources, done, error events.
 *
 * Backend uses FastAPI ServerSentEvent producing standard SSE format:
 *   data: {"type":"token","content":"..."}
 *   data: {"type":"sources","sources":[...]}
 *   event: done
 *   data: {"type":"done","conversation_id":"..."}
 *   event: error
 *   data: {"type":"error","message":"..."}
 */
export async function* streamChat(
  request: ChatRequest
): AsyncGenerator<SSEEvent> {
  const response = await fetch(`${API_BASE}/chats`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const body = await response.text().catch(() => '');
    throw new Error(`Chat API error: ${response.status}${body ? ` — ${body}` : ''}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('Chat API error: missing response body');
  }

  const decoder = new TextDecoder();
  let buffer = '';
  let dataChunks: string[] = [];

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      // Keep the last partial line in the buffer
      buffer = lines.pop() ?? '';

      for (const line of lines) {
        const trimmed = line.trim();

        // Empty line = event boundary → flush accumulated data
        if (trimmed.length === 0) {
          if (dataChunks.length > 0) {
            const dataStr = dataChunks.join('\n');
            dataChunks = [];
            try {
              const event: SSEEvent = JSON.parse(dataStr);
              yield event;
            } catch {
              // Skip malformed SSE data payload
            }
          }
          continue;
        }

        // Event type line — store for context but don't expose yet
        if (trimmed.startsWith('event:')) {
          continue;
        }

        // Retry line — store for potential reconnection logic
        if (trimmed.startsWith('retry:')) {
          continue;
        }

        // ID line — standard SSE field
        if (trimmed.startsWith('id:')) {
          continue;
        }

        // Comment line (starts with colon) — skip per SSE spec
        if (trimmed.startsWith(':')) {
          continue;
        }

        // Data line — accumulate (SSE events can span multiple data: lines)
        if (trimmed.startsWith('data:')) {
          const payload = trimmed.slice(5).trimStart();
          dataChunks.push(payload);
          continue;
        }

        // Unknown line — skip gracefully
      }
    }

    // Flush any remaining data after stream ends
    if (dataChunks.length > 0) {
      const dataStr = dataChunks.join('\n');
      try {
        const event: SSEEvent = JSON.parse(dataStr);
        yield event;
      } catch {
        // Skip malformed final event
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Fetch a paginated list of documents.
 * GET /api/documents?page={page}&limit={limit}
 */
export async function fetchDocuments(
  page: number = 1,
  limit: number = 50
): Promise<SuccessResponse<DocumentListResponse>> {
  const params = new URLSearchParams({
    page: String(page),
    limit: String(limit),
  });

  const response = await fetch(`${API_BASE}/documents?${params.toString()}`);

  if (!response.ok) {
    const body = await response.text().catch(() => '');
    throw new Error(`Documents API error: ${response.status}${body ? ` — ${body}` : ''}`);
  }

  return response.json() as Promise<SuccessResponse<DocumentListResponse>>;
}

/**
 * Upload a document.
 * POST /api/documents (multipart/form-data)
 * Field name: "document" (NOT "file")
 */
export async function uploadDocument(
  file: File,
  title?: string
): Promise<SuccessResponse<DocumentUploadResponse>> {
  const formData = new FormData();
  formData.append('document', file);
  if (title) {
    formData.append('title', title);
  }

  const response = await fetch(`${API_BASE}/documents`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const body = await response.text().catch(() => '');
    throw new Error(`Upload API error: ${response.status}${body ? ` — ${body}` : ''}`);
  }

  return response.json() as Promise<SuccessResponse<DocumentUploadResponse>>;
}

/**
 * Delete a document.
 * DELETE /api/documents/{id}
 */
export async function deleteDocument(
  id: string
): Promise<SuccessResponse<null>> {
  const response = await fetch(`${API_BASE}/documents/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const body = await response.text().catch(() => '');
    throw new Error(`Delete API error: ${response.status}${body ? ` — ${body}` : ''}`);
  }

  return response.json() as Promise<SuccessResponse<null>>;
}

/**
 * Check system health.
 * GET /api/health
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/health`);

  if (!response.ok) {
    const body = await response.text().catch(() => '');
    throw new Error(`Health API error: ${response.status}${body ? ` — ${body}` : ''}`);
  }

  return response.json() as Promise<HealthResponse>;
}
