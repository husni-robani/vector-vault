<template>
  <!-- Skip link: invisible until focused, first focusable element for keyboard users -->
  <a href="#chat-panel" class="skip-link">Skip to chat</a>

  <div class="app">
    <header class="header" ref="headerRef">
      <div class="header__brand">
        <div class="header__icon">
          <svg width="28" height="28" viewBox="0 0 32 32" fill="none" aria-hidden="true">
            <rect x="5" y="7" width="8" height="18" rx="4" fill="currentColor" />
            <rect x="19" y="7" width="8" height="18" rx="4" fill="currentColor" />
            <circle cx="16" cy="16" r="2.5" fill="currentColor" style="color: var(--color-accent)" />
          </svg>
        </div>
        <span class="header__name">Vector Vault</span>
      </div>

      <div class="header__actions">
        <!-- Hamburger (sidebar toggle) — visible only on mobile ≤500px -->
        <button
          class="sidebar-toggle"
          :aria-label="isSidebarOpen ? 'Close sidebar' : 'Open sidebar'"
          :aria-expanded="isSidebarOpen"
          @click="toggleSidebar"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <path d="M2 3.5h12M2 8h12M2 12.5h12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
          </svg>
        </button>

        <!-- Theme Toggle -->
        <button
          class="theme-toggle"
          :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          @click="toggleTheme"
        >
          <!-- Sun icon (visible in light mode) -->
          <svg
            v-show="!isDark"
            class="theme-toggle__icon"
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            aria-hidden="true"
          >
            <circle cx="8" cy="8" r="3.5" stroke="currentColor" stroke-width="1.4"/>
            <path d="M8 1V2.5M8 13.5V15M15 8H13.5M2.5 8H1M12.95 3.05L11.89 4.11M4.11 11.89L3.05 12.95M12.95 12.95L11.89 11.89M4.11 4.11L3.05 3.05" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
          <!-- Moon icon (visible in dark mode) -->
          <svg
            v-show="isDark"
            class="theme-toggle__icon"
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            aria-hidden="true"
          >
            <path d="M13.5 10.268A5.5 5.5 0 0 1 5.732 2.5 6 6 0 1 0 13.5 10.268Z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- Health Indicator (reactive) -->
        <div
          ref="healthRef"
          class="header__health"
          role="button"
          tabindex="0"
          :aria-label="`System status: ${status}`"
          :aria-expanded="isDetailOpen"
          @click="toggleDetail"
          @keydown.enter.prevent="toggleDetail"
          @keydown.space.prevent="toggleDetail"
        >
          <span class="header__health-dot" :class="healthDotClass"></span>
          <span class="header__health-label">{{ healthLabel }}</span>

          <!-- Health Detail Panel (absolutely positioned) -->
          <div v-if="isDetailOpen" class="health-detail" @click.stop @keydown.escape.stop="toggleDetail">
            <div class="health-detail__header">
              <span class="health-detail__title">System Status</span>
              <button
                class="health-detail__close"
                aria-label="Close system status"
                @click="toggleDetail"
              >&#x2715;</button>
            </div>

            <div class="health-detail__body">
              <!-- Ollama Row -->
              <div class="health-detail__row">
                <span class="health-detail__row-dot" :class="ollama?.connected ? 'health-detail__row-dot--success' : 'health-detail__row-dot--error'"></span>
                <span class="health-detail__row-service">Ollama</span>
                <span class="health-detail__row-status">{{ ollama?.connected ? 'Connected' : 'Disconnected' }}</span>
                <span v-if="ollama?.model" class="health-detail__row-model">{{ ollama.model }}</span>
                <span v-if="ollama?.connected" class="health-detail__row-loaded">{{ ollama?.model_loaded ? 'loaded' : 'not loaded' }}</span>
                <span v-if="ollama?.error" class="health-detail__row-error">{{ ollama.error }}</span>
              </div>

              <!-- ChromaDB Row -->
              <div class="health-detail__row">
                <span class="health-detail__row-dot" :class="chromadb?.connected ? 'health-detail__row-dot--success' : 'health-detail__row-dot--error'"></span>
                <span class="health-detail__row-service">ChromaDB</span>
                <span class="health-detail__row-status">{{ chromadb?.connected ? 'Connected' : 'Disconnected' }}</span>
                <span v-if="chromadb?.connected" class="health-detail__row-count">{{ chromadb?.collections_count ?? 0 }} collection{{ (chromadb?.collections_count ?? 0) === 1 ? '' : 's' }}</span>
                <span v-if="chromadb?.error" class="health-detail__row-error">{{ chromadb.error }}</span>
              </div>

              <!-- Embedding Row -->
              <div class="health-detail__row">
                <span class="health-detail__row-dot" :class="embeddingModel ? 'health-detail__row-dot--success' : 'health-detail__row-dot--error'"></span>
                <span class="health-detail__row-service">Embedding</span>
                <span class="health-detail__row-status">{{ embeddingModel ? 'Ready' : 'Unknown' }}</span>
                <span v-if="embeddingModel" class="health-detail__row-model">{{ embeddingModel }}</span>
                <span v-if="healthError" class="health-detail__row-error">{{ healthError }}</span>
              </div>
            </div>

            <div class="health-detail__footer">
              <span>Last checked: {{ lastCheckedText }}</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Offline Banner -->
    <Transition name="offline-banner">
      <div v-if="!isOnline" class="offline-banner" role="alert">
        <span class="offline-banner__icon">&#x26A0;</span>
        <span class="offline-banner__text">You are offline. Changes will sync when connection is restored.</span>
      </div>
    </Transition>

    <!-- Main Content -->
    <div class="main">
      <!-- Global Error Fallback -->
      <div v-if="globalError" class="global-error">
        <div class="global-error__card">
          <h2 class="global-error__heading">Something went wrong</h2>
          <p class="global-error__message">{{ globalError }}</p>
          <button class="global-error__reload" @click="reloadApp">Reload App</button>
        </div>
      </div>

      <!-- Normal route view -->
      <RouterView v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, provide, readonly, onErrorCaptured } from 'vue';
import { useHealth } from '@/composables/useHealth';
import { useOnline } from '@/composables/useOnline';

const THEME_KEY = 'vector-vault-theme';
const isDark = ref(false);

// ── Theme ──
function applyTheme(dark: boolean): void {
  isDark.value = dark;
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
}

function toggleTheme(): void {
  const next = !isDark.value;
  applyTheme(next);
  localStorage.setItem(THEME_KEY, next ? 'dark' : 'light');
}

onMounted(() => {
  const stored = localStorage.getItem(THEME_KEY);
  applyTheme(stored === 'dark');
});

// ── Health ──
const {
  status,
  ollama,
  chromadb,
  embeddingModel,
  lastChecked,
  error: healthError,
  isHealthy,
  isDetailOpen,
  toggleDetail,
} = useHealth();

const healthLabel = computed(() => {
  if (isHealthy.value) return 'System Healthy';
  if (status.value === 'loading') return 'Checking...';
  return 'Service Issue';
});

const healthDotClass = computed(() => ({
  'header__health-dot--healthy': isHealthy.value && status.value !== 'loading',
  'header__health-dot--unhealthy': !isHealthy.value && status.value !== 'loading',
  'header__health-dot--loading': status.value === 'loading',
}));

const lastCheckedText = computed(() => {
  const lc = lastChecked.value;
  if (!lc) return 'Never';
  const seconds = Math.floor((Date.now() - lc.getTime()) / 1000);
  if (seconds < 5) return 'just now';
  if (seconds < 60) return `${seconds} second${seconds === 1 ? '' : 's'} ago`;
  const minutes = Math.floor(seconds / 60);
  return `${minutes} minute${minutes === 1 ? '' : 's'} ago`;
});

// ── Offline Detection ──
const { isOnline } = useOnline();

// ── Sidebar Toggle (mobile) ──
const isSidebarOpen = ref(false);

function toggleSidebar(): void {
  isSidebarOpen.value = !isSidebarOpen.value;
}

function closeSidebar(): void {
  isSidebarOpen.value = false;
}

// Provide sidebar state to child components (ChatView)
provide('sidebarState', {
  isSidebarOpen: readonly(isSidebarOpen),
  toggleSidebar,
  closeSidebar,
});

// ── Global Error Boundary ──
const globalError = ref<string | null>(null);

onErrorCaptured((err: Error) => {
  console.error('Global error:', err);
  globalError.value = err.message || 'An unexpected error occurred.';
  return false; // prevent propagation
});

function reloadApp(): void {
  window.location.reload();
}

// ── Escape Key Handler ──
// Priority: health detail panel → sidebar → (future overlays)
function onKeyDown(e: KeyboardEvent): void {
  if (e.key !== 'Escape') return;

  if (isDetailOpen.value) {
    toggleDetail();
    return;
  }

  if (isSidebarOpen.value) {
    closeSidebar();
    return;
  }
}

// ── Click Outside to Close Health Detail ──
const healthRef = ref<HTMLElement | null>(null);
const headerRef = ref<HTMLElement | null>(null);

function onDocumentClick(e: MouseEvent): void {
  if (!isDetailOpen.value) return;
  const healthEl = healthRef.value;
  if (!healthEl) return;
  // If the click target is not inside the health indicator (and its detail panel), close it
  if (!healthEl.contains(e.target as Node)) {
    isDetailOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeyDown);
  document.addEventListener('click', onDocumentClick, true); // capture phase
});

onUnmounted(() => {
  document.removeEventListener('keydown', onKeyDown);
  document.removeEventListener('click', onDocumentClick, true);
});
</script>

<style scoped>
/* ── App Shell ── */
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
}

/* ── Skip Link ── */
.skip-link {
  position: absolute;
  top: -100%;
  left: 0;
  z-index: 1001;
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-accent);
  color: #ffffff;
  font-family: var(--font-body);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-emphasis);
  text-decoration: none;
  border-radius: 0 0 var(--radius-sm) 0;
  transition: top var(--transition-fast);
}

.skip-link:focus {
  top: 0;
}

/* ── Header Bar ── */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height);
  min-height: var(--header-height);
  padding: 0 var(--spacing-2xl);
  background: var(--color-bg-header);
  border-bottom: 1px solid var(--color-border-subtle);
  position: relative;
  z-index: 150;
}

/* ── Brand ── */
.header__brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.header__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  color: var(--color-text-primary);
}

.header__name {
  font-family: var(--font-display);
  font-size: var(--font-size-app-name);
  font-weight: var(--font-weight-strong);
  color: var(--color-text-primary);
  line-height: 1;
}

/* ── Actions ── */
.header__actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

/* ── Sidebar Toggle (Hamburger) ── */
.sidebar-toggle {
  display: none; /* hidden on desktop */
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-subtle);
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  transition:
    background var(--transition-fast),
    color var(--transition-fast),
    border-color var(--transition-fast);
}

.sidebar-toggle:hover {
  background: var(--color-surface-hover);
  color: var(--color-accent);
  border-color: var(--color-accent-border);
}

.sidebar-toggle svg {
  pointer-events: none;
}

@media (max-width: 500px) {
  .sidebar-toggle {
    display: flex;
  }
}

/* Theme Toggle */
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-subtle);
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  transition:
    background var(--transition-fast),
    color var(--transition-fast),
    border-color var(--transition-fast);
}

.theme-toggle:hover {
  background: var(--color-surface-hover);
  color: var(--color-accent);
  border-color: var(--color-accent-border);
}

/* Health Indicator */
.header__health {
  display: flex;
  align-items: center;
  gap: 7px;
  cursor: pointer;
  position: relative;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
  user-select: none;
}

.header__health:hover {
  background: var(--color-surface-hover);
}

.header__health-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-text-subtle);
  transition:
    background var(--transition-normal),
    box-shadow var(--transition-normal);
}

.header__health-dot--healthy {
  background: var(--color-success);
  box-shadow: 0 0 5px var(--color-health-glow);
}

.header__health-dot--unhealthy {
  background: var(--color-error);
}

.header__health-dot--loading {
  background: var(--color-text-subtle);
  box-shadow: none;
}

.header__health-label {
  font-family: var(--font-display);
  font-size: var(--font-size-small);
  font-weight: var(--font-weight-body);
  font-style: italic;
  color: var(--color-text-muted);
  transition: color var(--transition-slow);
}

/* ── Health Detail Panel ── */
.health-detail {
  position: absolute;
  top: calc(100% + var(--spacing-sm));
  right: 0;
  width: 340px;
  background: var(--color-surface-card);
  border: 1px solid var(--color-border-prominent);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-card-hover);
  z-index: 200;
  overflow: hidden;
  transition:
    background-color var(--transition-slow),
    border-color var(--transition-slow),
    color var(--transition-slow);
}

.health-detail__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-subtle);
}

.health-detail__title {
  font-family: var(--font-display);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-strong);
  font-style: italic;
  color: var(--color-text-primary);
}

.health-detail__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: var(--font-size-small);
  transition:
    background var(--transition-fast),
    color var(--transition-fast);
}

.health-detail__close:hover {
  background: var(--color-surface-hover);
  color: var(--color-text-body);
}

.health-detail__body {
  padding: var(--spacing-md) var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.health-detail__row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  line-height: var(--line-height-body);
}

.health-detail__row-dot {
  width: 6px;
  height: 6px;
  min-width: 6px;
  border-radius: 50%;
  background: var(--color-text-subtle);
  transition: background var(--transition-normal);
}

.health-detail__row-dot--success {
  background: var(--color-success);
}

.health-detail__row-dot--error {
  background: var(--color-error);
}

.health-detail__row-service {
  font-weight: var(--font-weight-emphasis);
  color: var(--color-text-primary);
  min-width: 72px;
}

.health-detail__row-status {
  color: var(--color-text-body);
}

.health-detail__row-model {
  color: var(--color-text-muted);
}

.health-detail__row-loaded {
  color: var(--color-text-subtle);
  font-style: italic;
}

.health-detail__row-count {
  color: var(--color-text-muted);
}

.health-detail__row-error {
  width: 100%;
  padding-top: var(--spacing-xs);
  color: var(--color-error);
  font-size: var(--font-size-caption);
  font-style: italic;
}

.health-detail__footer {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-top: 1px solid var(--color-border-subtle);
  font-family: var(--font-body);
  font-size: var(--font-size-caption);
  color: var(--color-text-subtle);
  font-style: italic;
}

/* ── Offline Banner ── */
.offline-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-accent-soft);
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  color: var(--color-accent);
  line-height: var(--line-height-body);
  z-index: 50;
  transition:
    background var(--transition-slow),
    color var(--transition-slow);
}

.offline-banner__icon {
  flex-shrink: 0;
}

.offline-banner__text {
  text-align: center;
}

/* Offline banner transition */
.offline-banner-enter-active,
.offline-banner-leave-active {
  transition:
    opacity var(--transition-normal),
    max-height var(--transition-normal);
}

.offline-banner-enter-from,
.offline-banner-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
  overflow: hidden;
}

.offline-banner-enter-to,
.offline-banner-leave-from {
  opacity: 1;
  max-height: 50px;
}

/* ── Global Error Fallback ── */
.global-error {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: var(--spacing-3xl);
}

.global-error__card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-lg);
  max-width: 400px;
  padding: var(--spacing-3xl);
  background: var(--color-surface-card);
  border: 1px solid var(--color-border-prominent);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-card);
  text-align: center;
  transition:
    background-color var(--transition-slow),
    border-color var(--transition-slow);
}

.global-error__heading {
  font-family: var(--font-display);
  font-size: var(--font-size-app-name);
  font-weight: var(--font-weight-strong);
  color: var(--color-error);
  line-height: 1.2;
  transition: color var(--transition-slow);
}

.global-error__message {
  font-family: var(--font-body);
  font-size: var(--font-size-body);
  color: var(--color-text-body);
  line-height: var(--line-height-body);
  transition: color var(--transition-slow);
}

.global-error__reload {
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  font-weight: var(--font-weight-emphasis);
  padding: var(--spacing-sm) var(--spacing-xl);
  border: 1px solid var(--color-border-prominent);
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--color-accent);
  cursor: pointer;
  transition:
    background var(--transition-fast),
    border-color var(--transition-fast),
    color var(--transition-fast);
}

.global-error__reload:hover {
  background: var(--color-accent-soft);
  border-color: var(--color-accent-border);
}

/* ── Main Content Area ── */
.main {
  display: flex;
  flex: 1;
  overflow: hidden;
  position: relative;
}
</style>
