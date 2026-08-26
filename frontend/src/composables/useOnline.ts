// Vector Vault — Online/Offline Detection Composable
// Monitors navigator.onLine and window online/offline events.

import { ref, readonly, onScopeDispose, type Ref } from 'vue';

export function useOnline() {
  // ── State ──
  const isOnline: Ref<boolean> = ref(navigator.onLine);

  // ── Event Handlers ──
  function handleOnline(): void {
    isOnline.value = true;
  }

  function handleOffline(): void {
    isOnline.value = false;
  }

  // ── Listeners ──
  window.addEventListener('online', handleOnline);
  window.addEventListener('offline', handleOffline);

  // ── Lifecycle ──
  onScopeDispose(() => {
    window.removeEventListener('online', handleOnline);
    window.removeEventListener('offline', handleOffline);
  });

  // ── Return ──
  return {
    isOnline: readonly(isOnline),
  };
}
