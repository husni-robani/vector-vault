<template>
  <div class="chat-input">
    <div class="chat-input__wrapper">
      <textarea
        ref="textareaRef"
        class="chat-input__field"
        :disabled="disabled"
        :placeholder="placeholder ?? 'Type your message...'"
        rows="1"
        aria-label="Message input"
        @keydown.enter.prevent="handleSubmit"
      ></textarea>
      <button
        class="chat-input__send"
        :disabled="disabled"
        aria-label="Send message"
        @click="handleSubmit"
      >
        <svg
          class="chat-input__send-icon"
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <path
            d="M1 8L15 1L8 15L6 9L1 8Z"
            fill="currentColor"
          />
          <path
            d="M6 9L8 15L15 1L6 9Z"
            fill="currentColor"
            fill-opacity="0.6"
          />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

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
</script>

<style scoped>
/* ── Chat Input Container ── */
.chat-input {
  width: 100%;
  max-width: 720px;
}

.chat-input__wrapper {
  display: flex;
  align-items: flex-end;
  gap: var(--spacing-sm);
  background: var(--color-bg-secondary);
  border: var(--border-width-normal) solid var(--border-color-light);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm);
  transition: border-color var(--transition-fast);
}

.chat-input__wrapper:focus-within {
  border-color: var(--color-accent);
}

/* ── Textarea ── */
.chat-input__field {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  color: var(--color-text-primary);
  font-family: var(--font-body);
  font-size: var(--font-size-base);
  line-height: var(--line-height-relaxed);
  padding: var(--spacing-xs) var(--spacing-sm);
  resize: none;
  min-height: calc(var(--font-size-base) * var(--line-height-relaxed) + var(--spacing-xs) * 2);
  max-height: 150px;
}

.chat-input__field::placeholder {
  color: var(--color-text-tertiary);
}

.chat-input__field:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Send Button ── */
.chat-input__send {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--color-accent);
  color: var(--color-dark-text);
  cursor: pointer;
  flex-shrink: 0;
  transition: background var(--transition-fast), transform var(--transition-fast);
}

.chat-input__send:hover:not(:disabled) {
  background: var(--color-accent-bright);
  transform: scale(1.05);
}

.chat-input__send:active:not(:disabled) {
  transform: scale(0.95);
}

.chat-input__send:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.chat-input__send-icon {
  display: block;
}

/* ── Responsive ── */
@media (max-width: 500px) {
  .chat-input__wrapper {
    padding: var(--spacing-xs);
  }

  .chat-input__field {
    font-size: var(--font-size-base);
  }
}
</style>
