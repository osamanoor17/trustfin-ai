# TrustFin AI: Document Acquisition & Governance Plan

> **Plan Version:** 1.0.1 (Phase 1B.1 Consistency Revision)  
> **Status:** Approved Operational Protocol  
> **Focus:** Acquisition Pipeline, Verification Standards, Provenance Capture, and Manifest Protocols  

---

## 1. Overview & Acquisition Objectives

The **Document Acquisition Plan** defines the operational procedure for collecting primary financial, regulatory, and institutional documents for **TrustFin AI**. 

### Primary Objectives
- **Strict Provenance Guarantee:** Every acquired document must be directly linked to a verified official publisher URL and cryptographically hashed upon download.
- **Controlled Pilot Target (Corpus v0.1):** Maintain a conservative, high-quality pilot corpus target of **20–40 carefully selected documents** rather than collecting hundreds of unvetted files.
- **Domain & Category Diversity:** Prioritize category coverage (e.g., prudential regulations, circulars, digital banking policy, consumer fee schedules) across Tier-1 regulators and Tier-2 institutions over duplicate document types.
- **Reproducible Pipeline:** Ensure any researcher can audit, verify, and re-create the exact dataset manifest using deterministic hashing and immutable metadata records.

---

## 2. Pipeline Lifecycle Stages

The acquisition workflow enforces strict separation between execution stages:

```
  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │  DISCOVERY   │ ──► │ VERIFICATION │ ──► │ ACQUISITION  │
  └──────────────┘     └──────────────┘     └──────────────┘
                                                   │
  ┌──────────────┐     ┌──────────────┐            ▼
  │   MANIFEST   │ ◄── │   METADATA   │ ◄── ┌──────────────┐
  └──────────────┘     └──────────────┘     │   HASHING    │
                                            └──────────────┘
```

1. **DISCOVERY:** Identify candidate document links from registered official domains matching target categories.
2. **VERIFICATION:** Validate source authority, HTTP accessibility, SSL integrity, mime-type (`application/pdf`), and relevance before downloading.
3. **ACQUISITION:** Fetch raw PDF binaries using rate-limited, polite HTTP request routines into ignored `data/raw/` storage.
4. **HASHING:** Compute SHA-256 digests immediately upon download to guarantee file integrity and catch byte-level corruption or duplicates.
5. **METADATA:** Extract and validate core document attributes conforming strictly to `DocumentMetadata` Pydantic schemas.
6. **MANIFEST:** Append verified document records to immutable, deterministic JSONL manifest logs (`data/manifest/corpus_manifest.jsonl`).

---

## 3. Pilot Corpus v0.1 Design Target

> [!NOTE]
> The numbers below represent a **design target** for initial empirical research, **not** a count of already collected files. Document downloading has not commenced.

### Proposed Distribution (20–40 Total Documents)

| Category Tier | Target Document Category | Target Count | Primary Candidate Sources | Focus Area |
|---|---|---|---|---|
| **Tier 1 (`TIER_1`)** | `PRUDENTIAL_REGULATION` | 5 – 8 | State Bank of Pakistan (`SBP`) | Capital adequacy, risk management, corporate governance. |
| **Tier 1 (`TIER_1`)** | `CIRCULAR` | 5 – 8 | State Bank of Pakistan (`SBP`) | Branchless banking, consumer protection, payment systems directives. |
| **Tier 1 (`TIER_1`)** | `DIGITAL_BANKING_POLICY` | 3 – 5 | State Bank of Pakistan (`SBP`), `SECP` | EMI regulations, digital bank licensing frameworks, fintech sandbox. |
| **Tier 1 (`TIER_1`)** | `AML_KYC_GUIDANCE` | 2 – 4 | State Bank of Pakistan (`SBP`), `SECP` | Anti-money laundering, customer due diligence, biometric verification rules. |
| **Tier 2 (`TIER_2`)** | `FEE_SCHEDULE` | 3 – 5 | `HBL`, `MEEZAN`, `MCB` | Schedules of Bank Charges (SOC), debit card tariffs, account fee tables. |
| **Tier 2 (`TIER_2`)** | `TERMS_AND_CONDITIONS` | 2 – 4 | `EASYPAISA`, `JAZZCASH`, `NAYAPAY` | Digital wallet account opening, transfer limits, consumer terms. |
| **Tier 1 / Tier 3** | `CONSUMER_GUIDANCE` | 2 – 4 | `SBP`, `WORLDBANK` | Financial literacy advisories, fair treatment of customers, fraud prevention. |
| **Total Target** | — | **22 – 38** | — | **High-diversity, multi-category pilot corpus** |

---

## 4. Acquisition Status Lifecycle

To track candidate documents without database dependencies, each record transitions through defined string status states:

| Status Code | Description & Entrance Criteria |
|---|---|
| **`DISCOVERED`** | Candidate document URL identified from an official registry domain during web discovery. |
| **`VERIFIED`** | URL validated for official domain alignment, HTTP 200 availability, and valid PDF mime-type (`application/pdf`). |
| **`DOWNLOADED`** | Raw binary successfully fetched and saved to local raw storage (`data/raw/`). |
| **`HASHED`** | SHA-256 cryptographic digest computed; verified against existing corpus digests to prevent duplicates. |
| **`METADATA_COMPLETE`** | Full Pydantic `DocumentMetadata` record constructed, validated against schema rules, and formatted. |
| **`REJECTED`** | Document failed verification, contained unreadable/corrupted binary, matched duplicate hash, or violated inclusion criteria. |

---

## 5. Standard Operating Procedures (SOP)

### 5.1 Source Verification Procedure
1. Verify the host domain resolves to an authorized candidate domain in `research/source_registry.md`.
2. Inspect HTTP headers: status must be `200 OK`, `Content-Type` must be `application/pdf` or `application/octet-stream` with valid PDF headers.
3. Confirm document contains no privacy violations, confidential PII, or non-public internal correspondence.

### 5.2 Document Selection Procedure
1. Evaluate candidate file against target category balance (Section 3).
2. Reject exact copies or minor formatting variants of existing circulars unless issued as formal amendments.
3. Prefer canonical primary PDF releases over HTML summaries or third-party web posts.

### 5.3 Provenance Capture Procedure
At the time of acquisition, scripts must capture:
- `source_url`: Full direct URL from which the binary was retrieved.
- `retrieval_timestamp`: UTC ISO-8601 timestamp (`YYYY-MM-DDTHH:MM:SSZ`).
- `publisher_institution`: Formal name and abbreviation of publishing authority.
- `http_etag` / `last_modified`: HTTP headers provided by host server (if present).

### 5.4 Download Procedure
- Execute requests with polite user-agent headers identifying `TrustFinAI-Research-Bot/0.1`.
- Enforce rate-limiting (minimum 2.0 seconds delay between requests to the same host domain).
- Store raw files directly in `data/raw/{document_id}.pdf`.

### 5.5 SHA-256 Integrity Procedure
- Read binary stream in 64 KB blocks and compute SHA-256 hex digest (64 lowercase hexadecimal characters).
- If hash matches an existing manifest entry, abort ingestion and mark state as `REJECTED (DUPLICATE_HASH)`.
- Store `sha256_hex` in `DocumentMetadata`.

### 5.6 Duplicate Handling
- **Byte Duplicates:** Automatically rejected based on SHA-256 collisions.
- **Version Duplicates:** If a circular or regulation is revised, assign a distinct `version` suffix (e.g., `_V2`) and record the superseded document ID in metadata notes.

### 5.7 Filename Normalization
Raw downloads must be renamed according to the standardized convention:
```
{country_code}_{institution_abbr}_{category}_{year}_{sequence}.pdf
```
*Example:* `PK_SBP_PRUDENTIAL_REGULATION_2023_001.pdf`

### 5.8 Document ID Assignment
Each document receives an immutable, globally unique string key matching the normalized filename without extension:
`PK_SBP_PRUDENTIAL_REGULATION_2023_001`

### 5.9 Manifest Creation Procedure
- Validated metadata records are written sequentially as JSON lines (`.jsonl`) to `data/manifest/corpus_manifest.jsonl`.
- Manifest updates are append-only to preserve auditability.

### 5.10 Failure Handling
- **HTTP 404 / 5xx Errors:** Log failure, set acquisition status to `REJECTED`, record HTTP status code in selection log.
- **Corrupted PDF Binary:** Validate initial 4 bytes match `%PDF`. If invalid, delete local binary, log error, mark `REJECTED`.
- **Timeout / Network Disruption:** Retry up to 3 times with exponential backoff (2s, 4s, 8s). If persistent, flag for manual review.

### 5.11 Reproducibility Procedure
- Manifest files (`corpus_manifest.jsonl`) and selection logs are checked into source control (without the raw binary files in `data/raw/`).
- Automated verification scripts can re-download target URLs, verify SHA-256 digests against manifest records, and confirm zero-drift reproducibility.
