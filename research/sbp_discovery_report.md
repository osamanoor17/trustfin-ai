# TrustFin AI: SBP Candidate Document Discovery Report (Phase 1B.2)

> **Document Version:** 1.0.1 (Phase 1B.2 Provenance Correction Revision)  
> **Discovery Date:** 2026-09-17  
> **Status:** Candidate Discovery Inventory Compiled & Provenance Verified  
> **Target Institution:** State Bank of Pakistan (`SBP`) — Central Bank Regulator (`TIER_1`)  
> **Manifest File:** [`data/manifest/sbp_discovery_candidates.jsonl`](file:///d:/trustfin-ai/data/manifest/sbp_discovery_candidates.jsonl)  

---

> [!IMPORTANT]
> **DISCOVERY & SELECTION BOUNDARY DISCLAIMER:**  
> Candidate discovery does **NOT** mean the document has been ingested into Corpus v0.1. No raw PDF downloads, OCR parsing, text chunking, embedding generation, or vector database indexing have been performed. This milestone establishes a verified metadata inventory of candidate SBP documents for acquisition planning.

---

## 1. Overview & Purpose

Phase 1B.2 executes the first target discovery batch for the **TrustFin AI Corpus v0.1**. In alignment with the provenance principles defined in Phase 1A (`research/corpus_specification.md`) and the candidate source catalog established in Phase 1B.1 (`research/source_registry.md`), this pilot discovery batch focuses exclusively on Pakistan's central monetary authority: the **State Bank of Pakistan (SBP)**.

The objective of this phase is to curate a highly authoritative, diverse, and verified inventory of candidate SBP regulatory frameworks, circulars, prudential standards, and statistical reports to support empirical research in cross-lingual retrieval, financial reasoning, and regulatory question answering.

---

## 2. Official Entry Points Searched

Document discovery was conducted strictly via verified official State Bank of Pakistan web domains and statutory publication portals. Third-party aggregators, document hosting mirrors, Scribd, ResearchGate, and unverified blogs were strictly excluded.

| Entry Point Name | Canonical Official URL | Scope & Content Type |
|---|---|---|
| **SBP Main Portal** | `https://www.sbp.org.pk/` | Primary institutional portal & announcement gateway |
| **Laws & Regulations** | `https://www.sbp.org.pk/laws-regulations` | Statutory acts, frameworks, and master regulatory codes |
| **SBP Circulars** | `https://www.sbp.org.pk/circulars/` | Departmental circulars (BPRD, PSD, PSP&OD, EPD) |
| **Banking Regulation & Supervision** | `https://www.sbp.org.pk/our-operations/banking-regulation-and-supervision` | Prudential regulations and operational directives |
| **SBP Publications** | `https://www.sbp.org.pk/our-operations/publications` | Annual reports, payment reviews, stability reports, and statistics |
| **Monetary Policy Portal** | `https://www.sbp.org.pk/m_policy/index.asp` | Monetary Policy Committee (MPC) decisions and compendiums |
| **Prudential Regulations Index** | `https://www.sbp.org.pk/publications/prudential/index.html` | Master booklets for Corporate, SME, and Microfinance banking |
| **Payment Systems Portal** | `https://www.sbp.org.pk/PS/index.html` | Retail payment statistics, Raast reviews, and digital payment circulars |
| **Regulatory Sandbox Portal** | `https://www.sbp.org.pk/dfs/RSB.html` | Sandbox guidelines, cohort framework, and innovation hub announcements |
| **SBP Archive Domain** | `https://archive.sbp.org.pk/` | Historical regulatory circulars and archived publications |

---

## 3. Discovery Summary & Key Metrics

* **Total Candidate Documents Discovered:** `12`
* **Source Institution:** State Bank of Pakistan (`SBP`)
* **Institution Type:** `CENTRAL_BANK_REGULATOR`
* **Country Focus:** Pakistan (`PK`)
* **Source Tier:** Tier 1 (`TIER_1`)
* **Verified Official Domain Records:** `9` (`75.0%`)
* **Records Requiring Manual Document Verification:** `3` (`25.0%`)

---

## 4. Candidate Document Inventory

The table below summarizes the 12 candidate documents cataloged in [`data/manifest/sbp_discovery_candidates.jsonl`](file:///d:/trustfin-ai/data/manifest/sbp_discovery_candidates.jsonl).

| Document ID | Official Title | Category | Pub Date | Ref / Circular | Verification Status |
|---|---|---|---|---|---|
| `PK-SBP-DIGITAL_BANKING_POLICY-2022-0001` | Licensing and Regulatory Framework for Digital Banks | `DIGITAL_BANKING_POLICY` | 2022-01-03 | BPRD Circ. 01/2022 | `VERIFIED_OFFICIAL_DOMAIN` |
| `PK-SBP-AML_KYC_GUIDANCE-2025-0001` | Consolidated Customer Onboarding Framework | `AML_KYC_GUIDANCE` | 2025-07-25 | BPRD Circ. 01/2025 | `VERIFIED_OFFICIAL_DOMAIN` |
| `PK-SBP-AML_KYC_GUIDANCE-2026-0001` | Amendments to Customer Onboarding Framework (RDA Scope) | `AML_KYC_GUIDANCE` | 2026-03-24 | BPRD Circ. Ltr 09/2026 | `VERIFIED_OFFICIAL_DOMAIN` |
| `PK-SBP-CONSUMER_GUIDANCE-2025-0001` | Business Conduct and Fair Treatment of Consumers (BC&FRF) | `CONSUMER_GUIDANCE` | 2025-10-17 | BPRD Circ. 04/2025 | `VERIFIED_OFFICIAL_DOMAIN` |
| `PK-SBP-FINTECH_REGULATION-2023-0001` | Revised Regulations for Electronic Money Institutions (EMIs) | `FINTECH_REGULATION` | 2023-06-16 | PSP&OD Circ. 03/2023 | `VERIFIED_OFFICIAL_DOMAIN` |
| `PK-SBP-PRUDENTIAL_REGULATION-2024-0001` | Prudential Regulations for Corporate / Commercial Banking | `PRUDENTIAL_REGULATION` | 2024-06-30 | SBP PR Booklet | `VERIFIED_OFFICIAL_DOMAIN` |
| `PK-SBP-PRUDENTIAL_REGULATION-2025-0001` | Prudential Regulations for Microfinance Banks (MFBs) | `PRUDENTIAL_REGULATION` | 2025-05-16 | SBP PR Microfinance | `VERIFIED_OFFICIAL_DOMAIN` |
| `PK-SBP-PAYMENT_SYSTEM_REPORT-2025-0001` | Annual Payment Systems Review FY25 | `PAYMENT_SYSTEM_REPORT` | 2025-10-31 | SBP PSD Review | `REQUIRES_MANUAL_DOCUMENT_VERIFICATION` |
| `PK-SBP-MONETARY_POLICY-2026-0001` | Monetary Policy Statement - September 14, 2026 | `MONETARY_POLICY` | 2026-09-14 | SBP MPC Statement | `REQUIRES_MANUAL_DOCUMENT_VERIFICATION` |
| `PK-SBP-PUBLIC_DISCLOSURE-2025-0001` | Financial Stability Review 2025 | `PUBLIC_DISCLOSURE` | 2025-11-15 | Statutory Report S.39 | `REQUIRES_MANUAL_DOCUMENT_VERIFICATION` |
| `PK-SBP-BANKING_STATISTICS-2025-0001` | Statistics on Banking System of Pakistan – June 2025 | `BANKING_STATISTICS` | 2025-08-15 | SBP Statistics Dept | `VERIFIED_OFFICIAL_DOMAIN` |
| `PK-SBP-FINTECH_REGULATION-2025-0001` | Guidelines for Regulatory Sandbox | `FINTECH_REGULATION` | 2025-05-15 | SBP Sandbox Framework | `VERIFIED_OFFICIAL_DOMAIN` |

---

## 5. Category & Temporal Distribution Analysis

### 5.1 Category Breakdown
The initial candidate inventory achieves high taxonomy coverage across 9 functional document categories:

```
[AML_KYC_GUIDANCE]        ████████████ 2 (16.7%)
[PRUDENTIAL_REGULATION]   ████████████ 2 (16.7%)
[FINTECH_REGULATION]      ████████████ 2 (16.7%)
[DIGITAL_BANKING_POLICY]  ██████ 1 (8.3%)
[CONSUMER_GUIDANCE]       ██████ 1 (8.3%)
[PAYMENT_SYSTEM_REPORT]   ██████ 1 (8.3%)
[MONETARY_POLICY]         ██████ 1 (8.3%)
[PUBLIC_DISCLOSURE]       ██████ 1 (8.3%)
[BANKING_STATISTICS]      ██████ 1 (8.3%)
```

### 5.2 Temporal Distribution (2022–2026)
Candidates bridge historical regulatory baselines and active circular updates:

* **2022:** 1 document (*Digital Banking Licensing Framework*)
* **2023:** 1 document (*EMI Regulations*)
* **2024:** 1 document (*Corporate Prudential Regulations*)
* **2025:** 7 documents (*Customer Onboarding, Consumer Protection, Microfinance PR, Payment Review, Financial Stability, Banking Statistics, Regulatory Sandbox Guidelines*)
* **2026:** 2 documents (*Customer Onboarding Amendments, Monetary Policy Statement*)

---

## 6. Important Version & Supersession Case Study

### 6.1 Consolidated Customer Onboarding Framework Case

A core challenge in regulatory NLP is handling temporal supersession and multi-document amendments without overwriting historical baselines. In this candidate discovery batch, a specific real-world pair illustrates this requirement:

1. **Base Regulatory Framework:**
   * **Document ID:** `PK-SBP-AML_KYC_GUIDANCE-2025-0001`
   * **Title:** Consolidated Customer Onboarding Framework
   * **Reference:** BPRD Circular No. 01 of 2025
   * **Publication Date:** 2025-07-25
   * **Role:** Establishes the core unified regulatory standards for account opening, digital onboarding, identity verification, and CDD/KYC requirements across banks, MFBs, and EMIs.

2. **Subsequent Amendment / Update:**
   * **Document ID:** `PK-SBP-AML_KYC_GUIDANCE-2026-0001`
   * **Title:** Amendments to Consolidated Customer Onboarding Framework – Expansion of Roshan Digital Accounts Scope
   * **Reference:** BPRD Circular Letter No. 09 of 2026
   * **Publication Date:** 2026-03-24
   * **Role:** Specifically amends the 2025 base framework by extending Roshan Digital Account (RDA) eligibility and digital onboarding channels to all non-resident natural and juridical persons.

### 6.2 Regulatory Sandbox Provenance Correction

* **Artifact:** `Guidelines for Regulatory Sandbox` (`PK-SBP-FINTECH_REGULATION-2025-0001`)
* **Chronology Verification:** Draft guidelines for the SBP Regulatory Sandbox were initially published for public consultation in December 2023. The final **Guidelines for Regulatory Sandbox** were formally issued in May 2025 (`2025-05-15`).
* **Handling:** Cataloged under `FINTECH_REGULATION` with publication date `2025-05-15`. Supersedes the December 2023 public consultation draft.

---

## 7. Verification & Selection Rationale

### 7.1 Selection Rationale
Candidate selection prioritized high-impact statutory frameworks, consumer protection rules, and digital transaction policies over routine administrative announcements (such as public holiday circulars or staff transfer notices). Selected documents address real-world financial queries regarding account opening, digital wallet limits, consumer fee transparency, and central bank monetary stance.

### 7.2 Manual Verification Requirements
For 3 candidate reports (`PAYMENT_SYSTEM_REPORT-2025-0001`, `MONETARY_POLICY-2026-0001`, and `PUBLIC_DISCLOSURE-2025-0001`), direct PDF download endpoints require manual HTTP header inspection (`%PDF-` header check and SSL certificate validation) prior to Phase 1B.3 execution. In accordance with URL Rule 7, direct URLs were cataloged conservatively and assigned `REQUIRES_MANUAL_DOCUMENT_VERIFICATION`.

---

## 8. Exclusions & Limitations

### 8.1 Exclusions
* **Routine Administrative Circulars:** Office holiday schedules, employee transfers, routine tender notices, and currency demonetization circulars without research relevance were excluded.
* **Third-Party Reposting Platforms:** Non-official PDF hosts (e.g., Scribd, SlideShare, external banking blogs) were excluded to maintain absolute provenance integrity.

### 8.2 Limitations
* **Single Institution Focus:** Phase 1B.2 focuses exclusively on SBP (`TIER_1`). Regulated commercial banks (`TIER_2`) and international bodies (`TIER_3`) cataloged in `research/source_registry.md` will be covered in subsequent discovery batches.
* **No Binary Acquisition:** Files have not yet been downloaded to disk or hashed (`sha256: null`, `file_size_bytes: null`).

---

## 9. Next Steps

1. **Phase 1B.3 — Candidate Verification & Header Validation:** Perform automated HTTP HEAD/GET checks to verify SSL certificates, HTTP 200 response codes, and `%PDF-` MIME headers for candidates marked `REQUIRES_MANUAL_DOCUMENT_VERIFICATION`.
2. **Phase 1B.4 — Controlled Document Acquisition:** Execute single-document acquisition scripts to populate `data/raw/` with verified PDFs and update SHA-256 cryptographic hashes in `data/manifest/sbp_discovery_candidates.jsonl`.
