# Phase 2C — Multilingual Dense Retrieval Baseline Research Specification & Experimental Report

## 1. Executive Summary
Phase 2C evaluates whether dense multilingual semantic embeddings can improve retrieval performance for English, Urdu, and Roman Urdu financial queries against the trusted, English-only State Bank of Pakistan (SBP) document corpus, compared with the frozen Phase 2B BM25 sparse lexical baseline (Commit [`419dea62d9e6181eee42b6c45a1d92ddd15ffd43`](https://github.com/osamanoor17/trustfin-ai/commit/419dea62d9e6181eee42b6c45a1d92ddd15ffd43)).

The experiment was executed reproducibly on Google Colab GPU under experimental code freeze [`8808f61675190d19dd2c60fd5c95392cd13e0dcd`](https://github.com/osamanoor17/trustfin-ai/commit/8808f61675190d19dd2c60fd5c95392cd13e0dcd). Dual-run reproducibility verification produced byte-identical output artifacts (`Byte-Identical Output: True`).

---

## 2. Frozen Multilingual Embedding Model Set

The baseline experiment evaluates exactly three pre-selected, publicly available multilingual embedding models. Models were selected prior to benchmark evaluation to eliminate selection bias.

| Model Candidate | Hugging Face ID | Revision Commit SHA | Dim | Max Tokens | Similarity Metric | Query Prefix | Passage Prefix | Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Multilingual-E5-Base** | `intfloat/multilingual-e5-base` | `d128750597153bb5987e10b1c3493a34e5a4502a` | 768 | 512 | Cosine (Dot product on $L_2$ norm) | `"query: "` | `"passage: "` | Retrieval-specialized multilingual baseline |
| **BGE-M3** | `BAAI/bge-m3` | `5617a9f61b028005a4858fdac845db406aefb181` | 1024 | 8192 | Cosine (Dot product on $L_2$ norm) | `""` | `""` | Multilingual dense retrieval / multi-granularity baseline (dense embeddings only) |
| **Paraphrase-MPNet-Multi** | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` | `4328cf26390c98c5e3c738b4460a05b95f4911f5` | 768 | 128 | Cosine (Dot product on $L_2$ norm) | `""` | `""` | General multilingual semantic embedding baseline |

> [!NOTE]
> **Pre-Results Revision Provenance Correction**:
> During initial pre-execution model loading verification, the originally recorded commit SHA strings were found to be invalid repository revisions. This issue was identified at first model loading prior to generating any dense embeddings, rankings, or evaluation metrics. The pre-selected model identities, order, token sequence limits, and embedding architectures were retained; their repository `main` branch heads were resolved and frozen to validated immutable SHAs (`d128750597153bb5987e10b1c3493a34e5a4502a`, `5617a9f61b028005a4858fdac845db406aefb181`, `4328cf26390c98c5e3c738b4460a05b95f4911f5`) prior to experimental execution.

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

BM25 evaluation artifacts (`research/results/bm25/bm25_summary.json` and `bm25_query_results.jsonl`) are immutable. Dense metrics (Hit@1, Hit@3, Hit@5, Hit@10, MRR@10) are directly compared against frozen BM25 baselines.

### Special Tracking for BM25 Zero-Overlap Queries
Dense retrieval does not rely on exact lexical matching. For the 4 Urdu queries with zero lexical overlap in BM25:
- `TFB-0003-UR`
- `TFB-0005-UR`
- `TFB-0006-UR`
- `TFB-0007-UR`

Dense retrieval results explicitly record the first relevant rank achieved by each model, evaluating whether semantic embedding spaces successfully recover cross-lingual evidence for queries with zero lexical overlap.

---

## 6. Cloud Execution Workflow (Google Colab / Kaggle)

The 3-model embedding experiment was executed on Google Colab T4 GPU:

1. Cloned repository and installed requirements.
2. Executed:
   ```bash
   python scripts/run_dense_baseline.py --execute --device cuda
   ```
3. Generated evaluation artifacts saved directly to `research/results/dense/`.

---

## 7. Experimental Results & Comparative Analysis

### 7.1 Overall Results Across All 9 Model $\times$ Chunk-Strategy Configurations

The table below summarizes retrieval performance across all 30 answerable queries for the 9 model candidate $\times$ chunking strategy combinations:

| Model Candidate | Chunk Strategy | Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR@10 | Chunk Trunc % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `intfloat/multilingual-e5-base` | `page_v1` | 0.6333 | 0.8667 | 0.9333 | 0.9333 | 0.7444 | 63.38% |
| `intfloat/multilingual-e5-base` | `fixed_300w_50o_v1` | 0.7000 | 0.9333 | 0.9667 | 1.0000 | 0.8287 | 6.53% |
| `intfloat/multilingual-e5-base` | `page_aware_300w_50o_v1` | 0.6667 | 0.8000 | 0.8667 | 0.9000 | 0.7428 | 5.24% |
| `BAAI/bge-m3` | `page_v1` | 0.6000 | 0.9000 | 0.9667 | 1.0000 | 0.7548 | 0.00% |
| `BAAI/bge-m3` | `fixed_300w_50o_v1` | **0.8000** | **1.0000** | **1.0000** | **1.0000** | **0.8778** | **0.00%** |
| `BAAI/bge-m3` | `page_aware_300w_50o_v1` | 0.5000 | 0.9333 | 0.9333 | 1.0000 | 0.7048 | 0.00% |
| `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` | `page_v1` | 0.3333 | 0.4000 | 0.5000 | 0.6333 | 0.3981 | 92.25% |
| `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` | `fixed_300w_50o_v1` | 0.3333 | 0.5667 | 0.5667 | 0.6000 | 0.4444 | 100.00% |
| `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` | `page_aware_300w_50o_v1` | 0.3333 | 0.4000 | 0.4667 | 0.5000 | 0.3881 | 94.76% |

---

### 7.2 Strongest Observed Configuration (Pilot Benchmark)

Descriptively, the strongest observed configuration on this 30-answerable-query pilot benchmark was:

$$\mathbf{BAAI/bge\text{-}m3 + fixed\_300w\_50o\_v1}$$

- **Overall Answerable Metrics**:
  - **Hit@1**: `0.8000` (24 / 30 queries)
  - **Hit@3**: `1.0000` (30 / 30 queries)
  - **Hit@5**: `1.0000` (30 / 30 queries)
  - **Hit@10**: `1.0000` (30 / 30 queries)
  - **MRR@10**: `0.8778`
- **Language MRR@10 Breakdown**:
  - **English**: `0.8833`
  - **Urdu**: `0.8167`
  - **Roman Urdu**: `0.9333`

*Note: This represents an observed descriptive result on the 30-answerable-query pilot benchmark, NOT a universal model ranking.*

---

### 7.3 Language-Level Breakdown & BM25 Baseline Comparison

The table below breaks down MRR@10 across language variants (10 queries each) compared to the Phase 2B BM25 baseline:

| Strategy / Model Candidate | Chunk Strategy | English MRR@10 | Urdu MRR@10 | Roman Urdu MRR@10 | Overall MRR@10 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BM25 Baseline** | `page_v1` | 0.8500 | 0.4667 | 0.7833 | 0.7000 |
| **BM25 Baseline** | `fixed_300w_50o_v1` | 0.8000 | 0.4700 | 0.7833 | 0.6844 |
| **BM25 Baseline** | `page_aware_300w_50o_v1` | 0.7833 | 0.4200 | 0.8333 | 0.6789 |
| **E5-Base** | `page_v1` | 0.8833 | 0.5417 | 0.8083 | 0.7444 |
| **E5-Base** | `fixed_300w_50o_v1` | 0.9000 | 0.7361 | 0.8500 | 0.8287 |
| **E5-Base** | `page_aware_300w_50o_v1` | 0.8500 | 0.5583 | 0.8200 | 0.7428 |
| **BGE-M3** | `page_v1` | 0.7833 | 0.7226 | 0.7583 | 0.7548 |
| **BGE-M3** | `fixed_300w_50o_v1` | **0.8833** | **0.8167** | **0.9333** | **0.8778** |
| **BGE-M3** | `page_aware_300w_50o_v1` | 0.7333 | 0.6810 | 0.7000 | 0.7048 |
| **MPNet** | `page_v1` | 0.4625 | 0.3533 | 0.3783 | 0.3981 |
| **MPNet** | `fixed_300w_50o_v1` | 0.5333 | 0.3500 | 0.4500 | 0.4444 |
| **MPNet** | `page_aware_300w_50o_v1` | 0.4143 | 0.3250 | 0.4250 | 0.3881 |

#### Key Descriptive Observations:
1. **Urdu Cross-Lingual Improvement**: Both E5-Base (`fixed_300w_50o_v1` MRR: `0.7361`) and BGE-M3 (`fixed_300w_50o_v1` MRR: `0.8167`) substantially outperformed BM25 (`fixed_300w_50o_v1` MRR: `0.4700`) on Urdu queries. Multilingual dense embedding spaces bridge the cross-lingual gap between Urdu query phrasing and English SBP regulatory source text.
2. **Roman Urdu Performance**: BGE-M3 achieved `0.9333` MRR@10 on Roman Urdu queries under `fixed_300w_50o_v1` (9 out of 10 queries retrieved relevant evidence at Rank 1), demonstrating robust transliterated semantic alignment.
3. **English Mono-Lingual Performance**: Dense models maintained or slightly exceeded BM25 performance on English queries (BGE-M3 & E5-Base English MRR `0.8833`–`0.9000` vs BM25 `0.8000`–`0.8500`).

---

### 7.4 Analysis of Zero-Lexical-Overlap Urdu Queries

Four answerable Urdu queries had zero lexical vocabulary overlap with the BM25 index: `TFB-0003-UR`, `TFB-0005-UR`, `TFB-0006-UR`, and `TFB-0007-UR`. Under Phase 2B BM25 evaluation rules requiring a positive-score relevant retrieval, queries with zero vocabulary overlap assigned 0.0 scores to all index chunks, resulting in complete retrieval failure (no positive-score hit) for all zero-overlap queries. In the case of `TFB-0007-UR`, chunk `000001` was placed at rank 1 solely due to deterministic zero-score tie-breaking (`-score, chunk_id`), but did not constitute a positive-score retrieval hit.

The table below details the rank of the first relevant chunk retrieved by BM25 vs Dense models using the exact frozen benchmark concept identifiers from `data/benchmarks/finurdu_pilot_v0_1.jsonl`:

| Benchmark Query ID | Frozen Concept Identifier | BM25 (`fixed_300w`) | E5 (`page_v1`) | E5 (`fixed_300w`) | BGE-M3 (`page_v1`) | BGE-M3 (`fixed_300w`) | MPNet (`fixed_300w`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `TFB-0003-UR` | `DIGITAL_BANK_PILOT_DEPOSIT_CAP_001` | No Hit (No positive score) | Rank 1 | Rank 1 | Rank 4 | **Rank 1** | Rank 1 |
| `TFB-0005-UR` | `CUSTOMER_ONBOARDING_FICTITIOUS_ACCOUNTS_001` | No Hit (No positive score) | Rank 2 | Rank 2 | Rank 1 | **Rank 1** | No Hit |
| `TFB-0006-UR` | `ASAAN_ACCOUNT_CREDIT_BALANCE_LIMIT_001` | No Hit (No positive score) | No Hit | Rank 2 | Rank 2 | **Rank 3** | No Hit |
| `TFB-0007-UR` | `DIGITAL_ONBOARDING_NON_RESIDENTS_001` | No positive-score hit (raw zero-score tie at rank 1) | Rank 3 | Rank 1 | Rank 1 | **Rank 1** | No Hit |

#### Findings:
- **BGE-M3 (`fixed_300w_50o_v1`)** retrieved relevant evidence within Top-3 for **all four** zero-overlap queries (Ranks 1, 1, 3, 1), demonstrating successful cross-lingual semantic recovery where sparse BM25 failed completely.
- **E5-Base (`fixed_300w_50o_v1`)** retrieved relevant evidence within Top-2 for **all four** zero-overlap queries (Ranks 1, 2, 2, 1).

---

### 7.5 Truncation as an Experimental Confound & Limitation

Truncation measurements reveal a crucial experimental confound regarding model sequence length limits (`max_sequence_length`):

| Model Candidate | Sequence Limit | `page_v1` Truncation % | `fixed_300w_50o_v1` Truncation % | `page_aware_300w_50o_v1` Truncation % |
| :--- | :--- | :--- | :--- | :--- |
| **E5-Base** | 512 tokens | 63.38% (90 / 142) | 6.53% (13 / 199) | 5.24% (13 / 248) |
| **BGE-M3** | 8192 tokens | 0.00% (0 / 142) | 0.00% (0 / 199) | 0.00% (0 / 248) |
| **MPNet** | 128 tokens | 92.25% (131 / 142) | 100.00% (199 / 199) | 94.76% (235 / 248) |

#### Methodological Interpretation:
- **BGE-M3**: 0% chunk truncation across all strategies due to its 8,192-token capacity.
- **E5-Base**: `page_v1` suffered high truncation (63.38%), which degraded its `page_v1` MRR (`0.7444`) compared to `fixed_300w_50o_v1` (`0.8287`, only 6.53% truncated).
- **MPNet**: Severe truncation across all strategies (92.25% to 100.00%) due to its strict 128-token limit.
- **Cautionary Rule**: MPNet's lower retrieval metrics (`MRR 0.3881–0.4444`) **must NOT be interpreted as pure evidence of inferior semantic capability**. The 128-token sequence limit truncated almost the entirety of the indexed corpus, severing key evidence text prior to embedding generation.

---

### 7.6 Corpus-Unanswerable Queries & Abstention Handling

The benchmark includes 6 corpus-unanswerable queries (`TFB-0010-EN`, `TFB-0010-UR`, `TFB-0010-RUR`, `TFB-0012-EN`, `TFB-0012-UR`, `TFB-0012-RUR`).

- **Dense Retrieval Behavior**: Unconditioned dense embedding retrieval always returns nearest-neighbor vector matches, even for unanswerable queries.
- **Phase 2C Policy**: No similarity score thresholding or abstention classification mechanism was evaluated in Phase 2C.
- **Evaluation Constraint**: In accordance with the experimental specification, unanswerable queries are excluded from standard Hit@K and MRR@10 performance calculations. Dense retrieval does not solve unanswerable query abstention without dedicated post-retrieval thresholding or LLM verification.

---

## 8. Dual-Run Reproducibility Verification

The Phase 2C experiment satisfied 100% deterministic dual-run reproducibility requirements.

### 8.1 Experimental Provenance & Freeze Identifiers
- **Execution Code Freeze Commit**: [`8808f61675190d19dd2c60fd5c95392cd13e0dcd`](https://github.com/osamanoor17/trustfin-ai/commit/8808f61675190d19dd2c60fd5c95392cd13e0dcd)
- **Validated Immutable Model Revisions**:
  - `intfloat/multilingual-e5-base`: `d128750597153bb5987e10b1c3493a34e5a4502a`
  - `BAAI/bge-m3`: `5617a9f61b028005a4858fdac845db406aefb181`
  - `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`: `4328cf26390c98c5e3c738b4460a05b95f4911f5`
- **Dual-Run Output Status**: `Byte-Identical Output: True` (Run 1 vs Run 2)

### 8.2 Immutable Output Artifact Hashes

| Artifact Path | File Description | SHA-256 Digest (Canonical LF) |
| :--- | :--- | :--- |
| `research/results/dense/dense_summary.json` | Experiment Summary & Aggregated Metrics | `24263b67d34b928087ecaed23db1b17d02a627555b7d17124eefdcbf950d91f5` |
| `research/results/dense/dense_query_results.jsonl` | Per-Query Ranking & Hit Records | `c303a88bc0b212ec3b8d5f57cf0e5dcb4884ca1cfc73f6e02510650bbd0c26f9` |

### 8.3 Non-Deterministic Execution Runtime Metadata
Runtime metadata is tracked separately in `research/results/dense/dense_run_metadata.json` for environment auditability:
- **Compute Hardware**: GPU (`Tesla T4`)
- **Python Version**: `3.11.13`
- **PyTorch Version**: `2.6.0+cu124`
- **Transformers Version**: `4.49.0`
- **Sentence-Transformers Version**: `3.4.1`
