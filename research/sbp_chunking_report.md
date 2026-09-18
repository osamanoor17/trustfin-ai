# TrustFin AI: SBP Document Chunking & Provenance Quality Report (Phase 1D)

> **Document Version:** 1.0.0  
> **Execution Date:** 2026-09-18  
> **Status:** Phase 1D Experimental Chunking & Provenance Complete  
> **Input Corpus:** [`data/processed/sbp/sbp_pages.jsonl`](file:///d:/trustfin-ai/data/processed/sbp/sbp_pages.jsonl) (SHA-256: `086af1f787c3bb62fdc1b69af47265502da006f23d8fff19445719c75f2d40a1`)  
> **Manifest Path:** [`data/manifest/sbp_chunking_manifest.jsonl`](file:///d:/trustfin-ai/data/manifest/sbp_chunking_manifest.jsonl)  

---

> [!IMPORTANT]
> **EXPERIMENTAL BOUNDARY DISCLAIMER:**  
> Phase 1D establishes three standardized, reproducible experimental chunking variants for the State Bank of Pakistan (SBP) regulatory corpus. No vector database, BM25 index, sentence-transformer model, LLM call, or RAG retrieval pipeline has been deployed. All strategies serve as initial experimental baselines for subsequent retrieval benchmarking.

---

## 1. Word Tokenization Rule

All strategies, manifest statistics, overlap calculations, and coverage validation functions adhere strictly to a single, deterministic word-tokenization rule:
* **Tokenization Function:** `text.split()` (splits string on standard whitespace `\s+`).
* **Word Count Definition:** `word_count = len(text.split())`.
* **No NLP Dependencies:** Tokenization requires no external tokenizers or model-specific dependencies, ensuring 100% transparent and portable word-boundary calculations across Python environments.

---

## 2. Experimental Strategy Specifications & Algorithmic Differences

Three distinct chunking strategies were implemented in [`scripts/chunk_documents.py`](file:///d:/trustfin-ai/scripts/chunk_documents.py):

### 2.1 Strategy A: Page Baseline (`page_v1`)
* **Policy:** Baseline 1-to-1 page strategy. One extracted PDF page becomes exactly one chunk (`chunk_text = page.normalized_text`).
* **Page Boundaries:** Page boundaries are strictly preserved. Pages are never merged or split.
* **Overlap:** 0 words overlap.
* **Target Size:** Variable (1 page = 1 chunk).

### 2.2 Strategy B: Fixed Word Window (`fixed_300w_50o_v1`)
* **Policy:** Continuous fixed-size word window across document text.
* **Configuration:** `target_words = 300`, `overlap_words = 50`, `step = 250`.
* **Page Boundary Handling:** Page boundaries DO NOT influence where windows are cut. Document text is treated as a continuous word stream.
* **Exact Provenance Mapping:** Parallel word-to-page indexing tracks the exact 1-based page origin of every individual word. `source_pages`, `page_start`, and `page_end` reflect exact contributing source pages.

### 2.3 Strategy C: Page-Aware Word Window (`page_aware_300w_50o_v1`)
* **Policy:** Structural windowing that respects page boundaries as primary document units.
* **Configuration:** `target_words = 300`, `overlap_words = 50`.
* **Page Boundary Handling:** 
  - If a single page word count exceeds `target_words` (300 words), the page is split internally using word windowing (`step = 250`).
  - If pages are each $\le 300$ words, whole page text segments are accumulated sequentially across adjacent pages up to 300 words.
  - Page boundaries are preserved when accumulating: page text is not split across chunks unless a single page exceeds the 300-word target.
* **Overlap Handling:** Overlap is maintained by carrying forward the trailing `overlap_words` (50 words) from the previous chunk to serve as the prefix for the subsequent chunk. `source_pages` records all pages contributing text (including overlap prefix).

---

## 3. Comparative Chunk Statistics Table

| Metric / Attribute | Strategy A: `page_v1` | Strategy B: `fixed_300w_50o_v1` | Strategy C: `page_aware_300w_50o_v1` |
|---|---|---|---|
| **Strategy Type** | Page Baseline | Continuous Fixed Window | Page-Aware Window |
| **Target / Overlap Words** | 1 page / 0 overlap | 300 words / 50 overlap | 300 words / 50 overlap |
| **Total Chunks Generated** | **142** | **199** | **248** |
| **Chunks: Digital Banking Policy (2022)** | 42 | 61 | 74 |
| **Chunks: Customer Onboarding (2025)** | 21 | 27 | 36 |
| **Chunks: Onboarding Amendment (2026)** | 2 | 2 | 3 |
| **Chunks: Consumer Protection (2025)** | 77 | 109 | 135 |
| **Min Words per Chunk** | 4 | 138 | 52 |
| **Max Words per Chunk** | 581 | 300 | 350 |
| **Mean Words per Chunk** | 348.54 | 297.70 | 248.76 |
| **Median Words per Chunk** | 418.00 | 300.00 | 294.50 |
| **Page-Crossing Chunks** | **0** (0.0%) | **132** (66.3%) | **134** (54.0%) |
| **Table-Like Content Chunks** | 42 | 60 | 75 |
| **Low-Text Chunks** | 1 | 1 | 1 |
| **Output JSONL Path** | `data/processed/sbp/chunks/page_v1.jsonl` | `data/processed/sbp/chunks/fixed_300w_50o_v1.jsonl` | `data/processed/sbp/chunks/page_aware_300w_50o_v1.jsonl` |
| **Output SHA-256 (Run 1 & 2)** | `74062cb22bffff87...` | `2f107d2c63f7b5be...` | `96ed48beb00ae44f...` |
| **Determinism Status** | **BYTE-IDENTICAL** | **BYTE-IDENTICAL** | **BYTE-IDENTICAL** |

---

## 4. Source Coverage & Content Integrity Validation

To guarantee zero content loss and strict text sequence fidelity, automated coverage validation (`validate_strategy_coverage`) was executed for every strategy across all 4 SBP documents using **Position- and Sequence-Aware Provenance**:
* **Validation Methodology:**
  1. **Token Position Provenance:** Represents document source text as an ordered sequence of 0-based token position indices (`0` to `N-1`).
  2. **Occurrence Coverage:** Verifies that every single source token position index `0..N-1` is present in the position union of generated chunks (`union(chunk_positions) == set(range(N))`), ensuring repeated token occurrences cannot be omitted undetected.
  3. **Sequence Integrity:** Validates that each chunk's token list forms a contiguous, ordered slice of the document's source token stream, flagging any dropped, fabricated, or reordered tokens.
* **Results:**
  - `page_v1`: **100% POSITION & SEQUENCE COVERAGE PASSED**
  - `fixed_300w_50o_v1`: **100% POSITION & SEQUENCE COVERAGE PASSED**
  - `page_aware_300w_50o_v1`: **100% POSITION & SEQUENCE COVERAGE PASSED**
* **Cross-Document Integrity:** Zero cross-document mixing observed. Every chunk strictly contains text from a single `document_id`.

---

## 5. Low-Text Page & Observational Table Signal Handling

### 5.1 Low-Text Page Handling
* `PK-SBP-AML_KYC_GUIDANCE-2025-0001` Page 1 contains 42 characters (cover title).
* **`page_v1`:** Preserved as a distinct chunk (`is_low_text = True`).
* **Window Strategies (`fixed_300w_50o_v1`, `page_aware_300w_50o_v1`):** Participating text is included in windowing while inheriting `is_low_text = True`.

### 5.2 Table-Like Signal Propagation
* `contains_table_like_content` is inherited as `True` if any contributing source page was observationally flagged with table-like content during Phase 1C.
* Table text is preserved as normalized plain text without structured re-interpretation or rewriting.

---

## 6. Output Reproducibility Verification

Executed `.venv\Scripts\python scripts/chunk_documents.py` across two consecutive runs. The resulting JSONL output files produced identical SHA-256 digests:

| Strategy ID | Output File Path | SHA-256 Digest (Run 1) | SHA-256 Digest (Run 2) | Match Status |
|---|---|---|---|---|
| `page_v1` | `data/processed/sbp/chunks/page_v1.jsonl` | `74062cb22bffff87995bbb0d247c37ff55caec89e7877998ba0aac07358be3e8` | `74062cb22bffff87995bbb0d247c37ff55caec89e7877998ba0aac07358be3e8` | **BYTE-IDENTICAL** |
| `fixed_300w_50o_v1` | `data/processed/sbp/chunks/fixed_300w_50o_v1.jsonl` | `2f107d2c63f7b5be5ff99741d1f017639ea6fcd26f3977c56b7f7ceeced7803d` | `2f107d2c63f7b5be5ff99741d1f017639ea6fcd26f3977c56b7f7ceeced7803d` | **BYTE-IDENTICAL** |
| `page_aware_300w_50o_v1` | `data/processed/sbp/chunks/page_aware_300w_50o_v1.jsonl` | `96ed48beb00ae44fc05b2541f1f4e5d83f8cca305f7adcb4d538599e183d15f6` | `96ed48beb00ae44fc05b2541f1f4e5d83f8cca305f7adcb4d538599e183d15f6` | **BYTE-IDENTICAL** |

---

## 7. Input Page Corpus & Raw Storage Immutability

* **Input Page Corpus Path:** `data/processed/sbp/sbp_pages.jsonl`
* **Input SHA-256 (Pre & Post-Chunking):** `086af1f787c3bb62fdc1b69af47265502da006f23d8fff19445719c75f2d40a1` (**UNTOUCHED**)
* **Raw PDF Binary SHA-256 (Pre & Post-Chunking):** All 4 raw SBP PDFs remain 100% identical and unedited.
