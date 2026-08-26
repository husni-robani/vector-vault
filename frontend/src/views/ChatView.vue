<template>
  <div class="chat-view">
    <!-- Sidebar Backdrop (mobile overlay) -->
    <Transition name="backdrop">
      <div
        v-if="sidebarState?.isSidebarOpen.value"
        class="sidebar-backdrop"
        aria-hidden="true"
        @click="sidebarState?.closeSidebar()"
      ></div>
    </Transition>

    <!-- Sidebar -->
    <aside
      ref="sidebarRef"
      class="sidebar"
      :class="{ 'sidebar--open': sidebarState?.isSidebarOpen.value }"
      :tabindex="sidebarState?.isSidebarOpen.value ? -1 : undefined"
      @keydown.tab="onSidebarTab"
    >
      <!-- Upload Button -->
      <DocumentUpload
        :disabled="isUploading"
        :error="uploadError"
        @upload="onUpload"
      />

      <!-- Section Label -->
      <span class="sidebar__section-label">Documents</span>

      <!-- Document List -->
      <DocumentList
        :documents="documents"
        :is-loading="docsLoading"
        :error="docsError"
        :has-more="hasMore"
        :deleting-ids="deletingIds"
        @delete="onDelete"
        @retry="loadDocuments()"
        @load-more="loadNextPage()"
      />
    </aside>

    <!-- Chat Panel -->
    <main id="chat-panel" class="chat-panel">
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

      <!-- Reconnecting Banner -->
      <Transition name="reconnecting">
        <div v-if="isReconnecting" class="reconnecting-banner" role="status">
          <span class="reconnecting-banner__dots">
            <span class="reconnecting-banner__dot" />
            <span class="reconnecting-banner__dot" />
            <span class="reconnecting-banner__dot" />
          </span>
          Reconnecting...
        </div>
      </Transition>

      <!-- Input Bar -->
      <ChatInput
        :disabled="isStreaming || isReconnecting"
        placeholder="Ask anything about your documents..."
        @submit="onSubmit"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, inject } from 'vue';
import ChatMessage from '@/components/ChatMessage.vue';
import ChatInput from '@/components/ChatInput.vue';
import DocumentUpload from '@/components/DocumentUpload.vue';
import DocumentList from '@/components/DocumentList.vue';
import { useChat } from '@/composables/useChat';
import { useDocuments } from '@/composables/useDocuments';
import type { Ref } from 'vue';

// ── Chat State ──
const { messages, isStreaming, isReconnecting, error, sendMessage, retryLastMessage, newChat, dismissError } = useChat();

// ── Documents State ──
const {
  documents,
  isLoading: docsLoading,
  isUploading,
  error: docsError,
  uploadError,
  deletingIds,
  hasMore,
  loadDocuments,
  loadNextPage,
  uploadDocument,
  deleteDocument,
} = useDocuments();

// ── Sidebar State (injected from App.vue) ──
const sidebarRef = ref<HTMLElement | null>(null);

const sidebarState = inject<{
  isSidebarOpen: Ref<boolean>;
  toggleSidebar: () => void;
  closeSidebar: () => void;
}>('sidebarState');

// ── Sidebar Focus Trap ──
// Watch for sidebar opening → auto-focus the sidebar
watch(
  () => sidebarState?.isSidebarOpen.value,
  (isOpen) => {
    if (isOpen) {
      nextTick(() => {
        sidebarRef.value?.focus();
      });
    }
  }
);

/**
 * Focus trap: when the sidebar is open, Tab and Shift+Tab cycle
 * through focusable elements within the sidebar only.
 */
function onSidebarTab(e: KeyboardEvent): void {
  if (!sidebarState?.isSidebarOpen.value) return;
  const sidebarEl = sidebarRef.value;
  if (!sidebarEl) return;

  const focusableSelector = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled])',
    'textarea:not([disabled])',
    'select:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
  ].join(',');

  const focusables = sidebarEl.querySelectorAll<HTMLElement>(focusableSelector);
  if (focusables.length === 0) return;

  const firstFocusable = focusables[0];
  const lastFocusable = focusables[focusables.length - 1];

  if (e.shiftKey) {
    // Shift+Tab: if at first element, wrap to last
    if (document.activeElement === firstFocusable) {
      e.preventDefault();
      lastFocusable.focus();
    }
  } else {
    // Tab: if at last element, wrap to first
    if (document.activeElement === lastFocusable) {
      e.preventDefault();
      firstFocusable.focus();
    }
  }
}

// ── Load documents on mount ──
onMounted(() => {
  loadDocuments();
});

// ── Document Event Handlers ──
async function onUpload({ file, title }: { file: File; title: string }): Promise<void> {
  await uploadDocument(file, title);
}

async function onDelete(id: string): Promise<void> {
  await deleteDocument(id);
}

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
  outline: none;
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

/* ── Sidebar Backdrop (mobile) ── */
.sidebar-backdrop {
  display: none;
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

/* ── Reconnecting Banner ── */
.reconnecting-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  margin: 0 var(--spacing-2xl);
  background: var(--color-accent-soft);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  color: var(--color-accent);
  line-height: var(--line-height-body);
  transition:
    background var(--transition-slow),
    color var(--transition-slow);
}

.reconnecting-banner__dots {
  display: flex;
  align-items: center;
  gap: 4px;
}

.reconnecting-banner__dot {
  display: inline-block;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--color-accent);
  opacity: 0.3;
  animation: typing-dot 1.2s ease-in-out infinite;
  transition: background var(--transition-slow);
}

.reconnecting-banner__dot:nth-child(2) {
  animation-delay: 0.2s;
}

.reconnecting-banner__dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing-dot {
  0%, 60%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  30% {
    opacity: 1;
    transform: scale(1.2);
  }
}

/* Reconnecting banner transition */
.reconnecting-enter-active,
.reconnecting-leave-active {
  transition:
    opacity var(--transition-normal),
    max-height var(--transition-normal);
}

.reconnecting-enter-from,
.reconnecting-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
  overflow: hidden;
}

.reconnecting-enter-to,
.reconnecting-leave-from {
  opacity: 1;
  max-height: 50px;
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

/* ── Responsive: Tablet ── */
@media (max-width: 900px) {
  .sidebar {
    width: 240px;
    min-width: 240px;
  }
}

/* ── Responsive: Mobile ── */
@media (max-width: 500px) {
  /* Sidebar becomes an overlay drawer */
  .sidebar {
    position: fixed;
    top: var(--header-height);
    left: 0;
    bottom: 0;
    z-index: 100;
    transform: translateX(-100%);
    transition: transform var(--transition-normal);
    box-shadow: var(--shadow-card-hover);
    width: 280px;
    min-width: 280px;
  }

  .sidebar--open {
    transform: translateX(0);
  }

  /* Backdrop visible on mobile */
  .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    top: var(--header-height);
    background: rgba(0, 0, 0, 0.35);
    z-index: 99;
  }

  /* Backdrop transition */
  .backdrop-enter-active,
  .backdrop-leave-active {
    transition: opacity var(--transition-normal);
  }

  .backdrop-enter-from,
  .backdrop-leave-to {
    opacity: 0;
  }

  .chat-messages {
    padding: var(--spacing-lg) var(--spacing-md);
  }

  .chat-error-banner {
    margin: var(--spacing-sm) var(--spacing-md) 0;
  }

  .reconnecting-banner {
    margin: 0 var(--spacing-md);
  }
}
</style>
