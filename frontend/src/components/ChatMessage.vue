<template>
  <div class="chat-message" :class="`chat-message--${role}`">
    <!-- Loading State: Skeleton -->
    <div v-if="loading" class="chat-message__skeleton" aria-busy="true" aria-label="Loading message">
      <div class="skeleton-line skeleton-line--short"></div>
      <div class="skeleton-line skeleton-line--long"></div>
      <div class="skeleton-line skeleton-line--medium"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="hasError" class="chat-message__error" role="alert">
      <span class="chat-message__error-icon" aria-hidden="true">&#x26A0;</span>
      <span class="chat-message__error-text">{{ errorMessage }}</span>
    </div>

    <!-- Empty State: Nothing renders -->
    <template v-else-if="!content">
    </template>

    <!-- Populated State -->
    <template v-else>
      <div class="chat-message__bubble">
        <p class="chat-message__text">{{ content }}</p>
        <!-- Streaming cursor -->
        <span v-if="isStreaming" class="chat-message__cursor" aria-label="Streaming response in progress"></span>
      </div>

      <!-- Source Chips (assistant only) -->
      <div v-if="role === 'assistant' && sources && sources.length > 0" class="chat-message__sources">
        <span class="chat-message__sources-label">Sources</span>
        <div class="chat-message__chips">
          <span
            v-for="(source, index) in sources"
            :key="index"
            class="chat-message__chip"
          >
            {{ source.title ?? 'Untitled' }}
          </span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { SourceInfo } from '@/types';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
  sources?: SourceInfo[];
  loading?: boolean;
  hasError?: boolean;
  errorMessage?: string;
}

withDefaults(defineProps<ChatMessageProps>(), {
  isStreaming: false,
  loading: false,
  hasError: false,
  errorMessage: '',
});
</script>

<style scoped>
/* ── Chat Message Container ── */
.chat-message {
  display: flex;
  flex-direction: column;
  max-width: 100%;
}

.chat-message--user {
  align-items: flex-end;
}

.chat-message--assistant {
  align-items: flex-start;
}

/* ── Message Bubble ── */
.chat-message__bubble {
  max-width: 85%;
  padding: var(--spacing-sm) var(--spacing-md);
  font-family: var(--font-body);
  font-size: var(--font-size-base);
  line-height: var(--line-height-relaxed);
  color: var(--color-text-primary);
  position: relative;
}

.chat-message--user .chat-message__bubble {
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
}

.chat-message--assistant .chat-message__bubble {
  background: transparent;
  border-left: var(--border-width-thick) solid var(--color-accent);
  border-radius: 0;
}

.chat-message__text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

/* ── Streaming Cursor ── */
.chat-message__cursor {
  display: inline-block;
  width: var(--spacing-sm);
  height: var(--font-size-base);
  background: var(--color-accent);
  vertical-align: text-bottom;
  animation: blink-cursor 1s step-end infinite;
}

@keyframes blink-cursor {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* ── Source Chips ── */
.chat-message__sources {
  margin-top: var(--spacing-sm);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.chat-message__sources-label {
  font-family: var(--font-body);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  letter-spacing: var(--letter-spacing-wider);
  text-transform: uppercase;
  margin-left: var(--spacing-md);
}

.chat-message__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  margin-left: var(--spacing-md);
}

.chat-message__chip {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-sm);
  background: var(--color-accent-bg);
  color: var(--color-accent);
  font-family: var(--font-body);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-sm);
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ── Skeleton (Loading State) ── */
.chat-message__skeleton {
  padding: var(--spacing-sm) var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  max-width: 60%;
}

.skeleton-line {
  height: var(--font-size-base);
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-sm);
  animation: shimmer 1.5s ease-in-out infinite;
}

.skeleton-line--short {
  width: 40%;
}

.skeleton-line--medium {
  width: 70%;
}

.skeleton-line--long {
  width: 100%;
}

@keyframes shimmer {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

/* ── Error State ── */
.chat-message__error {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(224, 108, 108, 0.08);
  border-left: var(--border-width-thick) solid var(--color-error);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-family: var(--font-body);
  font-size: var(--font-size-base);
  color: var(--color-error);
}

.chat-message__error-icon {
  flex-shrink: 0;
  font-size: var(--font-size-md);
}

.chat-message__error-text {
  color: var(--color-error);
}

/* ── Responsive ── */
@media (max-width: 500px) {
  .chat-message__bubble {
    max-width: 95%;
  }

  .chat-message__chip {
    max-width: 140px;
  }
}
</style>
