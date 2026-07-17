<template>
  <div class="chat-view">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2 class="sidebar-title">Documents</h2>
        <span class="sidebar-count">3</span>
      </div>

      <div class="document-list">
        <!-- Hardcoded document card for visual demonstration -->
        <article class="document-card">
          <div class="document-card__icon">&#x1F4C4;</div>
          <div class="document-card__body">
            <h3 class="document-card__title">ml-notes.md</h3>
            <p class="document-card__meta">12 chunks &middot; 8.4 KB</p>
          </div>
        </article>

        <article class="document-card">
          <div class="document-card__icon">&#x1F4C4;</div>
          <div class="document-card__body">
            <h3 class="document-card__title">deep-learning.pdf</h3>
            <p class="document-card__meta">24 chunks &middot; 2.1 MB</p>
          </div>
        </article>

        <article class="document-card">
          <div class="document-card__icon">&#x1F4C4;</div>
          <div class="document-card__body">
            <h3 class="document-card__title">research-notes.md</h3>
            <p class="document-card__meta">8 chunks &middot; 3.2 KB</p>
          </div>
        </article>
      </div>

      <!-- Empty state area (shown when no documents) -->
      <div class="sidebar-empty">
        <p class="sidebar-empty__text">No documents yet. Upload your first document to get started.</p>
      </div>
    </aside>

    <!-- Chat Panel -->
    <main class="chat-panel">
      <div class="chat-content">
        <!-- Header -->
        <header class="chat-header">
          <h1 class="chat-header__wordmark">Vector Vault</h1>
          <p class="chat-header__tagline">Your personal knowledge, searchable and conversational</p>
        </header>

        <!-- Messages Area -->
        <div class="chat-messages">
          <ChatMessage
            role="user"
            content="What are the key themes in my notes on machine learning?"
          />

          <ChatMessage
            role="assistant"
            content="Based on your documents, the key themes are supervised learning, neural networks, and model evaluation techniques."
            :sources="[
              { title: 'ml-notes.md', chunk_index: 3, distance: 0.12, snippet: 'Supervised learning algorithms...' },
              { title: 'deep-learning.pdf', chunk_index: 7, distance: 0.18, snippet: 'Neural network architectures...' },
            ]"
          />
        </div>

        <!-- Input Bar -->
        <div class="chat-input-area">
          <ChatInput placeholder="Ask a question about your documents..." />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import ChatMessage from '@/components/ChatMessage.vue';
import ChatInput from '@/components/ChatInput.vue';
</script>

<style scoped>
/* ── Main Layout ── */
.chat-view {
  display: flex;
  flex-direction: row;
  height: calc(100vh - var(--spacing-3xl) * 2);
  gap: 0;
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

/* ── Sidebar ── */
.sidebar {
  width: 280px;
  min-width: 280px;
  background: var(--color-bg-secondary);
  border-right: var(--border-width-normal) solid var(--border-color-light);
  display: flex;
  flex-direction: column;
  padding: var(--spacing-xl);
  gap: var(--spacing-lg);
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding-bottom: var(--spacing-md);
  border-bottom: var(--border-width-thin) solid var(--border-color-light);
}

.sidebar-title {
  font-family: var(--font-display);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  letter-spacing: var(--letter-spacing-tight);
}

.sidebar-count {
  font-family: var(--font-body);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-normal);
  color: var(--color-text-tertiary);
  letter-spacing: var(--letter-spacing-wider);
  text-transform: uppercase;
}

/* ── Document Cards ── */
.document-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.document-card {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-bg-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.document-card:hover {
  background: var(--color-bg-tertiary);
}

.document-card__icon {
  font-size: var(--font-size-xl);
  line-height: 1;
  flex-shrink: 0;
}

.document-card__body {
  min-width: 0;
  flex: 1;
}

.document-card__title {
  font-family: var(--font-body);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  line-height: var(--line-height-snug);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.document-card__meta {
  font-family: var(--font-body);
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin-top: var(--spacing-xs);
}

/* ── Empty State ── */
.sidebar-empty {
  display: none;
  flex: 1;
  align-items: center;
  justify-content: center;
}

.sidebar-empty__text {
  font-family: var(--font-body);
  font-size: var(--font-size-base);
  color: var(--color-text-tertiary);
  text-align: center;
  line-height: var(--line-height-normal);
}

/* ── Chat Panel ── */
.chat-panel {
  flex: 1;
  background: var(--color-bg-primary);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-content {
  max-width: 720px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: var(--spacing-3xl) var(--spacing-xl);
}

/* ── Chat Header ── */
.chat-header {
  text-align: center;
  padding-bottom: var(--spacing-3xl);
  border-bottom: var(--border-width-thin) solid var(--border-color-light);
  margin-bottom: var(--spacing-3xl);
}

.chat-header__wordmark {
  font-family: var(--font-display);
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  letter-spacing: var(--letter-spacing-tight);
  line-height: var(--line-height-tight);
}

.chat-header__tagline {
  font-family: var(--font-body);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-normal);
  color: var(--color-text-tertiary);
  margin-top: var(--spacing-sm);
}

/* ── Messages Area ── */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

/* ── Input Area ── */
.chat-input-area {
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: var(--border-width-thin) solid var(--border-color-light);
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .sidebar {
    width: 240px;
    min-width: 240px;
  }
}

@media (max-width: 500px) {
  .sidebar {
    display: none;
  }

  .chat-content {
    padding: var(--spacing-xl) var(--spacing-md);
  }
}
</style>
