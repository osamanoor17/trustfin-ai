# FinUrdu Multilingual Retrieval Benchmark Pilot Report (v0.1)

## Executive Summary

This report documents the design, annotation, manual semantic review, and automated validation of the **FinUrdu Multilingual Retrieval Benchmark Pilot (v0.1)** for TrustFin AI. FinUrdu v0.1 establishes a rigorous research foundation for evaluating cross-lingual information access across English, Urdu, and Roman Urdu financial queries against State Bank of Pakistan (SBP) regulatory documents.

> [!IMPORTANT]
> This phase evaluates benchmark design and annotation infrastructure ONLY. No retrieval models, vector indices, embeddings, or answer generation systems were executed or benchmarked in Phase 2A.

---

## Benchmark Statistics

All metrics in this report are computed directly from `data/benchmarks/finurdu_pilot_v0_1.jsonl`:

| Metric | Count | Percentage |
| :--- | :--- | :--- |
| **Total Information-Need Concepts** | 12 | 100.0% |
| **Total Query Records** | 36 | 100.0% |
| **English Queries (`EN`)** | 12 | 33.3% |
| **Urdu Queries (`UR`)** | 12 | 33.3% |
| **Roman Urdu Queries (`RU`)** | 12 | 33.3% |
| **Answerable Concepts / Queries** | 10 concepts / 30 queries | 83.3% |
| **Unanswerable Concepts / Queries (Out-of-Corpus)** | 2 concepts / 6 queries | 16.7% |
| **Trusted SBP Documents Represented** | 4 of 4 | 100.0% |
| **Verbatim Evidence Validation** | 100% Pass | Automated |
| **Semantic Evidence Sufficiency Review** | 100% Pass (10/10) | Manual Review |
| **Benchmark File SHA-256** | `ea2d964656145a6c058fa9239eff6fd324195a34a6dafda68fce293b9d0b61c4` | Deterministic |

---

## Recomputed Query Intent Taxonomy Distribution

Computed directly from JSONL records:

| Query Type | Concepts | Query Records | Concept % | Record % |
| :--- | :--- | :--- | :--- | :--- |
| `LIMIT_OR_THRESHOLD` | 5 | 15 | 41.7% | 41.7% |
| `REGULATORY_REQUIREMENT` | 5 | 15 | 41.7% | 41.7% |
| `ELIGIBILITY` | 1 | 3 | 8.3% | 8.3% |
| `PROCEDURAL` | 1 | 3 | 8.3% | 8.3% |
| **Total** | **12** | **36** | **100.0%** | **100.0%** |

---

## Recomputed Difficulty Distribution

| Difficulty Level | Concepts | Query Records | Concept % | Record % |
| :--- | :--- | :--- | :--- | :--- |
| `EASY` | 8 | 24 | 66.7% | 66.7% |
| `MEDIUM` | 4 | 12 | 33.3% | 33.3% |
| `HARD` | 0 | 0 | 0.0% | 0.0% |
| **Total** | **12** | **36** | **100.0%** | **100.0%** |

---

## Recomputed Document & Page Distribution

| Document ID | Document Title | Concepts | Query Records | Target Pages |
| :--- | :--- | :--- | :--- | :--- |
| `PK-SBP-DIGITAL_BANKING_POLICY-2022-0001` | Licensing & Regulatory Framework for Digital Banks | 3 | 9 | P20, P21, P26 |
| `PK-SBP-AML_KYC_GUIDANCE-2025-0001` | Consolidated Customer Onboarding Framework | 3 | 9 | P5, P18 |
| `PK-SBP-AML_KYC_GUIDANCE-2026-0001` | RDA Scope Expansion Amendments | 2 | 6 | P1, P2 |
| `PK-SBP-CONSUMER_GUIDANCE-2025-0001` | Business Conduct & Consumer Fair Treatment (BC&FRF) | 2 | 6 | P20, P48 |
| *Out-of-Corpus (Unanswerable)* | Cryptocurrency exchange & Microfinance interest caps | 2 | 6 | None (`[]`) |

---

## Manual Semantic Evidence Sufficiency & Multilingual Review Table

Automated code (`scripts/validate_benchmark.py`) verifies exact verbatim text existence in normalized source pages. **Manual semantic review** verifies that each evidence span actually contains sufficient evidence to answer the query, and that all 3 language variants (`EN`, `UR`, `RU`) are semantically equivalent.

| Concept ID | Answerability | Query Type | Difficulty | Gold Document | Target Page(s) | Semantic Sufficiency | Multilingual Alignment |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `DIGITAL_BANK_MINIMUM_CAPITAL_001` | `ANSWERABLE` | `LIMIT_OR_THRESHOLD` | `EASY` | `PK-SBP-DIGITAL_BANKING_POLICY-2022-0001` | Page 20 | **PASS** (Span contains complete MCR table: DRB 1.5B, DFB 6.5B) | **PASS** |
| `DIGITAL_BANK_CAR_REQUIREMENT_001` | `ANSWERABLE` | `REGULATORY_REQUIREMENT` | `EASY` | `PK-SBP-DIGITAL_BANKING_POLICY-2022-0001` | Page 26 | **PASS** (Span contains 15% CAR requirement and sub-clauses) | **PASS** |
| `DIGITAL_BANK_PILOT_DEPOSIT_CAP_001` | `ANSWERABLE` | `LIMIT_OR_THRESHOLD` | `MEDIUM` | `PK-SBP-DIGITAL_BANKING_POLICY-2022-0001` | Page 21 | **PASS** (Span contains per depositor cap PKR 500,000) | **PASS** |
| `CUSTOMER_ONBOARDING_STANDARDIZED_FORM_001` | `ANSWERABLE` | `REGULATORY_REQUIREMENT` | `EASY` | `PK-SBP-AML_KYC_GUIDANCE-2025-0001` | Page 5 | **PASS** (Span contains requirement and SAOF Annex-A form reference) | **PASS** |
| `CUSTOMER_ONBOARDING_FICTITIOUS_ACCOUNTS_001` | `ANSWERABLE` | `REGULATORY_REQUIREMENT` | `EASY` | `PK-SBP-AML_KYC_GUIDANCE-2025-0001` | Page 5 | **PASS** (Span contains explicit prohibition on fictitious accounts) | **PASS** |
| `ASAAN_ACCOUNT_CREDIT_BALANCE_LIMIT_001` | `ANSWERABLE` | `LIMIT_OR_THRESHOLD` | `MEDIUM` | `PK-SBP-AML_KYC_GUIDANCE-2025-0001` | Page 18 | **PASS** (Span contains Asaan Account entity context and Max Credit Balance PKR 3,000,000) | **PASS** |
| `DIGITAL_ONBOARDING_NON_RESIDENTS_001` | `ANSWERABLE` | `ELIGIBILITY` | `EASY` | `PK-SBP-AML_KYC_GUIDANCE-2026-0001` | Page 1 | **PASS** (Span contains explicit permission for non-resident digital onboarding) | **PASS** |
| `THIRD_PARTY_KYC_RELIANCE_ROSHAN_DIGITAL_001` | `ANSWERABLE` | `PROCEDURAL` | `MEDIUM` | `PK-SBP-AML_KYC_GUIDANCE-2026-0001` | Page 2 | **PASS** (Span contains third-party reliance provision for RDA KYC/CDD) | **PASS** |
| `CONSUMER_COMPLAINT_MAJOR_TAT_001` | `ANSWERABLE` | `LIMIT_OR_THRESHOLD` | `MEDIUM` | `PK-SBP-CONSUMER_GUIDANCE-2025-0001` | Page 48 | **PASS** (Span contains major complaint threshold: >7 working days) | **PASS** |
| `KEY_FACT_STATEMENT_REQUIREMENT_001` | `ANSWERABLE` | `REGULATORY_REQUIREMENT` | `EASY` | `PK-SBP-CONSUMER_GUIDANCE-2025-0001` | Page 20 | **PASS** (Span contains requirement and purpose: comparison and decision making) | **PASS** |
| `CRYPTO_CURRENCY_TRADING_FRAMEWORK_001` | `UNANSWERABLE` | `REGULATORY_REQUIREMENT` | `EASY` | Out-of-Corpus (`[]`) | None (`[]`) | **N/A** (Corpus-Unanswerable Verified) | **PASS** |
| `MICROFINANCE_MAXIMUM_INTEREST_CAP_001` | `UNANSWERABLE` | `LIMIT_OR_THRESHOLD` | `EASY` | Out-of-Corpus (`[]`) | None (`[]`) | **N/A** (Corpus-Unanswerable Verified) | **PASS** |

---

## Multilingual Alignment Review Findings

All 12 benchmark concepts were verified for semantic equivalence across languages:

1. **Urdu Phrasing**: Urdu queries utilize standard Pakistani banking terminology (e.g. `کم از کم سرمائے کی ضرورت` for MCR, `کیپٹل ایڈیکویسی ریشو` for CAR, `آسان اکاؤنٹ` for Asaan Account, `فرضی ناموں` for fictitious names).
2. **Roman Urdu Naturalness**: Roman Urdu queries reflect natural informal Pakistani user search patterns (e.g. `per depositor balance ki maximum limit`, `farzi naamo`, `shanakhti tasdeeq`, `sood ki maximum statutory percentage cap`) rather than rigid literal transliteration.

---

## Unanswerable Concept Corpus Clarification

Both `UNANSWERABLE` concepts represent realistic financial queries for which the **current 4-document SBP pilot corpus contains no evidence**:
- `CRYPTO_CURRENCY_TRADING_FRAMEWORK_001`: Cryptocurrency exchange licensing rules are absent from the 4 pilot SBP circulars.
- `MICROFINANCE_MAXIMUM_INTEREST_CAP_001`: Statutory interest rate caps on microfinance agricultural loans are absent from the pilot SBP circulars.

These are designated as **unanswerable from this corpus**, not as non-existent in real-world law.

---

## Validation Summary

- **Automated Validation (`scripts/validate_benchmark.py`)**: PASS (0 errors).
- **Pytest Suite (`pytest -v`)**: 63 of 63 tests PASSED in 1.01s.
- **SHA-256 Reproducibility**: `ea2d964656145a6c058fa9239eff6fd324195a34a6dafda68fce293b9d0b61c4`.
