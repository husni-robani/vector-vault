<template>
  <div class="chat-view">
    <!-- Sidebar -->
    <aside class="sidebar">
      <!-- Upload Button -->
      <button class="sidebar__upload-btn" aria-label="Upload a document">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <path d="M8 3V13M3 8H13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
        </svg>
        Upload Document
      </button>

      <!-- Section Label -->
      <span class="sidebar__section-label">Documents</span>

      <!-- Document List -->
      <div class="sidebar__documents">
        <article class="doc-card">
          <span class="doc-card__badge doc-card__badge--md">.md</span>
          <div class="doc-card__info">
            <span class="doc-card__name">quarterly-notes.md</span>
            <span class="doc-card__meta">2 days ago</span>
          </div>
          <button class="doc-card__delete" aria-label="Delete document">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
              <path d="M2 3.5H12M5 3.5V2.5C5 1.94772 5.44772 1.5 6 1.5H8C8.55228 1.5 9 1.94772 9 2.5V3.5M5.5 6V10.5M8.5 6V10.5M3.5 3.5L4 11.5C4 12.0523 4.44772 12.5 5 12.5H9C9.55228 12.5 10 12.0523 10 11.5L10.5 3.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </article>

        <article class="doc-card">
          <span class="doc-card__badge doc-card__badge--pdf">.pdf</span>
          <div class="doc-card__info">
            <span class="doc-card__name">research-paper.pdf</span>
            <span class="doc-card__meta">Today</span>
          </div>
          <button class="doc-card__delete" aria-label="Delete document">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
              <path d="M2 3.5H12M5 3.5V2.5C5 1.94772 5.44772 1.5 6 1.5H8C8.55228 1.5 9 1.94772 9 2.5V3.5M5.5 6V10.5M8.5 6V10.5M3.5 3.5L4 11.5C4 12.0523 4.44772 12.5 5 12.5H9C9.55228 12.5 10 12.0523 10 11.5L10.5 3.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </article>

        <article class="doc-card">
          <span class="doc-card__badge doc-card__badge--md">.md</span>
          <div class="doc-card__info">
            <span class="doc-card__name">meeting-minutes.md</span>
            <span class="doc-card__meta">5 days ago</span>
          </div>
          <button class="doc-card__delete" aria-label="Delete document">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
              <path d="M2 3.5H12M5 3.5V2.5C5 1.94772 5.44772 1.5 6 1.5H8C8.55228 1.5 9 1.94772 9 2.5V3.5M5.5 6V10.5M8.5 6V10.5M3.5 3.5L4 11.5C4 12.0523 4.44772 12.5 5 12.5H9C9.55228 12.5 10 12.0523 10 11.5L10.5 3.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </article>
      </div>

      <!-- Empty state (shown when no documents) -->
      <div class="sidebar-empty">
        <p class="sidebar-empty__text">No documents yet. Upload your first document to get started.</p>
      </div>
    </aside>

    <!-- Chat Panel -->
    <main class="chat-panel">
      <!-- Error Banner -->
      <div v-if="error" class="chat-error-banner" role="alert">
        <span class="chat-error-banner__icon">&#x26A0;</span>
        <span class="chat-error-banner__text">{{ error }}</span>
        <button @click="retryLastMessage()" class="chat-error-banner__retry">Retry</button>
        <button @click="dismissError()" class="chat-error-banner__dismiss" aria-label="Dismiss">&#x2715;</button>
      </div>

      <!-- Empty State -->
      <div v-if="isEmpty" class="chat-empty">
        <div class="chat-empty__icon">
          <svg width="56" height="56" viewBox="0 0 32 32" fill="none" aria-hidden="true">
            <rect x="5" y="7" width="8" height="18" rx="4" fill="currentColor" />
            <rect x="19" y="7" width="8" height="18" rx="4" fill="currentColor" />
            <circle cx="16" cy="16" r="2.5" fill="currentColor" />
          </svg>
        </div>
        <h2 class="chat-empty__heading">Your Personal Library</h2>
        <p class="chat-empty__subtitle">Upload documents and ask questions to explore your knowledge.</p>
      </div>

      <!-- Messages -->
      <div
        v-else
        ref="messagesRef"
        class="chat-messages"
        @scroll="onMessagesScroll"
      >
        <button class="chat-new-chat-btn" @click="newChat">New Conversation</button>
        <ChatMessage
          v-for="msg in messages"
          :key="msg.id"
          :role="msg.role"
          :content="msg.content"
          :is-streaming="msg.isStreaming"
          :sources="msg.sources"
          :has-error="!!msg.error"
          :error-message="msg.error || ''"
        />
      </div>

      <!-- Input Bar -->
      <ChatInput
        :disabled="isStreaming"
        placeholder="Ask anything about your documents..."
        @submit="onSubmit"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import ChatMessage from '@/components/ChatMessage.vue';
import ChatInput from '@/components/ChatInput.vue';
import { useChat } from '@/composables/useChat';

const { messages, isStreaming, error, sendMessage, retryLastMessage, newChat, dismissError } = useChat();

// ── Scroll Management ──
const messagesRef = ref<HTMLElement | null>(null);
const userScrolledUp = ref(false);

function scrollToBottom(smooth: boolean = false): void {
  const el = messagesRef.value;
  if (!el) return;

  // Respect manual scroll-up: don't force-scroll if user is reading history
  if (userScrolledUp.value && !smooth) return;

  el.scrollTo({
    top: el.scrollHeight,
    behavior: smooth ? 'smooth' : 'instant',
  });
}

function onMessagesScroll(): void {
  const el = messagesRef.value;
  if (!el) return;
  // User has scrolled up more than 100px from the bottom — they're reading history
  userScrolledUp.value = el.scrollHeight - el.scrollTop - el.clientHeight > 100;
}

// Auto-scroll: new message added
watch(() => messages.value.length, () => {
  nextTick(() => scrollToBottom(true));
});

// Auto-scroll: content grows during streaming (each new token)
watch(
  () => {
    const last = messages.value[messages.value.length - 1];
    return last ? last.content : '';
  },
  () => {
    if (isStreaming.value) {
      nextTick(() => scrollToBottom());
    }
  }
);

// ── Derived State ──
const isEmpty = computed(() => messages.value.length === 0);

// ── Event Handlers ──
function onSubmit(text: string): void {
  sendMessage(text);
}
</script>

<style scoped>
/* ── Main Layout ── */
.chat-view {
  display: flex;
  flex-direction: row;
  flex: 1;
  overflow: hidden;
}

/* ── Sidebar ── */
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background: var(--color-bg-sidebar);
  border-right: 1px solid var(--color-border-subtle);
  display: flex;
  flex-direction: column;
  padding: var(--spacing-xl) var(--spacing-lg);
  gap: var(--spacing-lg);
  overflow-y: auto;
}

/* Upload Button */
.sidebar__upload-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
  width: 100%;
  padding: 10px var(--spacing-lg);
  background: var(--color-accent);
  color: #ffffff;
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-emphasis);
  cursor: pointer;
  transition:
    background var(--transition-normal),
    box-shadow var(--transition-normal);
}

.sidebar__upload-btn:hover {
  background: var(--color-accent-hover);
  box-shadow: 0 2px 8px var(--color-accent-glow);
}

.sidebar__upload-btn svg {
  display: block;
  flex-shrink: 0;
}

/* Section Label */
.sidebar__section-label {
  font-family: var(--font-display);
  font-size: var(--font-size-small);
  font-weight: var(--font-weight-emphasis);
  font-style: italic;
  color: var(--color-text-muted);
  letter-spacing: 0.3px;
  padding: var(--spacing-xs) var(--spacing-xs) 0;
}

/* Document List */
.sidebar__documents {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

/* Document Card */
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

/* Badge */
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

/* Document Info */
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
}

/* Delete Button */
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

/* ── Empty State ── */
.sidebar-empty {
  display: none;
  flex: 1;
  align-items: center;
  justify-content: center;
}

.sidebar-empty__text {
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  color: var(--color-text-muted);
  text-align: center;
  line-height: var(--line-height-body);
}

/* ── Chat Panel ── */
.chat-panel {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--color-bg-canvas);
}

/* ── Empty State ── */
.chat-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px var(--spacing-2xl);
  text-align: center;
  gap: 14px;
  user-select: none;
}

.chat-empty__icon {
  color: var(--color-accent);
  opacity: 0.18;
  margin-bottom: var(--spacing-xs);
}

.chat-empty__heading {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: var(--font-weight-strong);
  color: var(--color-text-primary);
  letter-spacing: var(--letter-spacing-tight);
  line-height: 1.2;
}

.chat-empty__subtitle {
  font-family: var(--font-body);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-body);
  color: var(--color-text-muted);
  max-width: 340px;
  line-height: 1.65;
}

/* ── Messages Area ── */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-3xl) var(--spacing-2xl);
  display: flex;
  flex-direction: column;
  gap: 22px;
}

/* ── New Chat Button ── */
.chat-new-chat-btn {
  font-family: var(--font-display);
  font-size: var(--font-size-caption);
  font-style: italic;
  color: var(--color-text-subtle);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: var(--spacing-xs) var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
  align-self: flex-start;
  transition: color var(--transition-fast);
}

.chat-new-chat-btn:hover {
  color: var(--color-accent);
}

/* ── Error Banner ── */
.chat-error-banner {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  margin: var(--spacing-md) var(--spacing-2xl) 0;
  background: var(--color-error-soft);
  border-left: 3px solid var(--color-error);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-family: var(--font-body);
  font-size: var(--font-size-small);
}

.chat-error-banner__icon {
  flex-shrink: 0;
  font-size: var(--font-size-body);
  color: var(--color-error);
}

.chat-error-banner__text {
  flex: 1;
  color: var(--color-text-body);
  line-height: var(--line-height-body);
}

.chat-error-banner__retry {
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
  transition:
    background var(--transition-fast),
    color var(--transition-fast);
}

.chat-error-banner__retry:hover {
  background: var(--color-error);
  color: #ffffff;
}

.chat-error-banner__dismiss {
  font-family: var(--font-body);
  font-size: var(--font-size-body);
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0 var(--spacing-xs);
  line-height: 1;
  transition: color var(--transition-fast);
}

.chat-error-banner__dismiss:hover {
  color: var(--color-text-body);
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .sidebar {
    width: 240px;
    min-width: 240px;
  }
}

@media (max-width: 500px) {
  .sidebar {
    display: none;
  }

  .chat-messages {
    padding: var(--spacing-lg) var(--spacing-md);
  }

  .chat-error-banner {
    margin: var(--spacing-sm) var(--spacing-md) 0;
  }
}
</style>
