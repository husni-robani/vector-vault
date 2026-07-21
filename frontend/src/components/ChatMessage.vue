<template>
  <div class="message" :class="`message--${role}`">
    <!-- Assistant Message: marginalia-style with avatar -->
    <template v-if="role === 'assistant'">
      <div class="message__row">
        <div class="message__avatar">V</div>
        <div class="message__body">
          <div class="message__bubble">
            <!-- Waiting indicator: animated dots before first token -->
            <span v-if="isWaiting" class="message__typing" aria-label="Assistant is typing">
              <span class="message__typing-dot" />
              <span class="message__typing-dot" />
              <span class="message__typing-dot" />
            </span>
            <template v-else>
              <p class="message__text">{{ content }}</p>
              <span v-if="isStreaming" class="message__streaming-indicator">|</span>
            </template>
          </div>

          <!-- Sources -->
          <div v-if="sources && sources.length > 0" class="message__sources">
            <span
              v-for="(source, i) in sources"
              :key="i"
              class="source-chip"
            >
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
                <path d="M2 1.5H7.5L10 4V10.5C10 10.7761 9.77614 11 9.5 11H2.5C2.22386 11 2 10.7761 2 10.5V2C2 1.72386 2.22386 1.5 2.5 1.5Z" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7.5 1.5V4H10" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              Source: {{ source.title ?? 'Untitled' }} · chunk {{ (source.chunk_index ?? 0) + 1 }}
            </span>
          </div>

          <!-- Error state -->
          <div v-if="hasError" class="message__error" role="alert">{{ errorMessage }}</div>

          <!-- Timestamp -->
          <span class="message__time">Just now</span>
        </div>
      </div>
    </template>

    <!-- User Message: right-aligned, no avatar -->
    <template v-else>
      <div class="message__bubble">
        <p class="message__text">{{ content }}</p>
      </div>
      <span class="message__time">Just now</span>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { SourceInfo } from '@/types';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
  sources?: readonly SourceInfo[];
  hasError?: boolean;
  errorMessage?: string;
}

const props = withDefaults(defineProps<ChatMessageProps>(), {
  isStreaming: false,
  hasError: false,
  errorMessage: '',
});

const isWaiting = computed(() => props.isStreaming && !props.content);
</script>

<style scoped>
/* ── Message Container ── */
.message {
  display: flex;
  flex-direction: column;
  max-width: 72%;
}

.message--assistant {
  align-self: flex-start;
}

.message--user {
  align-self: flex-end;
  align-items: flex-end;
}

/* ── Assistant Row (avatar + body) ── */
.message__row {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
}

/* ── Avatar ── */
.message__avatar {
  width: 28px;
  height: 28px;
  min-width: 28px;
  border-radius: var(--radius-md);
  background: var(--color-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: var(--font-weight-strong);
  line-height: 1;
  transition: background var(--transition-slow);
}

/* ── Body ── */
.message__body {
  flex: 1;
  min-width: 0;
}

/* ── Message Bubble ── */
.message--assistant .message__bubble {
  padding: var(--spacing-xs) 0 var(--spacing-xs) var(--spacing-lg);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-body);
  line-height: var(--line-height-chat);
  color: var(--color-text-body);
  background: none;
  border-left: 3px solid var(--color-msg-accent-bar);
  transition:
    color var(--transition-slow),
    border-color var(--transition-slow);
}

.message--user .message__bubble {
  padding: var(--spacing-sm) 15px;
  border-radius: var(--radius-lg) var(--radius-lg) 2px var(--radius-lg);
  background: var(--color-user-bubble-bg);
  border: 1px solid var(--color-user-bubble-bd);
  color: var(--color-user-bubble-text);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-body);
  line-height: var(--line-height-chat);
  transition:
    background var(--transition-slow),
    border-color var(--transition-slow),
    color var(--transition-slow);
}

.message__text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

/* ── Streaming Cursor ── */
.message__streaming-indicator {
  display: inline-block;
  animation: blink 1s step-end infinite;
  color: var(--color-accent);
  font-weight: var(--font-weight-body);
  margin-left: 1px;
  transition: color var(--transition-slow);
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* ── Typing Indicator Dots ── */
.message__typing {
  display: flex;
  align-items: center;
  gap: 4px;
  height: calc(var(--font-size-body) * var(--line-height-chat));
}

.message__typing-dot {
  display: inline-block;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--color-accent);
  opacity: 0.3;
  animation: typing-dot 1.2s ease-in-out infinite;
  transition: background var(--transition-slow);
}

.message__typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.message__typing-dot:nth-child(3) {
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

/* ── Source Chips ── */
.message__sources {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: var(--spacing-sm);
  margin-left: 2px;
}

.source-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 3px 9px;
  background: var(--color-accent-chip-bg);
  border: 1px solid var(--color-accent-chip-bd);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-body);
  color: var(--color-text-muted);
  white-space: nowrap;
  transition:
    background var(--transition-slow),
    border-color var(--transition-slow),
    color var(--transition-slow);
}

.source-chip svg {
  color: var(--color-accent);
  flex-shrink: 0;
  transition: color var(--transition-slow);
}

/* ── Timestamps ── */
.message__time {
  font-family: var(--font-display);
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-body);
  font-style: italic;
  color: var(--color-text-subtle);
  margin-top: 5px;
  padding: 0 var(--spacing-xs);
  transition: color var(--transition-slow);
}

.message--user .message__time {
  text-align: right;
}

/* ── Error State ── */
.message__error {
  color: var(--color-error);
  font-size: var(--font-size-caption);
  margin-top: var(--spacing-sm);
  padding-left: 18px;
  font-style: italic;
  transition: color var(--transition-slow);
}

/* ── Responsive ── */
@media (max-width: 500px) {
  .message {
    max-width: 90%;
  }
}
</style>
