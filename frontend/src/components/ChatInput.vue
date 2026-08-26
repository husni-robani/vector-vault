<template>
  <div class="chat-input-bar" :class="{ 'chat-input-bar--disabled': disabled }">
    <div class="chat-input-bar__wrapper">
      <textarea
        ref="textareaRef"
        class="chat-input-bar__textarea"
        :disabled="disabled"
        :placeholder="placeholder ?? 'Ask anything about your documents...'"
        rows="1"
        aria-label="Message input"
        @keydown.enter.prevent="handleSubmit"
      ></textarea>
      <button
        class="chat-input-bar__send"
        :disabled="disabled"
        aria-label="Send message"
        @click="handleSubmit"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <path d="M8 2V14M3 7L8 2L13 7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

interface ChatInputProps {
  disabled?: boolean;
  placeholder?: string;
}

interface ChatInputEmits {
  (e: 'submit', value: string): void;
}

withDefaults(defineProps<ChatInputProps>(), {
  disabled: false,
});

const emit = defineEmits<ChatInputEmits>();
const textareaRef = ref<HTMLTextAreaElement | null>(null);

function handleSubmit(): void {
  const textarea = textareaRef.value;
  if (!textarea) return;

  const value = textarea.value.trim();
  if (value.length === 0) return;

  emit('submit', value);
  textarea.value = '';
}

// ── Keyboard Shortcut: / key to focus input ──
function onKeyDown(e: KeyboardEvent): void {
  // Don't capture if user is typing in another input or textarea
  if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
  // Don't capture if modifier keys are pressed
  if (e.ctrlKey || e.metaKey || e.altKey) return;

  if (e.key === '/') {
    e.preventDefault();
    textareaRef.value?.focus();
  }
}

onMounted(() => document.addEventListener('keydown', onKeyDown));
onUnmounted(() => document.removeEventListener('keydown', onKeyDown));
</script>

<style scoped>
/* ── Input Bar Container ── */
.chat-input-bar {
  display: flex;
  padding: var(--spacing-lg) var(--spacing-2xl);
  background: var(--color-bg-input-bar);
  border-top: 1px solid var(--color-border-subtle);
  transition:
    background var(--transition-slow),
    border-color var(--transition-slow);
}

.chat-input-bar__wrapper {
  position: relative;
  flex: 1;
  display: flex;
  align-items: flex-end;
}

/* ── Textarea ── */
.chat-input-bar__textarea {
  width: 100%;
  min-height: 44px;
  max-height: 120px;
  padding: var(--spacing-sm) 48px var(--spacing-sm) var(--spacing-lg);
  background: var(--color-surface-input);
  border: 1px solid var(--color-border-prominent);
  border-radius: var(--radius-lg);
  font-family: var(--font-body);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-body);
  color: var(--color-text-body);
  line-height: var(--line-height-body);
  resize: none;
  outline: none;
  transition:
    background-color var(--transition-normal),
    border-color var(--transition-normal),
    color var(--transition-normal),
    box-shadow var(--transition-normal);
}

.chat-input-bar__textarea::placeholder {
  color: var(--color-text-subtle);
  font-family: var(--font-display);
  font-style: italic;
  font-size: var(--font-size-small);
}

.chat-input-bar__textarea:focus {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-input-focus);
}

.chat-input-bar--disabled .chat-input-bar__textarea {
  opacity: 0.5;
  pointer-events: none;
}

/* ── Send Button (round, inside textarea) ── */
.chat-input-bar__send {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-accent);
  color: #ffffff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition:
    background var(--transition-normal),
    box-shadow var(--transition-normal),
    opacity var(--transition-normal);
}

.chat-input-bar__send:hover:not(:disabled) {
  background: var(--color-accent-hover);
  box-shadow: 0 2px 8px var(--color-accent-glow);
}

.chat-input-bar__send:disabled {
  opacity: 0.35;
  cursor: default;
  box-shadow: none;
}

/* ── Responsive ── */
@media (max-width: 500px) {
  .chat-input-bar {
    padding: var(--spacing-sm) var(--spacing-md);
  }

  /* Touch-friendly send button: 44px minimum tap target */
  .chat-input-bar__send {
    width: 44px;
    height: 44px;
  }

  /* Prevent iOS zoom on focus */
  .chat-input-bar__textarea {
    font-size: 16px;
  }
}
</style>
