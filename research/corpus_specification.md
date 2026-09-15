# TrustFin AI: Financial Corpus Specification

> **Specification Version:** 1.0.0 (Phase 1A)  
> **Status:** Approved Research Specification  
> **Focus:** Dataset Design, Taxonomy, Governance, and Ingestion Standards

---

## 1. Purpose
The purpose of this specification is to establish a rigorous, transparent, and reproducible dataset architecture for the **TrustFin AI** research initiative. TrustFin AI investigates trustworthy multilingual Retrieval-Augmented Generation (RAG) in high-stakes financial domains. 

In financial question-answering, errors have legal, fiduciary, and economic consequences. General-purpose language models struggle with domain-specific regulations, fail to ground answers in authoritative text, hallucinate numerical figures, and exhibit significant degradation when queried in low-resource and transliterated languages. This document defines the protocol for selecting, structuring, classifying, and governing the primary financial corpus without downloading or processing live documents prematurely.

---

## 2. Research Scope
The corpus designed under this specification serves as the empirical ground truth for research into:
- **Evidence-Grounded Generation:** Enforcing strict conditioning on retrieved institutional texts.
- **Cross-Lingual Information Retrieval (CLIR):** Retrieving primary regulatory texts published in English using queries formulated in Urdu or Roman Urdu.
- **Hybrid Retrieval Dynamics:** Quantifying trade-offs between sparse lexical search (e.g., BM25 for account tariffs, specific circular numbers, statutory codes) and multilingual dense embeddings.
- **Citation Attribution & Granularity:** Evaluating sentence-level and passage-level evidence tracking.
- **Hallucination Detection:** Validating post-generation verification models against verifiable financial clauses.
- **Principled Abstention:** Benchmarking model calibration on unanswerable, contradictory, or out-of-scope inquiries.
- **Numerical & Tabular Reasoning:** Evaluating model accuracy on multi-row financial fee tables, balance sheets, and regulatory thresholds.

---

## 3. Geographic Scope
- **Initial Research Focus:** Pakistan (`PK`).  
  Pakistan provides a representative multi-tier, multi-lingual financial ecosystem where regulatory circulars and legal statutes are published predominantly in English, while consumer discourse, retail banking queries, and public communication occur in Urdu and Roman Urdu.
- **Extensibility:** The schema, taxonomy, and identifier conventions are explicitly designed to scale to other emerging and developed financial jurisdictions (e.g., Bangladesh, India, UAE, UK) in future research phases.

---

## 4. Domain Scope
The corpus encompasses banking, payment systems, consumer financial protection, microfinance, fintech, and prudential regulatory frameworks. General macroeconomic news, speculative trading forums, and unvetted commentary are strictly excluded.

---

## 5. Language Scope & Taxonomy

| Language Variant | Script / Encoding | ISO Code | Role in Corpus & Benchmarking |
|---|---|---|---|
| **English** | Latin (standard ASCII/UTF-8) | `en` | Primary language of official banking laws, prudential regulations, circulars, and annual disclosures. |
| **Urdu** | Perso-Arabic (Nastaliq/Naskh) | `ur` | Consumer protection guidelines, awareness booklets, bilingual bank forms, statutory summaries. |
| **Roman Urdu** | Latin transliteration | `ur-Latn` / `roman-ur` | **Query and evaluation benchmark language.** Formal institutions rarely publish core regulations in Roman Urdu; its primary research function is evaluating cross-lingual user queries against English evidence documents. |

---

## 6. Target Document Categories

To avoid ad-hoc document gathering, all candidate documents are grouped into four functional tiers across 16 formal categories:

```
                      Target Document Categories
  ┌───────────────────────┬───────────────────────┬───────────────────────┬───────────────────────┐
  │      Regulatory       │     Institutional     │      Statistical      │    Consumer-Facing    │
  ├───────────────────────┼───────────────────────┼───────────────────────┼───────────────────────┤
  │ • REGULATION          │ • ANNUAL_REPORT       │ • BANKING_STATISTICS  │ • CONSUMER_GUIDANCE   │
  │ • CIRCULAR            │ • FINANCIAL_STATEMENT │ • PAYMENT_SYSTEM_     │ • PRODUCT_INFORMATION │
  │ • PRUDENTIAL_         │ • PUBLIC_DISCLOSURE   │   REPORT              │ • FEE_SCHEDULE        │
  │   REGULATION          │                       │                       │ • TERMS_AND_          │
  │ • DIGITAL_BANKING_    │                       │                       │   CONDITIONS          │
  │   POLICY              │                       │                       │                       │
  │ • AML_KYC_GUIDANCE    │                       │                       │                       │
  │ • FINTECH_REGULATION  │                       │                       │                       │
  │ • MONETARY_POLICY     │                       │                       │                       │
  └───────────────────────┴───────────────────────┴───────────────────────┴───────────────────────┘
```

### Detailed Category Definitions
1. **`REGULATION`:** Primary legislative or statutory banking frameworks issued by government bodies.
2. **`CIRCULAR`:** Operational instructions, notices, and policy directives issued to financial institutions.
3. **`PRUDENTIAL_REGULATION`:** Formal regulatory standards governing capital adequacy, liquidity, risk management, and credit operations.
4. **`DIGITAL_BANKING_POLICY`:** Regulatory directives concerning branchless banking, digital wallets, electronic funds transfers, and open banking.
5. **`AML_KYC_GUIDANCE`:** Anti-Money Laundering, Countering Financing of Terrorism (CFT), and Customer Due Diligence regulations.
6. **`FINTECH_REGULATION`:** Licensing and regulatory sandbox frameworks for emerging financial technology entities.
7. **`MONETARY_POLICY`:** Formal monetary policy statements and discount rate announcements.
8. **`ANNUAL_REPORT`:** Audited annual corporate reports of regulated banking institutions.
9. **`FINANCIAL_STATEMENT`:** Quarterly or annual balance sheets, income statements, and capital adequacy disclosures.
10. **`PUBLIC_DISCLOSURE`:** Statutory Basel III pillar disclosures and public risk reports.
11. **`BANKING_STATISTICS`:** Aggregated industry banking performance, deposit ratios, and credit metrics.
12. **`PAYMENT_SYSTEM_REPORT`:** Structured quarterly and annual reviews of retail payments, digital clearing, and card transactions.
13. **`CONSUMER_GUIDANCE`:** Official educational advisories, fraud warnings, and fair treatment of consumer guidelines.
14. **`PRODUCT_INFORMATION`:** Formally filed banking product specifications (e.g., account types, savings schemes).
15. **`FEE_SCHEDULE`:** Official Schedules of Bank Charges (SOC), transaction tariffs, and processing fees.
16. **`TERMS_AND_CONDITIONS`:** Legally binding account opening rules, debit card terms, and digital transaction agreements.

> [!NOTE]
> **Corpus v0.1 Scope:** Corpus v0.1 will focus on a high-value core subset (e.g., `PRUDENTIAL_REGULATION`, `CIRCULAR`, `CONSUMER_GUIDANCE`, and `FEE_SCHEDULE`) before expanding to broader categories.

---

## 7. Target Institution Categories
Documents must originate from clearly classified entities:
- **`CENTRAL_BANK_REGULATOR`:** Central monetary authority (e.g., State Bank of Pakistan) or statutory securities regulator.
- **`COMMERCIAL_BANK`:** Licensed conventional commercial banks.
- **`ISLAMIC_BANK`:** Fully licensed Islamic banking institutions operating under Shariah governance frameworks.
- **`DIGITAL_BANK`:** Specialized digital retail or digital corporate banking licensees.
- **`ELECTRONIC_MONEY_INSTITUTION`:** Licensed EMIs issuing digital payment tokens and operating e-wallets.
- **`PAYMENT_SERVICE_PROVIDER`:** Payment Service Operators (PSOs) and Payment Service Providers (PSPs).
- **`MICROFINANCE_BANK`:** Licensed microfinance banking institutions serving lower-income borrowers.
- **`GOVERNMENT_FINANCIAL_AUTHORITY`:** Ministry of Finance or national revenue authorities.
- **`INTERNATIONAL_FINANCIAL_INSTITUTION`:** Multilateral development banks and global standards bodies (e.g., IMF, World Bank, BIS).

---

## 8. Inclusion Criteria
To be included in the TrustFin AI research corpus, candidate documents must satisfy **all** of the following requirements:
1. **Public Accessibility:** Document must be legally and publicly accessible via official web portals, statutory gazettes, or formal publications.
2. **Definitive Provenance:** Document must have a clear, verifiable authoring institution, original publication title, and traceable primary URL.
3. **Domain Relevance:** Content must directly address financial regulation, operational banking rules, consumer fee structures, financial statistics, or institutional disclosures.
4. **Integrity Verification:** The source binary must be complete, uncorrupted, and verifiable via SHA-256 cryptographic hashing.
5. **Temporal Context:** The document must possess a discoverable publication date or verifiable year of issuance.
6. **Research Utility:** Document must provide textual or tabular evidence suitable for benchmarking information retrieval or grounded question-answering.

---

## 9. Exclusion Criteria
Documents exhibiting any of the following traits will be strictly excluded:
1. **Anonymous / Unattributed Texts:** Documents lacking author institution or regulatory identification.
2. **Third-Party / Unofficial Mirrors:** Unofficial aggregators, third-party blogs, or user-uploaded forums where file tampering cannot be ruled out.
3. **Exact Duplicates:** Byte-identical copies (matching SHA-256 hashes).
4. **Private / Confidential Records:** Any document containing non-public customer records, personally identifiable information (PII), private correspondence, or unredacted account data.
5. **Marketing / Promotional Ephemera:** Promotional social media banners, advertisement flyers, and lifestyle articles with zero regulatory or product definition value.
6. **Corrupted or Unreadable Artifacts:** Truncated files or damaged scans that cannot be processed into readable text.
7. **Copyright-Restricted Proprietary Datasets:** Documents with explicit redistribution bans that prohibit academic research indexing.

---

## 10. Temporal Coverage
### Initial Window (Corpus v0.1)
- **Primary Window:** 2018 – Present.
- **Rationale:** Focuses research on modern digital banking regulations, electronic money institution (EMI) frameworks, updated customer protection circulars, and current fee structures.
- **Historical Exceptions:** Foundational statutory acts (e.g., Banking Companies Ordinance, Central Bank Acts) may be included regardless of publication year due to their persistent legal force.

### Stored Temporal Attributes
Each document entry must record:
- `publication_date`: Date officially published by the issuer.
- `effective_date`: Date the directive, circular, or charge schedule legally takes effect (if specified).
- `retrieval_date`: Timestamp of archival/retrieval.

---

## 11. Source Authority Hierarchy
To prevent model hallucination caused by conflicting or outdated sources, documents are assigned an authority tier:

```
  Tier 1: Official Central Bank / Government Financial Regulator (Highest Authority)
    └── State Bank of Pakistan (SBP), Ministry of Finance, Official Gazettes.
  
  Tier 2: Regulated Financial Institutions
    └── Commercial banks, Islamic banks, EMIs, Microfinance banks (Schedule of Charges, T&Cs).
  
  Tier 3: Recognized International Financial Institutions
    └── Bank for International Settlements (BIS), IMF, World Bank, Financial Stability Board (FSB).
  
  Tier 4: Verified Secondary Sources & Industry Associations
    └── Banking associations, certified professional training institutes (Excluded from v0.1).
```

*Rule for Corpus v0.1:* Only **Tier 1** and **Tier 2** primary-source documents are eligible for collection.

---

## 12. Document Provenance Requirements
Every ingested document in TrustFin AI must maintain an unbroken chain of custody:
1. Immutable original file name.
2. Exact source URL where the file was archived.
3. Cryptographic SHA-256 binary hash.
4. Timestamp of archival (ISO 8601 UTC).
5. Publishing institution and source tier.
6. Local storage in an immutable `data/raw/` directory.

---

## 13. Versioning Strategy
To prevent coupling between the software platform and empirical research datasets, versioning is strictly decoupled:

- **Application Software Version:** Uses Semantic Versioning (`0.1.0`, `0.2.0`, etc.) reflecting code features, API endpoints, and schemas.
- **Corpus Dataset Version:** Uses Research Dataset Versioning (`v0.1`, `v0.2`, `v1.0`) reflecting immutable snapshots of collected and annotated documents.

Any future benchmark results will report both: e.g., `TrustFin-AI App v0.2.0 on Corpus v0.1`.

---

## 14. Duplicate Detection Strategy
1. **Exact Binary Duplicates:** Computed via SHA-256 hash across all raw binaries. If an incoming file matches an existing SHA-256, ingestion aborts with a duplicate status.
2. **Semantic & Version Duplicates:** Detected when an incoming document shares the same `institution`, `document_type`, and normalized `title`, but has a different publication date or revised content.
   - The newer document records the `document_id` of the previous version in its `supersedes` metadata field.
   - The older document is retained to support temporal reasoning benchmarks (evaluating whether a model accurately distinguishes current regulations from superseded rules).

---

## 15. Language Classification Strategy
Documents are tagged with ISO 639-1 language codes and ISO 15924 script codes:
- Monolingual English: `language: "en"`, `script: "Latn"`
- Monolingual Urdu: `language: "ur"`, `script: "Arab"`
- Mixed Bilingual (English & Urdu in same document): `language: "mul"` (multilingual), `script: "mixed"`

---

## 16. Roman Urdu Strategy
> [!IMPORTANT]
> **Key Research Reality:** Institutional banking regulations and legal directives are **not** published in Roman Urdu. Official bodies publish either in English or in standard Urdu (Perso-Arabic Nastaliq script).
>
> Therefore, in TrustFin AI:
> 1. **Source Corpus:** Composed of authoritative English and Urdu texts.
> 2. **Evaluation Benchmarks:** Questions and test prompts are formulated in Roman Urdu (Latin script transliteration), reflecting how consumers naturally query banking services via digital channels.
> 3. **Research Challenge:** Cross-lingual retrieval—retrieving English and Urdu evidence passages to faithfully answer queries formulated in Roman Urdu.

---

## 17. Ethical and Legal Considerations
- **Fair Use for Non-Commercial Research:** Ingested documents consist of public legal regulations, public tariff schedules, and published financial statements intended for open consumer review.
- **No PII Policy:** The corpus must never contain private customer records, account balances, or confidential communications.
- **No Financial Advice Disclaimer:** All downstream models evaluated on this corpus must enforce an explicit disclaimer that generated outputs are for empirical research and informational evaluation only.

---

## 18. Known Limitations
1. **Roman Urdu Orthographic Variance:** Roman Urdu has no standardized phonetic spelling (e.g., *paisa*, *paysa*, *paise*), requiring robust retrieval strategies.
2. **Complex Financial Tables:** Schedules of charges frequently employ nested, multi-column headers and footnote tariffs that resist naive line chunking.
3. **Scanned PDF Artifacts:** Historical circulars published prior to digital archiving may be scanned images requiring high-fidelity OCR.

---

## 19. Future International Expansion
The metadata schema includes `country` (ISO 3166-1 alpha-2) and `jurisdiction` fields. While Corpus v0.1 focuses on `PK`, the taxonomy directly accommodates future comparative cross-border studies (e.g., `BD` Bangladesh Bank, `IN` Reserve Bank of India, `AE` Central Bank of the UAE).

---

## 20. Corpus Versioning & Deterministic Document ID Convention

### Document ID Convention
Every document must have a unique, deterministic, human-readable identifier formatted as:

$$\mathbf{[COUNTRY]\textbf{-}[INSTITUTION]\textbf{-}[DOCUMENT\_TYPE]\textbf{-}[YEAR]\textbf{-}[SEQUENCE]}$$

- `COUNTRY`: ISO 3166-1 alpha-2 (e.g., `PK`).
- `INSTITUTION`: Normalized uppercase abbreviation (e.g., `SBP`, `HBL`, `MBL`).
- `DOCUMENT_TYPE`: Short code derived from the document category (e.g., `REG`, `CIR`, `PRUD`, `GUID`, `SOC`).
- `YEAR`: 4-digit publication or issuance year (e.g., `2023`).
- `SEQUENCE`: 4-digit zero-padded index (e.g., `0001`).

*Example:* `PK-SBP-CIR-2023-0004` represents the 4th circular issued by the State Bank of Pakistan in 2023.

### Manifest Specification
The corpus manifest will be maintained in machine-readable JSON Lines (`.jsonl`) format under `data/manifest/`. Each line constitutes an exact JSON serialization of the `DocumentMetadata` schema.
