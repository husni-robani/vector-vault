// Vector Vault — Health Polling Composable
// Polls GET /api/health every 30 seconds. Exposes system status with expandable detail.

import { ref, computed, readonly, onScopeDispose, type Ref, type ComputedRef } from 'vue';
import { checkHealth } from '@/api/client';
import type { HealthResponse, OllamaHealthResponse, ChromadbHealthResponse } from '@/types';

export function useHealth(pollIntervalMs: number = 30000) {
  // ── State ──
  const status: Ref<'healthy' | 'unhealthy' | 'loading'> = ref('loading');
  const ollama: Ref<OllamaHealthResponse | null> = ref(null);
  const chromadb: Ref<ChromadbHealthResponse | null> = ref(null);
  const embeddingModel: Ref<string | null> = ref(null);
  const lastChecked: Ref<Date | null> = ref(null);
  const error: Ref<string | null> = ref(null);
  const isDetailOpen: Ref<boolean> = ref(false);

  // ── Polling internals ──
  let intervalId: ReturnType<typeof setInterval> | null = null;

  // ── Computed ──
  const isHealthy: ComputedRef<boolean> = computed(() => status.value === 'healthy');

  /**
   * Perform an immediate health check.
   * Updates all state fields from the API response.
   */
  async function checkNow(): Promise<void> {
    try {
      const response: HealthResponse = await checkHealth();

      status.value = response.status === 'healthy' ? 'healthy' : 'unhealthy';
      ollama.value = response.ollama;
      chromadb.value = response.chromadb;
      embeddingModel.value = response.embedding_model;
      lastChecked.value = new Date();
      error.value = null;
    } catch (err: unknown) {
      status.value = 'unhealthy';
      error.value = err instanceof Error ? err.message : 'Health check failed.';
      lastChecked.value = new Date();
    }
  }

  /** Toggle the detail panel open/closed. */
  function toggleDetail(): void {
    isDetailOpen.value = !isDetailOpen.value;
  }

  /** Start the health polling interval. Safe to call multiple times (idempotent). */
  function startPolling(): void {
    if (intervalId !== null) return;
    intervalId = setInterval(checkNow, pollIntervalMs);
  }

  /** Stop the health polling interval. Safe to call multiple times (idempotent). */
  function stopPolling(): void {
    if (intervalId === null) return;
    clearInterval(intervalId);
    intervalId = null;
  }

  // ── Lifecycle ──
  // Check immediately, then start polling
  checkNow();
  startPolling();

  // Clean up on component/scope disposal
  onScopeDispose(() => {
    stopPolling();
  });

  // ── Return ──
  return {
    // State (readonly)
    status: readonly(status),
    ollama: readonly(ollama),
    chromadb: readonly(chromadb),
    embeddingModel: readonly(embeddingModel),
    lastChecked: readonly(lastChecked),
    error: readonly(error),
    // Computed
    isHealthy,
    // Detail panel state
    isDetailOpen,
    // Actions
    checkNow,
    toggleDetail,
    startPolling,
    stopPolling,
  };
}
