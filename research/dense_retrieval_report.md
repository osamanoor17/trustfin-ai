# Phase 2C — Multilingual Dense Retrieval Baseline Research Specification

## 1. Executive Summary
Phase 2C evaluates whether dense multilingual semantic embeddings can improve retrieval performance for English, Urdu, and Roman Urdu financial queries against the trusted, English-only State Bank of Pakistan (SBP) document corpus, compared with the frozen Phase 2B BM25 sparse lexical baseline (Commit `419dea62d9e6181eee42b6c45a1d92ddd15ffd43`).

The experiment is strictly controlled, 100% reproducible, and designed for cloud-first execution on free GPU environments (Google Colab / Kaggle).

---

## 2. Frozen Multilingual Embedding Model Set

The baseline experiment evaluates exactly three pre-selected, publicly available multilingual embedding models. Models were selected prior to benchmark evaluation to eliminate selection bias.

| Model Candidate | Hugging Face ID | Revision Commit SHA | Dim | Max Tokens | Similarity Metric | Query Prefix | Passage Prefix | Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Multilingual-E5-Base** | `intfloat/multilingual-e5-base` | `d7dbd236...` | 768 | 512 | Cosine (Dot product on $L_2$ norm) | `"query: "` | `"passage: "` | Retrieval-specialized multilingual baseline |
| **BGE-M3** | `BAAI/bge-m3` | `5617a9f6...` | 1024 | 8192 | Cosine (Dot product on $L_2$ norm) | `""` | `""` | Multilingual dense retrieval / multi-granularity baseline (dense embeddings only) |
| **Paraphrase-MPNet-Multi** | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` | `79f23827...` | 768 | 128 | Cosine (Dot product on $L_2$ norm) | `""` | `""` | General multilingual semantic embedding baseline |

---

## 3. Mathematical Similarity & Ranking Policy

### Embedding Normalization & Vector Similarity
- Every dense embedding vector $v \in \mathbb{R}^d$ is $L_2$-normalized prior to scoring:
  $$\hat{v} = \frac{v}{\|v\|_2}$$
- Cosine similarity between query vector $\hat{v}_q$ and chunk vector $\hat{v}_d$ is computed via dot product:
  $$\text{sim}(q, d) = \hat{v}_q \cdot \hat{v}_d$$

### Full-Precision Ranking Policy
- **Full Precision Ranking**: Ranking MUST use unrounded full-precision float scores. Scores are NOT rounded to 6 decimal places prior to sorting.
- **Sequence**:
  1. Compute full-precision float dot product for all indexed chunks.
  2. Perform deterministic sort by `(-full_precision_score, chunk.chunk_id)`.
  3. Select top-k chunks.
  4. **Float Serialization Policy**: In output JSON/JSONL result artifacts, scores are serialized with 6 decimal places (`round(score, 6)`) for deterministic presentation, but all metric computations (Hit@K, MRR@10) use rank positions derived strictly from full-precision scores.

### Deterministic Tie-Breaking
When multiple chunks yield genuinely identical full-precision similarity scores:
1. Primary sort: Full-precision similarity score descending (`-score`)
2. Secondary sort: Chunk ID ascending (`chunk.chunk_id`)

### Dense Relevance Policy
Unlike BM25 lexical retrieval, **dense similarity scores are NOT required to be strictly $> 0.0$** to count as relevant (dense cosine similarities may legitimately be negative depending on model embedding space geometry). A retrieved chunk item is marked `is_relevant = True` if and only if:
1. `chunk.document_id` matches gold `expected_document_ids`
2. `set(chunk.source_pages)` intersects gold `relevant_pages`

Ranking position determines Hit@K and MRR@10.

---

## 4. Truncation Measurement Methodology (Chunks & Queries)
Different chunking strategies (`page_v1`: 142 chunks, `fixed_300w_50o_v1`: 199 chunks, `page_aware_300w_50o_v1`: 248 chunks) and query text lengths produce varying sequence lengths. To evaluate the impact of sequence length constraints across models:

- **Real Model Tokenizers**: Truncation measurement during cloud execution uses each model's actual tokenizer (loaded via Hugging Face `revision=model_revision`) including special tokens and model-specific prefixes (`"passage: " + chunk_text` for E5 passages, `"query: " + query_text` for E5 queries).
- **Chunk Truncation Metric**: For each model candidate $\times$ chunking strategy, the experiment records:
  - Model token limit ($512$ for E5, $8192$ for BGE-M3, $128$ for MPNet).
  - Exact count of chunks whose formatted token length exceeds the model limit.
  - Percentage of truncated chunks ($ \frac{\text{truncated}}{\text{total}} \times 100\% $).
- **Query Truncation Metric**: For each model candidate across all 36 benchmark queries, the experiment records:
  - Count and percentage of queries exceeding `max_sequence_length`.
- **Rule**: Chunk text is never modified, re-chunked, or discarded. Truncation is recorded as an independent research variable.

---

## 5. Frozen BM25 Baseline Comparison Protocol

BM25 evaluation artifacts (`research/results/bm25/bm25_summary.json` and `bm25_query_results.jsonl`) are immutable. Dense metrics (Hit@1, Hit@3, Hit@5, Hit@10, MRR@10) will be directly compared against frozen BM25 baselines.

### Special Tracking for BM25 Zero-Overlap Queries
Dense retrieval does not rely on exact lexical matching. For the 4 Urdu queries with zero lexical overlap in BM25:
- `TFB-0003-UR`
- `TFB-0005-UR`
- `TFB-0006-UR`
- `TFB-0007-UR`

Dense retrieval results will explicitly record the first relevant rank achieved by each model, evaluating whether semantic embedding spaces successfully recover cross-lingual evidence for queries with zero lexical overlap.

---

## 6. Cloud Execution Workflow (Google Colab / Kaggle)

To execute the 3-model embedding experiment on cloud GPUs without installing heavy dependencies locally:

1. Open Google Colab or Kaggle Notebook with T4 GPU runtime enabled.
2. Clone repository and install dependencies:
   ```bash
   !git clone https://github.com/osamanoor17/trustfin-ai.git
   %cd trustfin-ai
   !pip install -r requirements.txt sentence-transformers torch
   ```
3. Run dense retrieval baseline experiment:
   ```bash
   !python scripts/run_dense_baseline.py --execute --device cuda
   ```
4. Commit resulting `research/results/dense/` evaluation artifacts to git. Heavy vector cache files (`.npy`) are excluded by `.gitignore`.
