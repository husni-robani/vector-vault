// Vector Vault — Chat State & SSE Streaming
// Core composable driving the RAG chat experience.
// Phase 4: SSE reconnection with exponential backoff.

import { ref, computed, readonly, nextTick, type Ref, type ComputedRef } from 'vue';
import { streamChat } from '@/api/client';
import { useConversationId } from './useConversationId';
import type { ChatMessageModel, SourceInfo } from '@/types';

/** Generate a unique ID with fallback for environments without crypto.randomUUID. */
function generateMessageId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 11)}`;
}

/**
 * Exponential backoff for reconnection attempts.
 * Sequence: 1s, 2s, 4s, 8s, 16s, 32s (capped at 30s).
 */
function getBackoff(retryNumber: number): number {
  return Math.min(1000 * Math.pow(2, retryNumber), 30000);
}

function wait(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/** Maximum number of automatic reconnection attempts. */
const MAX_RETRIES = 3;

export function useChat() {
  // ── State ──
  const messages: Ref<ChatMessageModel[]> = ref([]);
  const isStreaming: Ref<boolean> = ref(false);
  const error: Ref<string | null> = ref(null);
  const isReconnecting: Ref<boolean> = ref(false);
  const retryCount: Ref<number> = ref(0);

  const { conversationId, newConversation, setConversationId } = useConversationId();

  // ── Computed ──
  const messageCount: ComputedRef<number> = computed(() => messages.value.length);
  const lastMessage: ComputedRef<ChatMessageModel | null> = computed(() => {
    const msgs = messages.value;
    return msgs.length > 0 ? msgs[msgs.length - 1] : null;
  });

  // ── Actions ──

  /**
   * Send a user message and stream the assistant response via SSE.
   * Handles reconnection with exponential backoff on network failures.
   * Blocks during streaming or reconnection.
   */
  async function sendMessage(text: string): Promise<void> {
    // Guard: don't send while already streaming or reconnecting
    if (isStreaming.value || isReconnecting.value) return;

    // Reset retry state on fresh send
    retryCount.value = 0;
    isReconnecting.value = false;

    // Push user message
    const userMsg: ChatMessageModel = {
      id: generateMessageId(),
      role: 'user',
      content: text,
      sources: [],
      isStreaming: false,
      error: null,
    };
    messages.value = [...messages.value, userMsg];

    await _sendMessageWithRetry(text);
  }

  /**
   * Retry wrapper: calls _sendMessageOnce with exponential backoff on failure.
   * Does NOT push the user message — that's done by sendMessage().
   */
  async function _sendMessageWithRetry(text: string): Promise<void> {
    try {
      await _sendMessageOnce(text);
    } catch {
      retryCount.value++;
      if (retryCount.value < MAX_RETRIES) {
        isReconnecting.value = true;
        await wait(getBackoff(retryCount.value - 1));
        await _sendMessageWithRetry(text);
      } else {
        // Max retries exhausted — error state already set by _sendMessageOnce
        isReconnecting.value = false;
      }
    }
  }

  /**
   * Core streaming logic: pushes assistant message, consumes SSE events.
   * On network failure, throws so the retry wrapper can re-attempt.
   * On server-sent error events, returns without throwing (final state).
   */
  async function _sendMessageOnce(text: string): Promise<void> {
    // If reconnecting, remove the partial assistant message from the previous attempt
    if (retryCount.value > 0) {
      const msgs = [...messages.value];
      if (msgs.length > 0 && msgs[msgs.length - 1].role === 'assistant') {
        msgs.pop();
      }
      messages.value = msgs;
    }

    // Push fresh assistant message placeholder
    const assistantMsg: ChatMessageModel = {
      id: generateMessageId(),
      role: 'assistant',
      content: '',
      sources: [],
      isStreaming: true,
      error: null,
    };
    messages.value = [...messages.value, assistantMsg];

    isStreaming.value = true;
    error.value = null;
    isReconnecting.value = false;

    try {
      const eventStream = streamChat({
        message: text,
        conversation_id: conversationId.value,
      });

      for await (const event of eventStream) {
        const msgIndex = messages.value.length - 1;
        const current = messages.value[msgIndex];

        switch (event.type) {
          case 'token':
            messages.value[msgIndex] = {
              ...current,
              content: current.content + event.content,
            };
            await nextTick();
            break;

          case 'sources':
            messages.value[msgIndex] = {
              ...current,
              sources: event.sources as SourceInfo[],
            };
            break;

          case 'done':
            messages.value[msgIndex] = {
              ...current,
              isStreaming: false,
            };
            if (event.conversation_id) {
              setConversationId(event.conversation_id);
            }
            isStreaming.value = false;
            break;

          case 'error':
            messages.value[msgIndex] = {
              ...current,
              isStreaming: false,
              error: event.message,
            };
            error.value = event.message;
            isStreaming.value = false;
            // Server-sent errors are final — don't retry
            return;
        }
      }
    } catch {
      // Network error — mark the partial message, then throw for retry
      const msgIndex = messages.value.length - 1;
      if (msgIndex >= 0) {
        messages.value[msgIndex] = {
          ...messages.value[msgIndex],
          isStreaming: false,
        };
      }
      isStreaming.value = false;
      throw new Error('Connection lost');
    } finally {
      if (!isReconnecting.value) {
        isStreaming.value = false;
      }
    }
  }

  /**
   * Retry the last failed exchange by re-sending the last user message.
   * Removes both the errored assistant message and the last user message
   * before retrying (sendMessage will re-add both).
   */
  async function retryLastMessage(): Promise<void> {
    // Find the last user message
    let lastUserText: string | null = null;
    for (let i = messages.value.length - 1; i >= 0; i--) {
      if (messages.value[i].role === 'user') {
        lastUserText = messages.value[i].content;
        break;
      }
    }

    if (lastUserText === null) return;

    // Remove the last assistant (errored) and last user (will be re-sent)
    const msgs = [...messages.value];
    if (msgs.length > 0 && msgs[msgs.length - 1].role === 'assistant') {
      msgs.pop(); // remove errored assistant
    }
    if (msgs.length > 0 && msgs[msgs.length - 1].role === 'user') {
      msgs.pop(); // remove last user (sendMessage will push a fresh one)
    }
    messages.value = msgs;

    // Re-send (this resets retry state and pushes a new user message)
    await sendMessage(lastUserText);
  }

  /** Clear all messages and reset streaming/error state. */
  function clearMessages(): void {
    messages.value = [];
    error.value = null;
    isStreaming.value = false;
    isReconnecting.value = false;
    retryCount.value = 0;
  }

  /** Start a new conversation: generate fresh ID and clear messages. */
  function newChat(): void {
    newConversation();
    clearMessages();
  }

  /** Dismiss the global error banner. */
  function dismissError(): void {
    error.value = null;
  }

  // ── Return (state exposed as readonly) ──
  return {
    messages: readonly(messages),
    isStreaming: readonly(isStreaming),
    error: readonly(error),
    isReconnecting: readonly(isReconnecting),
    messageCount,
    lastMessage,
    sendMessage,
    retryLastMessage,
    clearMessages,
    newChat,
    dismissError,
  };
}
