# Data Governance Protocol: TrustFin AI

> **Governance Framework Version:** 1.0 (Phase 1A)  
> **Applicability:** All research datasets, manifests, annotations, and benchmarking assets.

---

## 1. Governance Principles
The TrustFin AI research corpus adheres to strict data governance to ensure scientific reproducibility, legal compliance, factual fidelity, and ethical integrity:
1. **Verifiability:** Every piece of evidence must trace directly to an official source.
2. **Immutability:** Raw ingested source documents must never be modified, overwritten, or re-hashed in place.
3. **Reproducibility:** Experiments conducted on a named corpus version (`v0.1`, `v0.2`) must be identically reconstructible from the manifest.
4. **Privacy-by-Design:** Strict exclusion of personally identifiable information (PII) or confidential banking customer data.

---

## 2. Provenance & Source Traceability
Every document ingested into the repository must possess an unbroken provenance trail recorded in the dataset manifest (`data/manifest/*.jsonl`). 

Required provenance attributes include:
- Canonical source URL of the publication.
- Exact publication date and archival retrieval timestamp.
- Issuing institution name and institutional category.
- Source authority tier (Tier 1 through Tier 4).
- Formal document category.

---

## 3. Raw Data Immutability & Cryptographic Hashing
- **Immutability Protocol:** Files written to `data/raw/` are treated as write-once, read-only artifacts.
- **Cryptographic Verification:** Upon retrieval, every raw document is hashed using SHA-256 (`sha256`).
- **Integrity Validation:** Downstream extraction, parsing, and chunking pipelines must verify the file's SHA-256 against the recorded manifest entry before processing. If a checksum mismatch occurs, execution aborts.
- **Separation of Stages:** Processed artifacts (e.g., text chunks, markdown representations, embeddings) are saved exclusively to `data/processed/` and must never overwrite raw documents.

---

## 4. Duplicate Detection & Document Identity
1. **Exact Duplicates:** Byte-identical files (matching SHA-256) are rejected at ingestion to avoid data contamination and synthetic retrieval inflation.
2. **Semantic / Revision Duplicates:** When a financial institution releases an updated version of an existing policy:
   - The new document is ingested as a distinct record with a new deterministic `document_id`.
   - The newer document references the previous document's ID in the `supersedes` field.
   - The superseded document is retained in the corpus to enable temporal reasoning evaluation (e.g., assessing whether models correctly distinguish active regulations from historical directives).

---

## 5. Withdrawn & Superseded Regulations
Financial regulations are frequently amended, repealed, or superseded.
- **Retention Rationale:** Superseded regulations provide essential empirical testbeds for temporal reasoning, counterfactual retrieval, and validity checking.
- **Status Flagging:** The metadata tracks the relationship via `supersedes`. Downstream evaluation queries must explicitly denote whether queries target *current* regulations or *historical* policies.

---

## 6. Privacy & Confidentiality (Zero-PII Policy)
- **Scope Restriction:** Ingestion is restricted to public regulatory circulars, published fee schedules, statutory laws, and official corporate reports.
- **Automated PII Screening:** Even on public documents, future ingestion pipelines will incorporate regex and NER screening to flag any inadvertent inclusion of individual personal names, private bank account numbers, national identity numbers (e.g., CNIC), or email addresses.
- **Action on Detection:** Any document identified as containing non-public customer PII will be purged immediately.

---

## 7. Licensing & Intellectual Property
- **Public Domain & Fair Use:** Public laws, government circulars, and official tariff disclosures are analyzed under non-commercial fair use for academic research.
- **Manifest Distribution:** The dataset manifest, schema definitions, and benchmark question pairs are openly licensed under the project's [MIT License](file:///d:/trustfin-ai/LICENSE).
- **Third-Party Documents:** Raw third-party banking documents are subject to their respective institutional disclosure terms. Research distributions will provide automated download manifests with cryptographic hashes rather than redistributing proprietary third-party archives where licensing restricts redistribution.

---

## 8. Dataset Versioning Protocol
Corpus datasets are versioned independently from software releases:
- **Major Releases (`v1.0`, `v2.0`):** Substantial additions of new regulatory jurisdictions, complete annual cycles, or foundational restructuring of categories.
- **Minor Releases (`v0.1`, `v0.2`):** Incremental additions of verified institutions, document categories, or benchmark query splits.
- **Release Manifests:** Each dataset release is accompanied by a locked, frozen manifest file (e.g., `data/manifest/corpus_v0.1.jsonl`).

---

## 9. Takedown & Removal Policy
If an authoring institution, regulator, or copyright holder requests the removal of a document from the research dataset:
1. **Formal Request Review:** The maintainers will acknowledge and verify the request within 5 business days.
2. **Exclusion:** The affected file will be removed from `data/raw/`, `data/processed/`, and future manifest releases.
3. **Tombstoning:** In historical manifest versions, the entry will be tombstoned (`"status": "withdrawn"`, content purged) with a public rationale to ensure reproducibility audits remain transparent without violating the removal request.
