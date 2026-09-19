# Phase 2B — BM25 Sparse Retrieval Baseline Report

## Executive Summary

This report documents the implementation, experimental evaluation, and empirical findings of the **BM25 Sparse Retrieval Baseline (Phase 2B)** for TrustFin AI.

As the initial retrieval baseline in TrustFin AI, this experiment evaluates a pure-Python lexical **Okapi BM25 engine** across all three existing chunking strategies (`page_v1`, `fixed_300w_50o_v1`, and `page_aware_300w_50o_v1`) evaluated against the 36 multilingual query records in the FinUrdu pilot retrieval benchmark (`data/benchmarks/finurdu_pilot_v0_1.jsonl`).

> [!IMPORTANT]
> **Strict Baseline Scope**: This experiment evaluates a purely lexical baseline without dense embeddings, vector databases, rerankers, query translation, or LLMs. No hyperparameters were tuned against the benchmark ($k_1=1.5, b=0.75$ remain fixed).

---

## 1. BM25 Implementation & Scoring Equations

The retrieval engine is implemented in pure Python ([`app/services/bm25.py`](file:///d:/trustfin-ai/app/services/bm25.py)) to ensure zero external server dependencies, full transparency, and 100% deterministic ranking across environments.

### BM25 Okapi Scoring Equation
For a query $Q$ consisting of terms $q_1, q_2, \dots, q_n$ and a document chunk $d$:

$$\text{Score}(d, Q) = \sum_{i=1}^n \text{IDF}(q_i) \cdot \frac{f(q_i, d) \cdot (k_1 + 1)}{f(q_i, d) + k_1 \cdot \left(1 - b + b \cdot \frac{|d|}{\text{avgdl}}\right)}$$

where:
- $f(q_i, d)$ is the frequency of query term $q_i$ in chunk $d$.
- $|d|$ is the length of chunk $d$ in tokens.
- $\text{avgdl}$ is the average token length across all chunks in the collection.
- $k_1 = 1.5$ (fixed term frequency saturation parameter).
- $b = 0.75$ (fixed length normalization parameter).

### Smoothed Non-Negative Okapi IDF Equation
$$\text{IDF}(q) = \ln\left(\frac{N - n(q) + 0.5}{n(q) + 0.5} + 1.0\right)$$

where:
- $N$ is the total number of indexed chunks in the strategy collection.
- $n(q)$ is the number of chunks containing query term $q$.

---

## 2. Baseline Tokenizer Definition

The experiment uses a single, explicit, un-tuned baseline tokenizer:

```python
def tokenize_text(text: str) -> List[str]:
    return re.findall(r"[^\W_]+", text.lower())
```

### Tokenizer Properties
- **Unicode-Aware**: Lowercases Latin script characters while preserving Arabic script (Urdu) characters intact.
- **Punctuation & Whitespace Separation**: Splits text by non-alphanumeric boundaries.
- **Zero Heavy NLP Processing**: No stemming, lemmatization, stop-word removal, spelling correction, query translation, or LLM normalization.

---

## 3. Strict Relevance & Zero-Score Policy

### Relevance Mapping Rule
A retrieved chunk is marked as relevant (`is_relevant == True`) if and only if:
1. `chunk.document_id` matches one of the benchmark's `expected_document_ids`.
2. The intersection of `chunk.source_pages` and benchmark `relevant_pages` is non-empty.
3. **Strict Positive Score Requirement**: The retrieved chunk has a **strictly positive BM25 score** (`score > 0.0`).

> [!CAUTION]
> Chunks with `score == 0.0` (zero lexical overlap) are **NEVER** counted as hits or relevant retrievals, even if deterministic tie-breaking places a matching document/page in the top-k results.

---

## 4. Evaluated Chunking Strategies

- **`page_v1`**: 142 total chunks (exact page boundaries).
- **`fixed_300w_50o_v1`**: 199 total chunks (300-word fixed window with 50-word overlap).
- **`page_aware_300w_50o_v1`**: 248 total chunks (300-word page-aware window with 50-word overlap).

All three strategies were built and evaluated independently against the 36 benchmark query records.

---

## 5. Experimental Retrieval Metrics (30 Answerable Queries)

Metrics are evaluated across the 30 answerable query records (10 English, 10 Urdu, 10 Roman Urdu). The 6 corpus-unanswerable queries are evaluated separately.

### Strategy Comparison Table

| Strategy | Language Subset | Query Count | Zero-Overlap Count (%) | Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR@10 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`page_v1`** | **Overall Answerable** | **30** | **4 (13.33%)** | **0.5667** | **0.8667** | **0.8667** | **0.8667** | **0.7000** |
| | English (`EN`) | 10 | 0 (0.00%) | 0.7000 | 1.0000 | 1.0000 | 1.0000 | 0.8500 |
| | Urdu (`UR`) | 10 | 4 (40.00%) | 0.4000 | 0.6000 | 0.6000 | 0.6000 | 0.4667 |
| | Roman Urdu (`RU`) | 10 | 0 (0.00%) | 0.6000 | 1.0000 | 1.0000 | 1.0000 | 0.7833 |
| **`fixed_300w_50o_v1`** | **Overall Answerable** | **30** | **4 (13.33%)** | **0.5333** | **0.8333** | **0.8667** | **0.8667** | **0.6844** |
| | English (`EN`) | 10 | 0 (0.00%) | 0.6000 | 1.0000 | 1.0000 | 1.0000 | 0.8000 |
| | Urdu (`UR`) | 10 | 4 (40.00%) | 0.4000 | 0.5000 | 0.6000 | 0.6000 | 0.4700 |
| | Roman Urdu (`RU`) | 10 | 0 (0.00%) | 0.6000 | 1.0000 | 1.0000 | 1.0000 | 0.7833 |
| **`page_aware_300w_50o_v1`** | **Overall Answerable** | **30** | **4 (13.33%)** | **0.5333** | **0.8333** | **0.8667** | **0.8667** | **0.6789** |
| | English (`EN`) | 10 | 0 (0.00%) | 0.6000 | 1.0000 | 1.0000 | 1.0000 | 0.7833 |
| | Urdu (`UR`) | 10 | 4 (40.00%) | 0.3000 | 0.5000 | 0.6000 | 0.6000 | 0.4200 |
| | Roman Urdu (`RU`) | 10 | 0 (0.00%) | 0.7000 | 1.0000 | 1.0000 | 1.0000 | 0.8333 |

---

## 6. Concept-Aligned First Relevant Rank Comparison

The table below shows the 1-based rank of the first relevant chunk (`score > 0.0`) retrieved for each answerable concept across English, Urdu, and Roman Urdu query variants:

| Concept ID | Language | `page_v1` Rank | `fixed_300w_50o_v1` Rank | `page_aware_300w_50o_v1` Rank |
| :--- | :--- | :--- | :--- | :--- |
| `DIGITAL_BANK_MINIMUM_CAPITAL_001` | EN / UR / RU | 1 / 1 / 1 | 1 / 1 / 1 | 1 / 1 / 1 |
| `DIGITAL_BANK_CAR_REQUIREMENT_001` | EN / UR / RU | 1 / 1 / 1 | 1 / 1 / 1 | 1 / 1 / 1 |
| `DIGITAL_BANK_PILOT_DEPOSIT_CAP_001` | EN / UR / RU | 1 / 1 / 1 | 1 / 1 / 1 | 1 / 1 / 1 |
| `CUSTOMER_ONBOARDING_STANDARDIZED_FORM_001` | EN / UR / RU | 1 / null / 1 | 2 / null / 2 | 2 / null / 1 |
| `CUSTOMER_ONBOARDING_FICTITIOUS_ACCOUNTS_001`| EN / UR / RU | 1 / null / 1 | 1 / null / 1 | 1 / null / 1 |
| `ASAAN_ACCOUNT_CREDIT_BALANCE_LIMIT_001` | EN / UR / RU | 1 / null / 1 | 1 / null / 1 | 1 / null / 1 |
| `DIGITAL_ONBOARDING_NON_RESIDENTS_001` | EN / UR / RU | 2 / 1 / 2 | 2 / 1 / 2 | 2 / 1 / 1 |
| `THIRD_PARTY_KYC_RELIANCE_ROSHAN_DIGITAL_001`| EN / UR / RU | 1 / 2 / 1 | 1 / 4 / 1 | 1 / 4 / 1 |
| `CONSUMER_COMPLAINT_MAJOR_TAT_001` | EN / UR / RU | 2 / null / 2 | 2 / null / 2 | 2 / null / 2 |
| `KEY_FACT_STATEMENT_REQUIREMENT_001` | EN / UR / RU | 1 / 1 / 1 | 1 / 1 / 1 | 1 / 1 / 1 |

*Note: `null` indicates no relevant chunk with `score > 0.0` appeared in top-10 results.*

---

## 7. Observations on Unanswerable Queries

For the 6 corpus-unanswerable queries (2 concepts: `CRYPTO_CURRENCY_TRADING_FRAMEWORK_001` and `MICROFINANCE_MAXIMUM_INTEREST_CAP_001`):
- BM25 retrieved chunks with positive scores when English keywords (e.g. `trading`, `microfinance`, `interest`, `framework`) overlapped with general banking text.
- Because no abstention or hallucination-detection mechanism is present in this baseline phase, BM25 operates purely as a lexical matcher. Unanswerable queries have no relevant chunks (`expected_document_ids = []`, `relevant_pages = []`).

---

## 8. Empirical Findings & Disciplined Interpretation

1. **English Performance**: High lexical retrieval fidelity (Hit@3/5/10 = 100.0%, MRR@10 = 0.7833 - 0.8500). English queries share direct vocabulary with the English SBP source material.
2. **Roman Urdu Performance**: Remarkably competitive with English (Hit@3/5/10 = 100.0%, MRR@10 = 0.7833 - 0.8333). Roman Urdu queries naturally contain financial loanwords and acronyms (e.g., `Digital Retail Bank`, `Asaan Account`, `CNIC`, `Roshan Digital Account`, `Key Fact Statement`), providing sufficient lexical anchors for BM25.
3. **Urdu Performance**: Suffers a substantial cross-lingual gap due to script mismatch (40.0% zero-overlap rate, Hit@10 = 60.0%, MRR@10 = 0.4200 - 0.4700). Purely Arabic-script Urdu queries without embedded English acronyms fail to retrieve English-medium passages lexically.
4. **Chunking Strategy Impact**: `page_v1` achieved the highest MRR@10 (0.7000 overall, 0.8500 English) compared to windowed strategies (`fixed_300w_50o_v1`: 0.6844; `page_aware_300w_50o_v1`: 0.6789), as full page contexts retain broader lexical vocabulary per chunk.

> [!WARNING]
> These findings reflect a **pilot baseline experiment** on a 30-answerable query benchmark and 4 SBP documents. They establish an empirical baseline for future dense and hybrid retrieval comparisons, but do not represent statistical claims across all financial literature.

---

## 9. Result Artifact Hashing & Reproducibility

Dual experiment runs produced 100% byte-identical artifact hashes:

- `research/results/bm25/bm25_summary.json`: `5ab4329a529348ace7ca0ec8a47ad7d863c11478edad67f86758e157fe6feac3`
- `research/results/bm25/bm25_query_results.jsonl`: `55eebe2b50f29901625dd6d2d26ddb1280922781e522572b999c02ebe4cfd594`
