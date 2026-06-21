# Question Vector Search

## Current Approach: Single-Vector Retrieval

When a user asks a question, `AnswerQuestionUseCase` runs the following pipeline:

```
question (string)
  → embed (single 384-dim vector via all-MiniLM-L6-v2)
    → ChromaDB cosine-similarity search (top-k closest chunks)
      → build prompt → LLM generates answer
```

The entire question is embedded as **one** vector. That vector captures the *centroid* of semantic meaning — the "average direction" of all words in the question. ChromaDB then finds the chunk vectors nearest to that point.

## What Questions Work Well

Single-vector search works best when the question and the target chunks share **direct semantic overlap**:

| Question Type | Example | Why It Works |
|---|---|---|
| Factual lookup | "What is the default port for Ollama?" | Question shares keywords with the relevant chunk |
| Definitions | "What does RAG stand for?" | Direct semantic match |
| Direct reference | "How do I configure ChromaDB?" | The chunk about ChromaDB config is nearby in vector space |

## Known Limitations

### Vocabulary Mismatch
The question and the stored document may use different words for the same concept.

- User asks: "How do I set up the database?"
- Document says: "Initialize the persistence layer" — embedding distance may be large despite high relevance.

### Compound / Multi-Faceted Questions
A single vector averages multiple concepts, potentially missing chunks for each sub-topic.

- "What are the tradeoffs between ChromaDB and Pinecone for a RAG system?"
- This touches on three concepts (ChromaDB, Pinecone, RAG). The averaged vector may be far from some relevant chunks.

### Multi-Hop Reasoning
Questions requiring information from multiple disjoint chunks struggle because the query vector sits somewhere between them, close to neither.

- "How does the error handling in `AnswerQuestionUseCase` differ from `IngestDocumentUseCase`?"
- Requires finding chunks about *both* use cases and comparing them.

### Negation / Absence
Embedding models handle negation poorly. "What doesn't the project support?" may produce a vector close to "what the project supports."

### Ambiguous or Open-Ended Queries
- "Tell me about the architecture" — broad, no single target, the nearest chunks may be arbitrary.

## Why Single Vector Is Reasonable for v1

Vector Vault is a **personal knowledge management** system. Documents are uploaded by the same person who asks questions. This reduces the vocabulary gap:

- Users know what's in their documents
- They tend to ask questions using similar phrasing
- The document corpus is personal, not a massive heterogeneous pool

The bounded cosine distance range (0–2) also makes it easy to set confidence thresholds (e.g., discard matches with distance > 0.5).

## Future Improvement Options

### 1. Multi-Query Retrieval

Decompose the user's question into multiple sub-questions (via the LLM), embed each sub-question, search for each independently, then deduplicate and merge results.

```
"What are the tradeoffs between A and B?"
  → LLM decomposition
    → "What are the benefits of A?"
    → "What are the drawbacks of A?"
    → "What are the benefits of B?"
    → "What are the drawbacks of B?"
  → 4 separate vector searches
  → merge + deduplicate results
```

**Pros**: Better coverage for compound questions.
**Cons**: 4× LLM calls + 4× vector searches per user question. Higher latency.

### 2. HyDE (Hypothetical Document Embeddings)

Have the LLM generate a hypothetical answer to the question *first*, then embed that answer and use it as the search query instead of the raw question.

```
question "What is the default Ollama port?"
  → LLM generates: "Ollama runs on port 11434 by default"
    → embed the generated text
      → search with that vector
```

**Pros**: Bridges vocabulary gap — the generated text uses language similar to the documents.
**Cons**: Extra LLM call per question. Generated text may be wrong (hallucination).

### 3. Reranking

Retrieve a larger candidate set (e.g., k=20) with vector search, then pass all candidates through a reranker model (e.g., cross-encoder) that scores each chunk against the original question with higher precision.

```
search(k=20) → reranker scores all 20 → return top-5
```

**Pros**: Higher precision, catches matches that raw vector search misses. No extra LLM calls.
**Cons**: Requires a reranker model. ~20× more scoring computation per query.

### 4. Hybrid Search (Sparse + Dense)

Combine vector (dense) search with keyword (sparse/BM25) search and merge results.

```
vector search (cosine) × weighted combination × BM25 keyword search
```

**Pros**: Catches exact keyword matches that vector search might miss. Well-studied, proven approach.
**Cons**: Requires additional indexing (BM25). Tuning the fusion weights.

### 5. Query Embedding Augmentation

Augment the original question with metadata or document structure before embedding.

```
question "How do I handle errors?"
  → augmented: "How do I handle errors in the context of Python dependency injection FastAPI clean architecture?"
```

**Pros**: Simple, no extra infrastructure.
**Cons**: Context window limits. The augmentation may bias in the wrong direction.

---

## Summary

| Approach | Latency Impact | Complexity | Precision Gain |
|---|---|---|---|
| Multi-Query Retrieval | Medium (LLM calls) | Low-medium | High for compound Qs |
| HyDE | Medium (LLM call) | Low | Moderate (vocabulary gap) |
| Reranking | Low | Medium (model infra) | High |
| Hybrid Search (BM25) | Low | High (dual index) | Moderate-high |
| Query Augmentation | Low | Low | Low-moderate |

For the current project scope (personal knowledge base, single user, moderate corpus size), single-vector cosine search is a pragmatic v1. Reranking and multi-query retrieval are the most impactful next steps if precision becomes insufficient.
