# FinUrdu Multilingual Retrieval Benchmark Dataset Card (v0.1 Pilot)

## Benchmark Overview

- **Benchmark Name**: FinUrdu Multilingual Retrieval Benchmark Pilot (`finurdu_pilot_v0_1`)
- **Version**: `0.1`
- **Release Date**: September 2026
- **Repository Location**: `data/benchmarks/finurdu_pilot_v0_1.jsonl`
- **File SHA-256**: `ea2d964656145a6c058fa9239eff6fd324195a34a6dafda68fce293b9d0b61c4`
- **License**: MIT (Research & Evaluation Use)

---

## Intended Use

FinUrdu v0.1 is a specialized research benchmark created to evaluate **cross-lingual retrieval performance** for Pakistani financial and regulatory information access. It enables benchmarking sparse (BM25), dense, and hybrid retrieval models on retrieving English-medium regulatory evidence when queried in **English**, **Urdu**, and **Roman Urdu**.

> [!NOTE]
> This dataset is designed for **retrieval evaluation only**. It does NOT evaluate LLM answer generation or RAG synthesis.

---

## Dataset Composition & Size

- **Total Query Records**: 36
- **Total Information-Need Concepts**: 12
- **Queries per Language**:
  - **English (`EN`)**: 12 queries (33.3%, Latin script)
  - **Urdu (`UR`)**: 12 queries (33.3%, Arabic script)
  - **Roman Urdu (`RU`)**: 12 queries (33.3%, Latin script)
- **Answerability Distribution**:
  - **Answerable Concepts**: 10 concepts (83.3%, 30 query records)
  - **Unanswerable Concepts (Out-of-Corpus)**: 2 concepts (16.7%, 6 query records)

---

## Source Corpus Provenance

All gold evidence is anchored directly to the 4 identity-verified State Bank of Pakistan (SBP) regulatory documents in the TrustFin AI corpus (142 normalized pages):

1. `PK-SBP-DIGITAL_BANKING_POLICY-2022-0001`: Licensing and Regulatory Framework for Digital Banks (42 pages)
2. `PK-SBP-AML_KYC_GUIDANCE-2025-0001`: Consolidated Customer Onboarding Framework (21 pages)
3. `PK-SBP-AML_KYC_GUIDANCE-2026-0001`: Amendments to Consolidated Customer Onboarding Framework – Expansion of RDA Scope (2 pages)
4. `PK-SBP-CONSUMER_GUIDANCE-2025-0001`: Business Conduct and Fair Treatment of Consumers Regulatory Framework (77 pages)

---

## Annotation Methodology & Verification Protocol

1. **Concept Formulation**: 12 information-need concepts were defined based on regulatory rules, limits, eligibility, and consumer rights across all 4 SBP documents.
2. **Gold Evidence Anchoring**: Each answerable concept was linked to exact `document_id` and `page_number` provenance, with verbatim text spans extracted directly from `data/processed/sbp/sbp_pages.jsonl`.
3. **Multilingual Query Authoring**:
   - Queries were manually authored in English, Urdu, and Roman Urdu without using automated LLM or translation APIs.
   - Roman Urdu phrasing was curated to match natural Pakistani user search patterns.
4. **Dual Verification Protocol**:
   - **Automated Validation (`scripts/validate_benchmark.py`)**: Validates unique IDs, schema compliance, script encodings, document ID bounds, and verbatim substring existence.
   - **Manual Semantic Review**: Manually inspects every verbatim evidence span to guarantee **semantic answer sufficiency** (ensuring spans contain actual answer values, not just section headers) and verifies **cross-lingual semantic equivalence**.

---

## Answerability Clarification

`UNANSWERABLE` items represent plausible financial questions for which the **current 4-document SBP pilot corpus does not contain sufficient evidence**. It does NOT imply that no real-world regulation exists in Pakistani financial law generally.

---

## Known Biases & Limitations

- **Pilot Scale**: FinUrdu v0.1 contains 12 concepts and 36 queries. It serves as a methodology pilot and does not claim full coverage of the Pakistani financial system.
- **English-Medium Corpus Bias**: Source documents are exclusively English-medium official regulatory texts issued by the SBP.
- **Dialect & Orthography**: Roman Urdu spelling varies widely among users; current v0.1 queries reflect standard informal Pakistani Roman Urdu conventions.

---

## Ethical Considerations

- All source documents are official public regulatory circulars and frameworks published by the State Bank of Pakistan.
- No personally identifiable information (PII) or confidential banking data is contained in the benchmark.
