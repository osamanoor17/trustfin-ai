# Dataset Card: TrustFin AI Multilingual Financial Corpus

> [!IMPORTANT]
> **PRE-COLLECTION DATASET CARD**  
> This dataset card defines the intended design, scope, and governance protocols for the upcoming TrustFin AI research corpus. No documents have been acquired, crawled, or populated yet. Statistics, document tallies, and empirical measurements will be recorded in future releases.

---

## 1. Dataset Summary
The TrustFin AI Corpus is a planned domain-specific research collection designed to evaluate trustworthy multilingual Retrieval-Augmented Generation (RAG) and question-answering in banking, payments, and financial regulation. The initial release (Corpus v0.1) targets the regulatory and retail financial landscape of Pakistan, featuring primary regulatory instruments, bank tariffs, and consumer protection guidelines published in **English** and **Urdu**, coupled with benchmark queries in **Roman Urdu**.

---

## 2. Motivation
While significant NLP benchmarks evaluate financial language models in high-resource western economies (e.g., US SEC EDGAR filings), low-resource multilingual economies face a severe information barrier:
1. Primary legal disclosures, circulars, and central bank prudential rules are published overwhelmingly in English.
2. Millions of consumers and small merchants converse, negotiate, and query banking policies in regional languages (Urdu) or informal transliteration (Roman Urdu).
3. Off-the-shelf generative models suffer from catastrophic hallucination of interest rates, misattribution of banking circulars, and inability to parse complex fee schedules.

TrustFin AI establishes a standardized, reproducible empirical benchmark to investigate cross-lingual retrieval, verifiable evidence attribution, and principled refusal of unanswerable questions in this domain.

---

## 3. Languages
- **English (`en`):** Primary language of statutory regulations, prudential guidelines, circulars, and audited disclosures.
- **Urdu (`ur`):** Perso-Arabic (Nastaliq script) consumer protection circulars, fair treatment guidelines, and bilingual bank forms.
- **Roman Urdu (`ur-Latn` / `roman-ur`):** Evaluated primarily as a **query and benchmark evaluation language** for cross-lingual retrieval rather than a formal publishing medium.

---

## 4. Geographic Scope
- **Country:** Pakistan (`PK`).
- **Jurisdiction:** Federal financial laws and regulations overseen by the State Bank of Pakistan (SBP) and related financial authorities.
- **Extensibility:** The schema incorporates ISO country codes (`country`) to support planned international expansion.

---

## 5. Data Sources & Authority Tiers
Data will be sourced according to a strict provenance hierarchy:
- **Tier 1:** Official central bank / financial regulator web portals and government gazettes.
- **Tier 2:** Official regulated commercial banks, Islamic banks, microfinance banks, and licensed Electronic Money Institutions (EMIs).
- **Tiers 3 & 4:** International standards bodies and verified secondary sources (deferred for v0.1).

*No third-party aggregators, unofficial mirrors, or unverified re-uploads will be admitted.*

---

## 6. Document Types
The planned corpus categorizes documents across 16 functional types:
- **Regulatory:** `REGULATION`, `CIRCULAR`, `PRUDENTIAL_REGULATION`, `DIGITAL_BANKING_POLICY`, `AML_KYC_GUIDANCE`, `FINTECH_REGULATION`, `MONETARY_POLICY`.
- **Institutional:** `ANNUAL_REPORT`, `FINANCIAL_STATEMENT`, `PUBLIC_DISCLOSURE`.
- **Statistical:** `BANKING_STATISTICS`, `PAYMENT_SYSTEM_REPORT`.
- **Consumer-Facing:** `CONSUMER_GUIDANCE`, `PRODUCT_INFORMATION`, `FEE_SCHEDULE`, `TERMS_AND_CONDITIONS`.

---

## 7. Collection Methodology (Planned)
1. **Target Identification:** Curation of canonical URLs from official regulator and institutional portals.
2. **Archival & Ingestion:** Direct retrieval of public PDF artifacts with automated retrieval timestamping.
3. **Cryptographic Integrity:** Generation of SHA-256 binary checksums upon download to ensure immutability.
4. **Metadata Cataloging:** Generating a machine-readable JSONL entry in `data/manifest/` conforming to `DocumentMetadata`.
5. **Deduplication:** Automatic rejection of byte-identical binaries and version tracking of superseded policies.

---

## 8. Metadata Schema
Every entry in the corpus manifest adheres to the `DocumentMetadata` Pydantic model (`app/schemas/document.py`), capturing:
- `document_id`: Deterministic identifier (e.g., `PK-SBP-CIR-2023-0001`).
- `title`, `file_name`, `source_url`.
- `institution`, `institution_type`, `country`, `jurisdiction`, `source_tier`.
- `document_type`, `language`, `script`.
- `publication_date`, `effective_date`, `retrieval_date`.
- `mime_type`, `file_size_bytes`, `page_count`, `sha256`.
- `is_scanned`, `has_tables`, `has_images`.
- `version`, `supersedes`, `license_or_usage_note`, `notes`.

---

## 9. Intended Uses
- Academic and empirical research in multilingual Information Retrieval (IR) and RAG.
- Benchmarking cross-lingual dense and sparse retrieval models.
- Evaluating evidence-grounded answer generation, token attribution, and citation accuracy.
- Designing hallucination detection algorithms on structured financial tables and regulatory clauses.
- Developing calibration mechanisms for unanswerable question detection.

---

## 10. Out-of-Scope Uses
- Real-time automated financial, investment, legal, or tax advice for retail consumers without human fiduciary review.
- Training models for speculative high-frequency trading or algorithmic market manipulation.
- Commercial redistribution of raw third-party copyrighted materials beyond fair use research scopes.

---

## 11. Biases & Known Limitations
- **Orthographic Variance:** Roman Urdu has no standardized spelling; retrieval models may struggle with phonemic transliteration drift.
- **Reporting Bias:** Regulatory documents reflect formal institutional language and may not capture colloquial consumer vocabulary.
- **Tabular Complexity:** Financial fee schedules contain multi-level nested tables that pose challenges for baseline text splitters.

---

## 12. Risks, Privacy & Security
- **Personally Identifiable Information (PII):** Ingestion pipelines will enforce zero-PII filters. The corpus contains only public institutional disclosures, circulars, and fee schedules.
- **Financial Misinformation:** Benchmark models trained or evaluated on the corpus must enforce disclaimers stating that generated answers do not constitute financial advice.

---

## 13. Licensing & Usage
- The dataset metadata, schema, and curation scripts are distributed under the [MIT License](file:///d:/trustfin-ai/LICENSE).
- Individual primary source documents remain subject to the public disclosure terms, government publication rights, or fair use research provisions of their respective authoring institutions.

---

## 14. Maintenance & Versioning
- Dataset releases follow independent versioning (`v0.1`, `v0.2`, `v1.0`), decoupled from software application versions (`0.x.x`).
- Changes will be tracked via timestamped JSONL manifest files stored in `data/manifest/`.

---

## 15. Citation
When citing the TrustFin AI Corpus specification in research:

```bibtex
@misc{trustfin_ai_corpus_2025,
  title={TrustFin AI: Trustworthy Multilingual Financial Intelligence for Low-Resource Languages},
  author={Noor, Muhammad Osama and Contributors},
  year={2025},
  howpublished={\url{https://github.com/osamanoor17/trustfin-ai}},
  note={Research Corpus Specification v1.0.0 (Phase 1A)}
}
```
