<template>
  <div class="app">
    <header class="header">
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
        <div class="header__health">
          <span class="header__health-dot"></span>
          <span class="header__health-label">System Healthy</span>
        </div>
      </div>
    </header>
    <div class="main">
      <RouterView />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const THEME_KEY = 'vector-vault-theme';
const isDark = ref(false);

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
</script>

<style scoped>
/* ── App Shell ── */
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
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
}

.header__health-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-accent);
  box-shadow: 0 0 5px var(--color-accent-glow);
}

.header__health-label {
  font-family: var(--font-display);
  font-size: var(--font-size-small);
  font-weight: var(--font-weight-body);
  font-style: italic;
  color: var(--color-text-muted);
}

/* ── Main Content Area ── */
.main {
  display: flex;
  flex: 1;
  overflow: hidden;
}
</style>
