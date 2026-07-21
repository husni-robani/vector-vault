// Vector Vault — Chat State & SSE Streaming
// Core composable driving the RAG chat experience.

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

export function useChat() {
  // ── State ──
  const messages: Ref<ChatMessageModel[]> = ref([]);
  const isStreaming: Ref<boolean> = ref(false);
  const error: Ref<string | null> = ref(null);

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
   * Handles token-by-token accumulation, source citations, error events,
   * and connection failures.
   */
  async function sendMessage(text: string): Promise<void> {
    // Guard: don't send while already streaming
    if (isStreaming.value) return;

    // 1. Push user message
    const userMsg: ChatMessageModel = {
      id: generateMessageId(),
      role: 'user',
      content: text,
      sources: [],
      isStreaming: false,
      error: null,
    };
    messages.value = [...messages.value, userMsg];

    // 2. Push empty assistant message (placeholder for streaming)
    const assistantMsg: ChatMessageModel = {
      id: generateMessageId(),
      role: 'assistant',
      content: '',
      sources: [],
      isStreaming: true,
      error: null,
    };
    messages.value = [...messages.value, assistantMsg];

    // 3. Enter streaming state
    isStreaming.value = true;
    error.value = null;

    try {
      // 4. Start SSE stream
      const eventStream = streamChat({
        message: text,
        conversation_id: conversationId.value,
      });

      // 5. Consume SSE events
      for await (const event of eventStream) {
        const msgIndex = messages.value.length - 1;
        const current = messages.value[msgIndex];

        switch (event.type) {
          case 'token':
            // Append token content to the growing assistant message
            messages.value[msgIndex] = {
              ...current,
              content: current.content + event.content,
            };
            // Allow Vue to flush DOM updates before next token
            await nextTick();
            break;

          case 'sources':
            // Attach source citations to the assistant message
            messages.value[msgIndex] = {
              ...current,
              sources: event.sources as SourceInfo[],
            };
            break;

          case 'done':
            // Mark streaming complete
            messages.value[msgIndex] = {
              ...current,
              isStreaming: false,
            };
            // Persist conversation_id if the backend provides one
            if (event.conversation_id) {
              setConversationId(event.conversation_id);
            }
            isStreaming.value = false;
            break;

          case 'error':
            // Mark message as errored and set global error
            messages.value[msgIndex] = {
              ...current,
              isStreaming: false,
              error: event.message,
            };
            error.value = event.message;
            isStreaming.value = false;
            break;
        }
      }
    } catch {
      // Fetch or stream-level error (connection drop, network failure)
      const msgIndex = messages.value.length - 1;
      if (msgIndex >= 0) {
        messages.value[msgIndex] = {
          ...messages.value[msgIndex],
          isStreaming: false,
          error: 'Connection lost. Please try again.',
        };
      }
      error.value = 'Connection lost. Please try again.';
    } finally {
      isStreaming.value = false;
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

    // Re-send
    await sendMessage(lastUserText);
  }

  /** Clear all messages and reset streaming/error state. */
  function clearMessages(): void {
    messages.value = [];
    error.value = null;
    isStreaming.value = false;
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
    messageCount,
    lastMessage,
    sendMessage,
    retryLastMessage,
    clearMessages,
    newChat,
    dismissError,
  };
}
