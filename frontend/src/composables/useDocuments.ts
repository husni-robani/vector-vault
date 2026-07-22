// Vector Vault — useDocuments composable
// Full document lifecycle state management: list, upload, delete, pagination.

import { ref, computed, readonly } from 'vue';
import type { DocumentInfo, DocumentUploadResponse, DocumentType } from '@/types';
import {
  fetchDocuments,
  uploadDocument as uploadDocumentApi,
  deleteDocument as deleteDocumentApi,
} from '@/api/client';

export function useDocuments() {
  // ── State ──
  const documents = ref<DocumentInfo[]>([]);
  const isLoading = ref(false);
  const isUploading = ref(false);
  const error = ref<string | null>(null);
  const uploadError = ref<string | null>(null);
  const currentPage = ref(0); // 0 = not yet loaded
  const totalDocuments = ref(0);
  const deletingIds = ref<Set<string>>(new Set());

  // ── Computed ──
  const hasMore = computed(() => documents.value.length < totalDocuments.value);
  const isEmpty = computed(() => !isLoading.value && documents.value.length === 0);

  // ── Actions ──

  /**
   * Fetch documents from the backend.
   * @param page — if omitted, loads page 1 (fresh, replaces list).
   *              if provided, loads that page; results are appended when page > 1.
   */
  async function loadDocuments(page?: number): Promise<void> {
    const targetPage = page ?? 1;
    const isAppend = page !== undefined && page !== 1;

    isLoading.value = true;
    error.value = null;

    try {
      const response = await fetchDocuments(targetPage, 20);
      const data = response.data!;

      if (isAppend) {
        documents.value = [...documents.value, ...data.documents];
      } else {
        documents.value = data.documents;
      }

      currentPage.value = data.page;
      totalDocuments.value = data.total;
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : 'Failed to load documents';
      error.value = message;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Append the next page of documents to the existing list.
   */
  async function loadNextPage(): Promise<void> {
    if (!hasMore.value) return;
    await loadDocuments(currentPage.value + 1);
  }

  /**
   * Upload a document file.
   * Pushes a "pending" placeholder card IMMEDIATELY so the user sees
   * the "Processing..." indicator during the API call (which may take
   * seconds for embedding / vector storage).
   *
   * On success: replaces the placeholder with real document data.
   * On failure: removes the placeholder (uploadError is shown separately).
   */
  async function uploadDocument(file: File, title?: string): Promise<void> {
    isUploading.value = true;
    uploadError.value = null;

    const docTitle = title ?? file.name.replace(/\.[^.]+$/, '');
    const tempId = `uploading-${Date.now()}`;
    const ext = file.name.split('.').pop()?.toLowerCase();
    const fileType: DocumentType = ext === 'pdf' ? '.pdf' : '.md';

    // 1. Push placeholder immediately — user sees "Processing..." instantly
    const placeholder: DocumentInfo = {
      id: tempId,
      title: docTitle,
      filename: file.name,
      file_type: fileType,
      chunks_count: 0,
      created_at: new Date().toISOString(),
      status: 'pending' as const,
      size_bytes: file.size,
    };

    documents.value = [placeholder, ...documents.value];
    totalDocuments.value++;

    try {
      // 2. Make the (potentially slow) API call
      const response = await uploadDocumentApi(file, docTitle);
      const uploaded: DocumentUploadResponse = response.data!;

      // 3. Replace placeholder with real document from server
      // NOTE: uploaded.file_type may be a MIME type ("application/pdf")
      // while the list endpoint returns extension strings (".pdf").
      // Use our client-side fileType (from filename) for consistency.
      const realDoc: DocumentInfo = {
        id: uploaded.document_id,
        title: uploaded.title ?? docTitle,
        filename: uploaded.filename,
        file_type: fileType,
        chunks_count: 0,
        created_at: new Date().toISOString(),
        status: uploaded.status,
        size_bytes: file.size,
      };

      documents.value = documents.value.map((d) =>
        d.id === tempId ? realDoc : d
      );
    } catch (e: unknown) {
      // 4. On failure: remove placeholder (uploadError shown in DocumentUpload)
      documents.value = documents.value.filter((d) => d.id !== tempId);
      totalDocuments.value = Math.max(0, totalDocuments.value - 1);

      const message = e instanceof Error ? e.message : 'Upload failed';
      uploadError.value = message;
    } finally {
      isUploading.value = false;
    }
  }

  /**
   * Delete a document.
   * Tracks the ID in deletingIds for fade-out UI.
   * On success: removes from list; decrements totalDocuments.
   * On failure: sets error.
   * Always removes from deletingIds in finally.
   */
  async function deleteDocument(id: string): Promise<void> {
    // Add to deleting set (reactive: create a new Set)
    deletingIds.value = new Set([...deletingIds.value, id]);

    try {
      await deleteDocumentApi(id);
      documents.value = documents.value.filter((d) => d.id !== id);
      totalDocuments.value = Math.max(0, totalDocuments.value - 1);
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : 'Delete failed';
      error.value = message;
    } finally {
      // Remove from deleting set
      const updated = new Set(deletingIds.value);
      updated.delete(id);
      deletingIds.value = updated;
    }
  }

  /**
   * Clear the general error state. Preserves uploadError.
   */
  function dismissError(): void {
    error.value = null;
  }

  // ── Return (readonly state, writable actions) ──
  return {
    documents: readonly(documents),
    isLoading: readonly(isLoading),
    isUploading: readonly(isUploading),
    error: readonly(error),
    uploadError: readonly(uploadError),
    deletingIds: readonly(deletingIds),
    hasMore,
    isEmpty,
    loadDocuments,
    loadNextPage,
    uploadDocument,
    deleteDocument,
    dismissError,
  };
}
