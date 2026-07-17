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

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.length === 0) continue;

        try {
          const event: SSEEvent = JSON.parse(trimmed);
          yield event;
        } catch {
          // Skip malformed lines
        }
      }
    }

    // Flush remaining buffer
    if (buffer.trim().length > 0) {
      try {
        const event: SSEEvent = JSON.parse(buffer.trim());
        yield event;
      } catch {
        // Skip malformed final line
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
