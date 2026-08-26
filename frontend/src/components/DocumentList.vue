<template>
  <div class="document-list">
    <!-- ── A) Loading State ── -->
    <template v-if="isLoading && documents.length === 0">
      <article
        v-for="i in 3"
        :key="'skeleton-' + i"
        class="doc-card doc-card--skeleton"
        aria-hidden="true"
      >
        <span class="doc-card__badge-skeleton"></span>
        <div class="doc-card__info">
          <span class="doc-card__name-skeleton"></span>
          <span class="doc-card__meta-skeleton"></span>
        </div>
      </article>
    </template>

    <!-- ── B) Empty State ── -->
    <template v-else-if="!isLoading && documents.length === 0 && !error">
      <div class="sidebar-empty">
        <p class="sidebar-empty__text">
          No documents yet. Upload your first document above to get started.
        </p>
      </div>
    </template>

    <!-- ── C) Error State ── -->
    <template v-else-if="error && documents.length === 0">
      <div class="doc-list-error" role="alert">
        <svg
          class="doc-list-error__icon"
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          aria-hidden="true"
        >
          <circle
            cx="10"
            cy="10"
            r="8"
            stroke="currentColor"
            stroke-width="1.5"
          />
          <path
            d="M10 6V11"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
          />
          <circle cx="10" cy="14" r="0.8" fill="currentColor" />
        </svg>
        <span class="doc-list-error__text">{{ error }}</span>
        <button class="doc-list-error__retry" @click="$emit('retry')">
          Retry
        </button>
      </div>
    </template>

    <!-- ── D) Populated State (also shown after error when docs exist) ── -->
    <div v-if="documents.length > 0" class="sidebar__documents">
      <article
        v-for="doc in documents"
        :key="doc.id"
        class="doc-card"
        :class="{
          'doc-card--deleting': deletingIds.has(doc.id),
          'doc-card--confirming': confirmingId === doc.id,
          'doc-card--pending': doc.status === 'pending' && confirmingId !== doc.id && !deletingIds.has(doc.id),
          'doc-card--error': doc.status === 'error' && confirmingId !== doc.id && !deletingIds.has(doc.id),
        }"
      >
        <!-- Normal Card View -->
        <template v-if="confirmingId !== doc.id">
          <span
            class="doc-card__badge"
            :class="
              doc.file_type === '.md'
                ? 'doc-card__badge--md'
                : 'doc-card__badge--pdf'
            "
          >
            {{ doc.file_type }}
          </span>
          <div class="doc-card__info">
            <span class="doc-card__name">{{ doc.filename }}</span>
            <!-- Status-dependent meta line -->
            <span v-if="doc.status === 'pending'" class="doc-card__meta doc-card__meta--processing">
              <span class="doc-card__processing-spinner" aria-hidden="true"></span>
              Processing&hellip;
            </span>
            <span v-else-if="doc.status === 'error'" class="doc-card__meta doc-card__meta--error">
              Processing failed
            </span>
            <span v-else class="doc-card__meta">
              {{ formatRelativeTime(doc.created_at) }} &middot;
              {{ doc.chunks_count }}
              {{ doc.chunks_count === 1 ? 'chunk' : 'chunks' }} &middot;
              {{ formatBytes(doc.size_bytes) }}
            </span>
          </div>
          <!-- Delete button or spinner -->
          <button
            v-if="!deletingIds.has(doc.id)"
            class="doc-card__delete"
            aria-label="Delete document"
            @click="confirmingId = doc.id"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 14 14"
              fill="none"
              aria-hidden="true"
            >
              <path
                d="M2 3.5H12M5 3.5V2.5C5 1.94772 5.44772 1.5 6 1.5H8C8.55228 1.5 9 1.94772 9 2.5V3.5M5.5 6V10.5M8.5 6V10.5M3.5 3.5L4 11.5C4 12.0523 4.44772 12.5 5 12.5H9C9.55228 12.5 10 12.0523 10 11.5L10.5 3.5"
                stroke="currentColor"
                stroke-width="1.2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
          <span v-else class="doc-card__spinner" aria-label="Deleting...">
            <svg
              width="14"
              height="14"
              viewBox="0 0 14 14"
              fill="none"
              aria-hidden="true"
            >
              <circle
                cx="7"
                cy="7"
                r="6"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-dasharray="28"
                stroke-dashoffset="8"
                stroke-linecap="round"
              />
            </svg>
          </span>
        </template>

        <!-- Inline Confirmation View -->
        <template v-else>
          <div class="doc-card__confirm">
            <span class="doc-card__confirm-text">
              Delete &ldquo;{{ doc.filename }}&rdquo;?
            </span>
            <div class="doc-card__confirm-actions">
              <button
                class="doc-card__confirm-cancel"
                @click="confirmingId = null"
              >
                Cancel
              </button>
              <button
                class="doc-card__confirm-delete"
                @click="onConfirmDelete(doc.id)"
              >
                Delete
              </button>
            </div>
          </div>
        </template>
      </article>

      <!-- ── Load More ── -->
      <button
        v-if="hasMore"
        class="doc-list__load-more"
        :disabled="isLoading"
        @click="$emit('load-more')"
      >
        <template v-if="isLoading">Loading&hellip;</template>
        <template v-else>Load more documents</template>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { DocumentInfo } from '@/types';

// ── Props ──
interface Props {
  documents: readonly DocumentInfo[];
  isLoading: boolean;
  error: string | null;
  hasMore: boolean;
  deletingIds: ReadonlySet<string>;
}

defineProps<Props>();

// ── Emits ──
interface Emits {
  delete: [id: string];
  retry: [];
  'load-more': [];
}

const emit = defineEmits<Emits>();

// ── Local State ──
const confirmingId = ref<string | null>(null);

// ── Confirmation Handler ──
function onConfirmDelete(id: string): void {
  confirmingId.value = null;
  emit('delete', id);
}

// ── Utility: Human-readable file sizes ──
function formatBytes(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1048576) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  if (bytes < 1073741824) {
    return `${(bytes / 1048576).toFixed(1)} MB`;
  }
  return `${(bytes / 1073741824).toFixed(1)} GB`;
}

// ── Utility: Relative time display ──
function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSeconds < 60) return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes} min ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`;
  if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7);
    return `${weeks} week${weeks === 1 ? '' : 's'} ago`;
  }

  // Fallback: formatted date
  const months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
  ];
  return `${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
}
</script>

<style scoped>
/* ── Container ── */
.document-list {
  display: flex;
  flex-direction: column;
}

/* ── Document List Container ── */
.sidebar__documents {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

/* ── Document Card ── */
.doc-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px var(--spacing-md);
  background: var(--color-surface-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  transition:
    opacity var(--transition-fast),
    transform var(--transition-fast),
    box-shadow var(--transition-fast),
    background var(--transition-fast);
}

.doc-card:hover {
  background: var(--color-surface-hover);
  box-shadow: var(--shadow-card-hover);
  transform: translateY(-1px);
}

.doc-card:hover .doc-card__delete {
  opacity: 1;
}

/* ── Deleting State ── */
.doc-card--deleting {
  opacity: 0.5;
  pointer-events: none;
}

/* ── Confirming State ── */
.doc-card--confirming {
  background: var(--color-surface-hover);
  border-color: var(--color-accent-border);
}

/* ── Pending / Processing State ── */
.doc-card--pending {
  background: var(--color-accent-soft);
  border-color: var(--color-accent-border);
}

.doc-card--pending:hover {
  background: var(--color-accent-chip-bg);
}

.doc-card--pending .doc-card__delete {
  opacity: 1;
}

/* ── Error State ── */
.doc-card--error {
  background: var(--color-error-soft);
  border-color: var(--color-error);
}

.doc-card--error:hover {
  background: var(--color-error-soft);
}

.doc-card--error .doc-card__delete {
  opacity: 1;
}

/* ── Processing Spinner ── */
.doc-card__processing-spinner {
  display: inline-block;
  width: 10px;
  height: 10px;
  border: 1.5px solid var(--color-accent);
  border-top-color: transparent;
  border-radius: 50%;
  animation: doc-spinner-rotate 0.8s linear infinite;
  flex-shrink: 0;
}

@keyframes doc-spinner-rotate {
  to { transform: rotate(360deg); }
}

/* ── Processing Meta Text ── */
.doc-card__meta--processing {
  color: var(--color-accent);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

/* ── Error Meta Text ── */
.doc-card__meta--error {
  color: var(--color-error);
}

/* ── Badge ── */
.doc-card__badge {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  width: 28px;
  height: 18px;
  border-radius: 2px;
  font-family: var(--font-mono);
  font-size: var(--font-size-badge);
  font-weight: var(--font-weight-strong);
  letter-spacing: 0.3px;
  text-transform: uppercase;
  color: var(--color-text-muted);
  background: var(--color-badge-bg);
  border: 1px solid var(--color-badge-bd);
  flex-shrink: 0;
}

.doc-card__badge--md {
  color: var(--color-badge-md-text);
  background: var(--color-badge-md-bg);
  border-color: var(--color-badge-md-bd);
}

.doc-card__badge--pdf {
  color: var(--color-badge-pdf-text);
  background: var(--color-badge-pdf-bg);
  border-color: var(--color-badge-pdf-bd);
}

/* ── Document Info ── */
.doc-card__info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.doc-card__name {
  font-family: var(--font-body);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-emphasis);
  color: var(--color-text-body);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.doc-card__meta {
  font-family: var(--font-display);
  font-size: var(--font-size-meta);
  font-weight: var(--font-weight-body);
  font-style: italic;
  color: var(--color-text-subtle);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── Delete Button ── */
.doc-card__delete {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: var(--radius-md);
  background: transparent;
  border: none;
  color: var(--color-text-subtle);
  cursor: pointer;
  flex-shrink: 0;
  opacity: 0;
  transition:
    color var(--transition-fast),
    background var(--transition-fast),
    opacity var(--transition-fast);
}

.doc-card__delete:hover {
  color: var(--color-error);
  background: var(--color-error-soft);
}

.doc-card__delete svg {
  display: block;
}

/* ── Spinner (during deletion) ── */
.doc-card__spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  flex-shrink: 0;
  color: var(--color-text-subtle);
  animation: spin 1s linear infinite;
}

.doc-card__spinner svg {
  display: block;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* ── Inline Confirmation ── */
.doc-card__confirm {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
}

.doc-card__confirm-text {
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  color: var(--color-text-body);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
}

.doc-card__confirm-actions {
  display: flex;
  gap: var(--spacing-xs);
  flex-shrink: 0;
}

.doc-card__confirm-cancel,
.doc-card__confirm-delete {
  font-family: var(--font-body);
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-emphasis);
  border-radius: var(--radius-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
  cursor: pointer;
  border: none;
  transition:
    background var(--transition-fast),
    color var(--transition-fast);
  white-space: nowrap;
}

.doc-card__confirm-cancel {
  background: transparent;
  color: var(--color-text-muted);
  border: 1px solid var(--color-border-prominent);
}

.doc-card__confirm-cancel:hover {
  background: var(--color-surface-hover);
  color: var(--color-text-body);
}

.doc-card__confirm-delete {
  background: var(--color-error);
  color: #ffffff;
}

.doc-card__confirm-delete:hover {
  background: #8e3e3e;
}

/* ── Skeleton (Loading) ── */
.doc-card--skeleton {
  pointer-events: none;
}

.doc-card__badge-skeleton {
  min-width: 28px;
  width: 28px;
  height: 18px;
  border-radius: 2px;
  background: var(--color-border-subtle);
  flex-shrink: 0;
  animation: shimmer 1.5s ease-in-out infinite;
}

.doc-card__name-skeleton {
  width: 70%;
  height: 12px;
  border-radius: var(--radius-sm);
  background: var(--color-border-subtle);
  animation: shimmer 1.5s ease-in-out infinite;
}

.doc-card__meta-skeleton {
  width: 50%;
  height: 10px;
  margin-top: 3px;
  border-radius: var(--radius-sm);
  background: var(--color-border-subtle);
  animation: shimmer 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  0% {
    background-color: var(--color-border-subtle);
  }
  50% {
    background-color: var(--color-surface-hover);
  }
  100% {
    background-color: var(--color-border-subtle);
  }
}

/* ── Empty State ── */
.sidebar-empty {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  min-height: 120px;
}

.sidebar-empty__text {
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  color: var(--color-text-muted);
  text-align: center;
  line-height: var(--line-height-body);
  max-width: 220px;
}

/* ── Error State ── */
.doc-list-error {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: var(--color-error-soft);
  border-left: 3px solid var(--color-error);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-family: var(--font-body);
  font-size: var(--font-size-small);
}

.doc-list-error__icon {
  flex-shrink: 0;
  color: var(--color-error);
  margin-top: 1px;
}

.doc-list-error__text {
  flex: 1;
  color: var(--color-text-body);
  line-height: var(--line-height-body);
  word-break: break-word;
}

.doc-list-error__retry {
  font-family: var(--font-body);
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-emphasis);
  color: var(--color-error);
  background: transparent;
  border: 1px solid var(--color-error);
  border-radius: var(--radius-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  transition:
    background var(--transition-fast),
    color var(--transition-fast);
}

.doc-list-error__retry:hover {
  background: var(--color-error);
  color: #ffffff;
}

/* ── Load More ── */
.doc-list__load-more {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  margin-top: var(--spacing-xs);
  background: transparent;
  border: 1px dashed var(--color-border-prominent);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-emphasis);
  color: var(--color-text-muted);
  cursor: pointer;
  transition:
    background var(--transition-fast),
    color var(--transition-fast),
    border-color var(--transition-fast);
}

.doc-list__load-more:hover {
  background: var(--color-surface-hover);
  color: var(--color-accent);
  border-color: var(--color-accent-border);
}

.doc-list__load-more:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
