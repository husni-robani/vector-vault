<template>
  <div
    class="document-upload"
    :class="{ 'document-upload--dragging': isDragging }"
    @dragenter.prevent="onDragEnter"
    @dragleave.prevent="onDragLeave"
    @dragover.prevent
    @drop.prevent="onDrop"
  >
    <button
      class="document-upload__btn"
      :class="{ 'document-upload__btn--disabled': disabled }"
      :disabled="disabled"
      aria-label="Upload a document"
      @click="openFileDialog"
    >
      <svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        aria-hidden="true"
      >
        <path
          d="M8 3V13M3 8H13"
          stroke="currentColor"
          stroke-width="1.6"
          stroke-linecap="round"
        />
      </svg>
      Upload Document
    </button>

    <!-- Hidden file input -->
    <input
      ref="fileInputRef"
      type="file"
      accept=".md,.pdf"
      class="document-upload__input"
      :disabled="disabled"
      @change="onFileSelected"
    />

    <!-- Error text -->
    <p
      v-if="validationError || props.error"
      class="document-upload__error"
      role="alert"
    >
      {{ validationError || props.error }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// ── Props ──
interface Props {
  disabled?: boolean;
  error?: string | null;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  error: null,
});

// ── Emits ──
interface Emits {
  upload: [payload: { file: File; title: string }];
}

const emit = defineEmits<Emits>();

// ── Refs ──
const fileInputRef = ref<HTMLInputElement | null>(null);
const validationError = ref<string | null>(null);
const dragCounter = ref(0);

const isDragging = ref(false);

// ── Constants ──
const ALLOWED_TYPES = ['.md', '.pdf'];
const MAX_SIZE_BYTES = 50 * 1024 * 1024; // 50 MB

// ── Methods ──

function openFileDialog(): void {
  if (props.disabled) return;
  fileInputRef.value?.click();
}

function getTitleFromFile(file: File): string {
  return file.name.replace(/\.[^.]+$/, '');
}

function validateFile(file: File): boolean {
  validationError.value = null;

  // Check extension
  const extension = '.' + file.name.split('.').pop()?.toLowerCase();
  if (!ALLOWED_TYPES.includes(extension)) {
    validationError.value = 'Only .md and .pdf files are supported.';
    return false;
  }

  // Check size
  if (file.size > MAX_SIZE_BYTES) {
    validationError.value = 'File exceeds 50MB limit.';
    return false;
  }

  return true;
}

function onFileSelected(event: Event): void {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;

  // Clear any previous validation error when user selects a new file
  validationError.value = null;

  if (!validateFile(file)) {
    resetInput();
    return;
  }

  const title = getTitleFromFile(file);
  emit('upload', { file, title });
  resetInput();
}

function resetInput(): void {
  if (fileInputRef.value) {
    fileInputRef.value.value = '';
  }
}

// ── Drag-and-Drop ──

function onDragEnter(): void {
  if (props.disabled) return;
  dragCounter.value++;
  isDragging.value = dragCounter.value > 0;
}

function onDragLeave(): void {
  if (props.disabled) return;
  dragCounter.value--;
  isDragging.value = dragCounter.value > 0;
}

function onDrop(event: DragEvent): void {
  if (props.disabled) return;
  dragCounter.value = 0;
  isDragging.value = false;

  const file = event.dataTransfer?.files?.[0];
  if (!file) return;

  validationError.value = null;

  if (!validateFile(file)) return;

  const title = getTitleFromFile(file);
  emit('upload', { file, title });
}
</script>

<style scoped>
/* ── Container ── */
.document-upload {
  position: relative;
}

/* ── Upload Button ── */
.document-upload__btn {
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

.document-upload__btn:hover {
  background: var(--color-accent-hover);
  box-shadow: 0 2px 8px var(--color-accent-glow);
}

.document-upload__btn:active {
  background: var(--color-accent);
}

.document-upload__btn svg {
  display: block;
  flex-shrink: 0;
}

/* ── Disabled State ── */
.document-upload__btn--disabled {
  background: var(--color-accent-disabled);
  color: var(--color-accent-disabled-text);
  cursor: not-allowed;
}

.document-upload__btn--disabled:hover {
  background: var(--color-accent-disabled);
  box-shadow: none;
}

/* ── Drag-over Glow ── */
.document-upload--dragging .document-upload__btn {
  box-shadow: 0 0 0 2px var(--color-accent-glow);
}

/* ── Hidden File Input ── */
.document-upload__input {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  overflow: hidden;
  pointer-events: none;
}

/* ── Error Text ── */
.document-upload__error {
  font-family: var(--font-body);
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-body);
  color: var(--color-error);
  margin-top: var(--spacing-xs);
  padding: 0 var(--spacing-xs);
  line-height: var(--line-height-body);
}
</style>
