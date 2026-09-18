# TrustFin AI: SBP Document Parsing & Normalization Quality Report (Phase 1C)

> **Document Version:** 1.0.0  
> **Execution Date:** 2026-09-18  
> **Status:** Phase 1C Ingestion & Normalization Complete  
> **Target Institution:** State Bank of Pakistan (`SBP`) — Central Bank Regulator (`TIER_1`)  
> **Processed Corpus Path:** [`data/processed/sbp/sbp_pages.jsonl`](file:///d:/trustfin-ai/data/processed/sbp/sbp_pages.jsonl) (Git-ignored)  
> **Processed Manifest Path:** [`data/manifest/sbp_processed_manifest.jsonl`](file:///d:/trustfin-ai/data/manifest/sbp_processed_manifest.jsonl)  

---

> [!IMPORTANT]
> **INGESTION BOUNDARY DISCLAIMER:**  
> Phase 1C converts trusted, identity-verified raw SBP PDFs into a clean, page-aware JSONL corpus. Text extraction is strictly deterministic and conservative. No chunking, vector database creation, BM25 indexing, embeddings, RAG operations, OCR, or LLM transformations have been performed. Raw PDFs remain immutable in `data/raw/sbp/`.

---

## 1. Corpus Ingestion Summary

The pilot corpus comprises 4 identity-verified statutory regulatory frameworks issued by the State Bank of Pakistan (SBP):

| Document ID | Source Filename | Total Pages | Extracted Pages | Empty Pages | Low-Text Pages | OCR Review Pages | Table-Like Pages | Total Extracted Characters | Status |
|---|---|---|---|---|---|---|---|---|---|
| `PK-SBP-AML_KYC_GUIDANCE-2025-0001` | `bprd-circular-no-01-of-2025.pdf` | 21 | 21 | 0 | 1 | 0 | 13 | 45,942 | `PROCESSED_SUCCESSFULLY` |
| `PK-SBP-AML_KYC_GUIDANCE-2026-0001` | `bprd-circular-letter-no-09-of-2026.pdf` | 2 | 2 | 0 | 0 | 0 | 2 | 3,456 | `PROCESSED_SUCCESSFULLY` |
| `PK-SBP-CONSUMER_GUIDANCE-2025-0001` | `bprd-circular-no-04-of-2025.pdf` | 77 | 77 | 0 | 0 | 0 | 22 | 183,705 | `PROCESSED_SUCCESSFULLY` |
| `PK-SBP-DIGITAL_BANKING_POLICY-2022-0001` | `bprd-circular-no-01-of-2022.pdf` | 42 | 42 | 0 | 0 | 0 | 5 | 97,925 | `PROCESSED_SUCCESSFULLY` |
| **CORPUS TOTALS** | **4 Documents** | **142** | **142** | **0** | **1** | **0** | **42** | **331,028** | **100% SUCCESS** |

---

## 2. Document-by-Document Ingestion Detail

### 2.1 Licensing and Regulatory Framework for Digital Banks (2022)
* **Document ID:** `PK-SBP-DIGITAL_BANKING_POLICY-2022-0001`
* **Raw Filename:** `bprd-circular-no-01-of-2022.pdf`
* **SHA-256 Digest:** `517071f7b6e5c0a79d52c4a36f935fac7b85a543a8fe069eb46291a7c39cf282`
* **Page Count:** 42 pages (100% extracted)
* **Character Count:** 97,925 characters (14,484 words)
* **Table-Like Pages:** 5 pages (e.g. minimum capital requirement progression tables)
* **Low-Text / Empty Pages:** 0 pages
* **Notable Extraction Characteristics:** Includes page numbering header `Page X of 42` across content pages. High text density, clean formatting, complete preservation of mathematical symbols, capital amounts (PKR / USD), and witness signature blocks on page 42.

### 2.2 Consolidated Customer Onboarding Framework (2025 Base)
* **Document ID:** `PK-SBP-AML_KYC_GUIDANCE-2025-0001`
* **Raw Filename:** `bprd-circular-no-01-of-2025.pdf`
* **SHA-256 Digest:** `7a97a04ed2dfe03574693b0b7161a75ffd88762e572d5a909645309d77c144e2`
* **Page Count:** 21 pages (100% extracted)
* **Character Count:** 45,942 characters (6,634 words)
* **Table-Like Pages:** 13 pages (includes standardized account opening forms and transaction limit tables)
* **Low-Text / Empty Pages:** 1 page (Page 1 cover title page containing 42 characters)
* **Notable Extraction Characteristics:** High proportion of multi-column tabular data (Annex A & B forms). Bullet point symbols (`•`, `\uf0b7`) and placeholders (`XXX-XXX-XXX`) preserved intact.

### 2.3 Amendments to Consolidated Customer Onboarding Framework (2026 Amendment)
* **Document ID:** `PK-SBP-AML_KYC_GUIDANCE-2026-0001`
* **Raw Filename:** `bprd-circular-letter-no-09-of-2026.pdf`
* **SHA-256 Digest:** `612b13059f31307d61c97e9fa77efab88bdca41030b0860c9422ad731ce5f831`
* **Page Count:** 2 pages (100% extracted)
* **Character Count:** 3,456 characters (516 words)
* **Table-Like Pages:** 2 pages (both pages consist of regulatory comparison tables: Ref / Existing Provision / Updated Provision)
* **Low-Text / Empty Pages:** 0 pages
* **Notable Extraction Characteristics:** Explicit regulatory amendment delta table. Preserves references to foreign exchange manual provisions (`para 8A(i) of chapter 8 of FE Manual`).

### 2.4 Business Conduct and Fair Treatment of Consumers Regulatory Framework (BC&FRF)
* **Document ID:** `PK-SBP-CONSUMER_GUIDANCE-2025-0001`
* **Raw Filename:** `bprd-circular-no-04-of-2025.pdf`
* **SHA-256 Digest:** `be83d985669417d97dfb16718d44d9686c157bf6fd920111f3ef0e44380a092c`
* **Page Count:** 77 pages (100% extracted)
* **Character Count:** 183,705 characters (26,584 words)
* **Table-Like Pages:** 22 pages (includes FTC governance matrices, disclosure forms, and training statistics)
* **Low-Text / Empty Pages:** 0 pages
* **Notable Extraction Characteristics:** Largest document in the pilot batch. Features extensive Roman numerals (i, ii, iii, iv) and sub-clause enumerations. Page headers include department designation `BANKING CONDUCT POLICY DIVISION (BCPD)`.

---

## 3. Pre & Post-Ingestion Source Integrity Verification

To guarantee that the raw source corpus remains immutable and untouched during extraction, SHA-256 cryptographic digests were computed immediately prior to parsing and recomputed following corpus generation:

| Document ID | Target PDF Path | SHA-256 (Pre-Parse) | SHA-256 (Post-Parse) | Integrity Match |
|---|---|---|---|---|
| `PK-SBP-AML_KYC_GUIDANCE-2026-0001` | `data/raw/sbp/bprd-circular-letter-no-09-of-2026.pdf` | `612b13059f31307d61c97e9fa77efab88bdca41030b0860c9422ad731ce5f831` | `612b13059f31307d61c97e9fa77efab88bdca41030b0860c9422ad731ce5f831` | **MATCH** |
| `PK-SBP-DIGITAL_BANKING_POLICY-2022-0001` | `data/raw/sbp/bprd-circular-no-01-of-2022.pdf` | `517071f7b6e5c0a79d52c4a36f935fac7b85a543a8fe069eb46291a7c39cf282` | `517071f7b6e5c0a79d52c4a36f935fac7b85a543a8fe069eb46291a7c39cf282` | **MATCH** |
| `PK-SBP-AML_KYC_GUIDANCE-2025-0001` | `data/raw/sbp/bprd-circular-no-01-of-2025.pdf` | `7a97a04ed2dfe03574693b0b7161a75ffd88762e572d5a909645309d77c144e2` | `7a97a04ed2dfe03574693b0b7161a75ffd88762e572d5a909645309d77c144e2` | **MATCH** |
| `PK-SBP-CONSUMER_GUIDANCE-2025-0001` | `data/raw/sbp/bprd-circular-no-04-of-2025.pdf` | `be83d985669417d97dfb16718d44d9686c157bf6fd920111f3ef0e44380a092c` | `be83d985669417d97dfb16718d44d9686c157bf6fd920111f3ef0e44380a092c` | **MATCH** |

---

## 4. Header / Footer Observation Notes

Repeated text elements observed across pages include:
1. **Running Page Identifiers**: e.g., `Page 22 of 42` or `Page 15` centered or right-aligned.
2. **Regulatory Authority Headers**: e.g., `State Bank of Pakistan`, `Banking Policy & Regulations Department`, `Banking Conduct Policy Division (BCPD)`.
3. **Circular Identifiers**: e.g., `BPRD Circular No. 01 of 2022`, `BPRD Circular No. 04 of 2025`.

**Policy Decision:** All repeated headers and footers have been **preserved** in `normalized_text`. In legal and regulatory domains, running headers often carry essential context (such as circular number, issue date, or department) that anchors isolated excerpts.

---

## 5. Implications for Future Retrieval

Based on observed extraction properties of the SBP pilot corpus, future indexing and retrieval stages (Phase 2) should account for the following structural characteristics:

1. **Page Provenance Anchoring**:
   - Each page record explicitly ties `document_id`, `source_sha256`, `source_file_name`, and 1-based `page_number`. This provides an unambiguous audit trail for citations back to official SBP circulars.

2. **Table Layout Interleaving & Observational Signals**:
   - 42 pages were flagged as containing table-like content by the non-destructive PyMuPDF-based signal; these flags are observational and have not yet been evaluated as a table-detection benchmark.
   - In raw text streams, table cells appear as space-separated tokens across lines. When chunking algorithms are designed in future phases, table-aware boundaries will be necessary to prevent splitting numeric columns from their headers.

3. **Low-Text & Cover Pages**:
   - 1 page (`PK-SBP-AML_KYC_GUIDANCE-2025-0001` Page 1) contains < 50 characters (cover title).
   - Filtering out low-text pages from vector indexing (or treating cover pages with special document-level metadata) will prevent noisy vector embeddings.

4. **Multi-level Enumeration & Bullet Hierarchies**:
   - SBP frameworks rely heavily on nested clauses (e.g., `Section C -> Para 5 -> Clause (a) -> Sub-clause (i)`).
   - Preserving full line break context in normalized text ensures sub-clause boundaries remain identifiable during text chunking.

5. **Language & Script Observations**:
   - Automated synthetic normalization tests confirmed that Urdu-script and non-ASCII Unicode preservation functions correctly (`tests/test_parse_documents.py` PASSED).
   - In the actual 142-page English-medium SBP pilot corpus, Unicode and special-character preservation was empirically observed (e.g. `•`, `—`, `©`, `§`, `€`); actual Urdu-script text was **not observed** in these 4 regulatory PDFs. Urdu-script preservation is covered by automated unit tests and will require empirical validation on future Urdu-source documents.
