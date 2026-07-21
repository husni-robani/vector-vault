// Vector Vault — Conversation ID Persistence
// Manages conversation_id with localStorage backing.

import { ref, readonly, type Ref } from 'vue';

const STORAGE_KEY = 'vector-vault-conversation-id';

/** Generate a UUID with fallback for environments without crypto.randomUUID. */
function generateId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  // Fallback: timestamp + random
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 11)}`;
}

export function useConversationId() {
  const stored = localStorage.getItem(STORAGE_KEY);
  const conversationId: Ref<string> = ref(stored ?? generateId());

  // Persist on creation if it wasn't already stored
  if (!stored) {
    localStorage.setItem(STORAGE_KEY, conversationId.value);
  }

  /** Generate a new conversation ID, persist it, and return it. */
  function newConversation(): void {
    const id = generateId();
    conversationId.value = id;
    localStorage.setItem(STORAGE_KEY, id);
  }

  /** Update the conversation ID (e.g. from a done SSE event). */
  function setConversationId(id: string): void {
    conversationId.value = id;
    localStorage.setItem(STORAGE_KEY, id);
  }

  return {
    conversationId: readonly(conversationId),
    newConversation,
    setConversationId,
  };
}
