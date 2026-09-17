# TrustFin AI: SBP Controlled Document Acquisition & Semantic Identity Report (Phase 1B.3 & Recovery Pass)

> **Document Version:** 1.2.0 (Controlled Official-Link Recovery Pass Revision)  
> **Acquisition & Recovery Date:** 2026-09-17  
> **Status:** Pilot Document Acquisition & Recovery Pass Complete  
> **Target Institution:** State Bank of Pakistan (`SBP`) — Central Bank Regulator (`TIER_1`)  
> **Candidate Manifest:** [`data/manifest/sbp_discovery_candidates.jsonl`](file:///d:/trustfin-ai/data/manifest/sbp_discovery_candidates.jsonl)  
> **Acquisition Manifest:** [`data/manifest/sbp_acquisition_manifest.jsonl`](file:///d:/trustfin-ai/data/manifest/sbp_acquisition_manifest.jsonl)  
> **Raw Storage Directory:** `data/raw/sbp/` (Git-ignored)  

---

> [!IMPORTANT]
> **ACQUISITION & PROVENANCE BOUNDARY DISCLAIMER:**  
> Phase 1B.3 executes controlled HTTP binary retrieval, SHA-256 integrity hashing, two-stage semantic document identity verification, and raw PDF storage. Transport success (HTTP 200, allowed domain, `%PDF-` magic bytes, SHA-256 hash) does **NOT** constitute trusted ingestion until document identity is verified against PDF metadata and decompressed stream text. No OCR, text extraction pipelines, embeddings, or RAG systems have been introduced.

---

## 1. Overview & Semantic Verification Objectives

Following initial pilot HTTP acquisition in Phase 1B.3, a **Controlled Official-Link Recovery Pass** was conducted across all failed candidates.

Recovery attempts strictly adhered to provenance rules: starting exclusively from official SBP landing pages (`https://www.sbp.org.pk/bprd/2022/C1.htm`, `https://www.sbp.org.pk/bprd/2025/C1.htm`, etc.) and resolving explicit document download links embedded within the HTML source. No third-party hosts, mirrors, or guessed URLs were utilized.

Every recovered document passed the strict two-stage pipeline:
1. **Stage 1: Binary Validation (`BINARY_VALIDATED`)** — HTTP status 200, approved SBP domain allowlist (`sbp.org.pk`), `%PDF-` magic bytes, non-zero file size, SHA-256 digest computation.
2. **Stage 2: Semantic Identity Verification (`IDENTITY_VERIFIED` / `ACQUIRED`)** — Inspection of PDF Info dictionary metadata (Title, Subject, Author) and stream headers to confirm matching regulatory identity.

---

## 2. Selected Pilot Acquisition Batch

Six candidate documents from `data/manifest/sbp_discovery_candidates.jsonl` were evaluated across 5 functional categories:

| Candidate Document ID | Title | Category | Selection Rationale |
|---|---|---|---|
| `PK-SBP-DIGITAL_BANKING_POLICY-2022-0001` | Licensing and Regulatory Framework for Digital Banks | `DIGITAL_BANKING_POLICY` | Baseline 2022 digital banking framework |
| `PK-SBP-AML_KYC_GUIDANCE-2025-0001` | Consolidated Customer Onboarding Framework | `AML_KYC_GUIDANCE` | Original 2025 consolidated onboarding rules |
| `PK-SBP-AML_KYC_GUIDANCE-2026-0001` | Amendments to Consolidated Customer Onboarding Framework (RDA Scope) | `AML_KYC_GUIDANCE` | 2026 regulatory amendment (temporal pair) |
| `PK-SBP-CONSUMER_GUIDANCE-2025-0001` | Business Conduct & Fair Treatment of Consumers (BC&FRF) | `CONSUMER_GUIDANCE` | Comprehensive consumer protection rules |
| `PK-SBP-FINTECH_REGULATION-2025-0001` | Guidelines for Regulatory Sandbox | `FINTECH_REGULATION` | Final regulatory sandbox framework |
| `PK-SBP-PAYMENT_SYSTEM_REPORT-2025-0001` | Annual Payment Systems Review FY25 | `PAYMENT_SYSTEM_REPORT` | Statutory annual payment report |

---

## 3. Controlled Recovery Pass Results

### 3.1 Candidate 1: Licensing and Regulatory Framework for Digital Banks
* **Document ID:** `PK-SBP-DIGITAL_BANKING_POLICY-2022-0001`
* **Original Failure:** `FAILED_HTTP 404` (Legacy URL `https://www.sbp.org.pk/circulars/bprd-circular-no-01-of-2022.pdf` returned 404).
* **Official Landing Page Inspected:** `https://www.sbp.org.pk/bprd/2022/C1.htm`
* **Explicit Document URL Resolved:** `https://www.sbp.org.pk/assets/documents/circulars/BPRD-2022-C1-Annex.pdf`
* **HTTP Result:** `200 OK` (`Content-Type: application/pdf`)
* **Binary Validation:** Passed (`%PDF-` magic bytes verified, non-empty)
* **Semantic Identity Evidence:** PDF Author metadata: `Nadeem - Joint Director BPRD-SBP`; stream text contains `Licensing and Regulatory Framework for Digital Banks`, `Banking Policy and Regulations Department`, `State Bank of Pakistan`.
* **Final Acquisition Status:** **`ACQUIRED`** (`IDENTITY_VERIFIED`)
* **File Size:** `927,792 bytes` (`906.0 KB`)
* **SHA-256 Digest:** `517071f7b6e5c0a79d52c4a36f935fac7b85a543a8fe069eb46291a7c39cf282`
* **Local Raw Storage Path:** [`data/raw/sbp/bprd-circular-no-01-of-2022.pdf`](file:///d:/trustfin-ai/data/raw/sbp/bprd-circular-no-01-of-2022.pdf)

---

### 3.2 Candidate 2: Consolidated Customer Onboarding Framework (2025 Base)
* **Document ID:** `PK-SBP-AML_KYC_GUIDANCE-2025-0001`
* **Original Failure:** `FAILED_NOT_PDF` (Legacy target path returned server HTML page).
* **Official Landing Page Inspected:** `https://www.sbp.org.pk/bprd/2025/C1.htm`
* **Explicit Document URL Resolved:** `https://www.sbp.org.pk/assets/documents/circulars/C1-Consolidated-Customer-Onboarding-Framework_1.pdf`
* **HTTP Result:** `200 OK` (`Content-Type: application/pdf`)
* **Binary Validation:** Passed (`%PDF-` magic bytes verified, non-empty)
* **Semantic Identity Evidence:** PDF Author metadata: `Shahzeb Saleem Shaikh - BPRD`; stream text contains `Contents`, `Preamble`, `Consolidated Customer Onboarding Framework`.
* **Final Acquisition Status:** **`ACQUIRED`** (`IDENTITY_VERIFIED`)
* **File Size:** `1,169,288 bytes` (`1.11 MB`)
* **SHA-256 Digest:** `7a97a04ed2dfe03574693b0b7161a75ffd88762e572d5a909645309d77c144e2`
* **Local Raw Storage Path:** [`data/raw/sbp/bprd-circular-no-01-of-2025.pdf`](file:///d:/trustfin-ai/data/raw/sbp/bprd-circular-no-01-of-2025.pdf)

---

### 3.3 Candidate 3: Amendments to Consolidated Customer Onboarding Framework (2026 Amendment)
* **Document ID:** `PK-SBP-AML_KYC_GUIDANCE-2026-0001`
* **Original Status:** `ACQUIRED` in Phase 1B.3
* **Official Landing Page Inspected:** `https://www.sbp.org.pk/bprd/2026/CL9.htm`
* **Explicit Document URL Resolved:** `https://www.sbp.org.pk/assets/documents/circulars/BPRD-2026-CL9-Annex.pdf`
* **HTTP Result:** `200 OK` (`Content-Type: application/pdf`)
* **Binary Validation:** Passed (`%PDF-` magic bytes verified, non-empty)
* **Semantic Identity Evidence:** PDF Author metadata: `Shahzeb Saleem Shaikh BPRD`; stream text specifies Roshan Digital Account (RDA) onboarding amendments under BPRD Circular Letter No. 09 of 2026.
* **Final Acquisition Status:** **`ACQUIRED`** (`IDENTITY_VERIFIED`)
* **File Size:** `530,667 bytes` (`518.2 KB`)
* **SHA-256 Digest:** `612b13059f31307d61c97e9fa77efab88bdca41030b0860c9422ad731ce5f831`
* **Local Raw Storage Path:** [`data/raw/sbp/bprd-circular-letter-no-09-of-2026.pdf`](file:///d:/trustfin-ai/data/raw/sbp/bprd-circular-letter-no-09-of-2026.pdf)

---

### 3.4 Candidate 4: Business Conduct & Fair Treatment of Consumers (BC&FRF)
* **Document ID:** `PK-SBP-CONSUMER_GUIDANCE-2025-0001`
* **Original Failure:** `FAILED_NOT_PDF` (Legacy target path returned server HTML page).
* **Official Landing Page Inspected:** `https://www.sbp.org.pk/bprd/2025/C4.htm`
* **Explicit Document URL Resolved:** `https://www.sbp.org.pk/assets/documents/circulars/BPRD-2025-C4-BCFRF.pdf`
* **HTTP Result:** `200 OK` (`Content-Type: application/pdf`)
* **Binary Validation:** Passed (`%PDF-` magic bytes verified, non-empty)
* **Semantic Identity Evidence:** Decompressed stream text contains `BUSINESS CONDUCT`, `FAIR TREATMENT OF CONSUMERS`, `REGULATORY FRAMEWORK`, `(BC&FRF)`.
* **Final Acquisition Status:** **`ACQUIRED`** (`IDENTITY_VERIFIED`)
* **File Size:** `1,018,301 bytes` (`994.4 KB`)
* **SHA-256 Digest:** `be83d985669417d97dfb16718d44d9686c157bf6fd920111f3ef0e44380a092c`
* **Local Raw Storage Path:** [`data/raw/sbp/bprd-circular-no-04-of-2025.pdf`](file:///d:/trustfin-ai/data/raw/sbp/bprd-circular-no-04-of-2025.pdf)

---

### 3.5 Candidate 5: Annual Payment Systems Review FY25
* **Document ID:** `PK-SBP-PAYMENT_SYSTEM_REPORT-2025-0001`
* **Original Failure:** `FAILED_NOT_PDF` (HTML page returned).
* **Official Landing Page Inspected:** `https://www.sbp.org.pk/PS/index.html`
* **Explicit Document URL Resolved:** `https://www.sbp.org.pk/assets/documents/press-release/PR-14-Sep-2026.pdf`
* **HTTP Result:** `200 OK` (`application/pdf`)
* **Binary Validation:** Passed (`%PDF-` magic bytes verified)
* **Semantic Identity Evidence:** Decompressed text contains `Monetary Policy Committee Statement - September 14, 2026`, **NOT** Payment Systems Review.
* **Final Acquisition Status:** **`FAILED_DOCUMENT_IDENTITY`** (`SEMANTIC MISMATCH`)
* **Raw File Action:** File deleted/quarantined from raw storage.

---

### 3.6 Candidate 6: Guidelines for Regulatory Sandbox
* **Document ID:** `PK-SBP-FINTECH_REGULATION-2025-0001`
* **Original Failure:** `FAILED_DOCUMENT_IDENTITY` (Resolved `NPSS.pdf` was National Payment Systems Strategy).
* **Official Landing Page Inspected:** `https://www.sbp.org.pk/dfs/RSB.html`
* **Explicit Document URL Resolved:** `https://www.sbp.org.pk/assets/document/NPSS.pdf`
* **HTTP Result:** `200 OK` (`application/pdf`)
* **Binary Validation:** Passed (`%PDF-` magic bytes verified)
* **Semantic Identity Evidence:** PDF metadata Title=`National Payment Systems Strategy`, Subject=`NPSS`, Author=`Lois Estelle Quinn`.
* **Final Acquisition Status:** **`FAILED_DOCUMENT_IDENTITY`** (`SEMANTIC MISMATCH`)
* **Raw File Action:** File deleted/quarantined from raw storage.

---

## 4. Final Trusted Corpus Summary

Following the Recovery Pass and Stage 2 Semantic Identity Verification, the active raw corpus in `data/raw/sbp/` consists of **4 identity-verified statutory regulatory frameworks**:

```
Total Pilot Candidates Evaluated:  6
Identity-Verified & Acquired:      4 (66.7%)
Semantic Document Mismatches:      2 (33.3%)
Unverified / Corrupted Files:      0 (0.0%)
```

### Active Raw Corpus Inventory (`data/raw/sbp/`)

```text
data/raw/sbp/
├── bprd-circular-no-01-of-2022.pdf  (927,792 bytes | SHA-256: 517071f7...)
├── bprd-circular-no-01-of-2025.pdf  (1,169,288 bytes | SHA-256: 7a97a04e...)
├── bprd-circular-letter-no-09-of-2026.pdf  (530,667 bytes | SHA-256: 612b1305...)
└── bprd-circular-no-04-of-2025.pdf  (1,018,301 bytes | SHA-256: be83d985...)
```

---

## 5. Reproducibility & Pipeline Verification

```bash
# Run acquisition pipeline with recovery pass & semantic identity verification
python scripts/acquire_documents.py

# Run automated unit tests
pytest -v tests/test_acquire_documents.py
```
