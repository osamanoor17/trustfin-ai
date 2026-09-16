# TrustFin AI: Official Source Registry

> **Registry Version:** 0.1.1 (Phase 1B.1 Consistency Revision)  
> **Status:** Candidate Source Specification  
> **Focus:** Candidate Authoritative Financial Sources for Corpus v0.1  

---

## 1. Overview & Principles

The **Official Source Registry** defines candidate authoritative institutions for **TrustFin AI Corpus v0.1**. 

### Core Principles
1. **Provenance First:** Only official regulatory, government, and licensed financial institution channels are eligible for inclusion.
2. **High Quality over Volume:** Corpus v0.1 remains intentionally small and curated (target: 20–40 documents). Size is secondary to provenance, category diversity, and factual ground truth reliability.
3. **Primary Jurisdiction:** Pakistan (`PK`) serves as the primary geographical focus due to its multi-lingual (English, Urdu, Roman Urdu) regulatory and retail banking landscape.
4. **Verification Boundary:** URLs and domain paths are cataloged conservatively. If exact endpoints cannot be validated via live browser execution during registry compile-time, they are marked with `Verification Status: REQUIRES MANUAL VERIFICATION`. URLs are never fabricated or guessed.

---

## 2. Source Tier Hierarchy

Candidate sources strictly align with the canonical Phase 1A provenance hierarchy (`app/schemas/document.py` and `research/corpus_specification.md`):

| Tier Level | Designation | Description | Authority Weight |
|---|---|---|---|
| **Tier 1 (`TIER_1`)** | `CENTRAL_BANK_REGULATOR` / `GOVERNMENT_FINANCIAL_AUTHORITY` | Official Central Bank, statutory regulators, and government ministries (e.g., State Bank of Pakistan, SECP, Ministry of Finance). | **Highest (Primary Legal & Statutory Grounding)** |
| **Tier 2 (`TIER_2`)** | `COMMERCIAL_BANK` / `ISLAMIC_BANK` / `MICROFINANCE_BANK` / `ELECTRONIC_MONEY_INSTITUTION` | Regulated financial institutions operating under statutory licensing (e.g., HBL, Meezan Bank, Telenor Microfinance, NayaPay). | **High (Operational & Tariff Grounding)** |
| **Tier 3 (`TIER_3`)** | `INTERNATIONAL_FINANCIAL_INSTITUTION` | Recognized international financial bodies (e.g., IMF, World Bank, BIS). | **Contextual / Global Comparative Baseline** |
| **Tier 4 (`TIER_4`)** | `INDUSTRY_ASSOCIATION` / `SECONDARY_SOURCE` | Secondary sources, banking associations, and verified professional bodies (Excluded from v0.1 baseline). | **Secondary / Auxiliary Context** |

---

## 3. Candidate Source Registry

### 3.1 Tier 1: Regulators & Government Financial Authorities

#### 1. State Bank of Pakistan (SBP)
- **Institution:** State Bank of Pakistan
- **Institution Abbreviation:** `SBP`
- **Institution Type:** `CENTRAL_BANK_REGULATOR`
- **Country:** Pakistan (`PK`)
- **Jurisdiction:** Federal / National
- **Source Tier:** Tier 1 (`TIER_1`)
- **Official Domain:** `sbp.org.pk`
- **Relevant Document Categories:** `REGULATION`, `CIRCULAR`, `PRUDENTIAL_REGULATION`, `DIGITAL_BANKING_POLICY`, `AML_KYC_GUIDANCE`, `FINTECH_REGULATION`, `MONETARY_POLICY`, `CONSUMER_GUIDANCE`, `PAYMENT_SYSTEM_REPORT`, `BANKING_STATISTICS`
- **Expected Languages:** `en`, `ur`
- **Research Relevance:** Central monetary authority for banking regulations, interest rate policy decisions, EMI licensing frameworks, prudential standards, branchless banking directives, and consumer protection circulars. Primary anchor source for Tier-1 ground truth.
- **Acquisition Priority:** `P1 (Critical Baseline)`
- **Verification Status:** `REQUIRES MANUAL VERIFICATION`
- **Notes:** Primary anchor institution for Corpus v0.1 baseline documents.

#### 2. Securities and Exchange Commission of Pakistan (SECP)
- **Institution:** Securities and Exchange Commission of Pakistan
- **Institution Abbreviation:** `SECP`
- **Institution Type:** `GOVERNMENT_FINANCIAL_AUTHORITY`
- **Country:** Pakistan (`PK`)
- **Jurisdiction:** Federal / National
- **Source Tier:** Tier 1 (`TIER_1`)
- **Official Domain:** `secp.gov.pk`
- **Relevant Document Categories:** `REGULATION`, `FINTECH_REGULATION`, `PUBLIC_DISCLOSURE`, `AML_KYC_GUIDANCE`
- **Expected Languages:** `en`, `ur`
- **Research Relevance:** Statutory financial regulator governing Non-Banking Financial Companies (NBFCs), digital lending platforms, regulatory sandboxes, and corporate disclosures.
- **Acquisition Priority:** `P2 (High)`
- **Verification Status:** `REQUIRES MANUAL VERIFICATION`
- **Notes:** Complementary statutory authority for non-bank financial regulation.

#### 3. Ministry of Finance, Government of Pakistan (MOF)
- **Institution:** Ministry of Finance, Government of Pakistan
- **Institution Abbreviation:** `MOF_PK`
- **Institution Type:** `GOVERNMENT_FINANCIAL_AUTHORITY`
- **Country:** Pakistan (`PK`)
- **Jurisdiction:** Federal / National
- **Source Tier:** Tier 1 (`TIER_1`)
- **Official Domain:** `finance.gov.pk`
- **Relevant Document Categories:** `REGULATION`, `PUBLIC_DISCLOSURE`, `CONSUMER_GUIDANCE`
- **Expected Languages:** `en`, `ur`
- **Research Relevance:** Primary fiscal policies, federal financial enactments, and national economic publications.
- **Acquisition Priority:** `P3 (Medium)`
- **Verification Status:** `REQUIRES MANUAL VERIFICATION`
- **Notes:** Statutory legislative authority for federal financial framework acts.

---

### 3.2 Tier 2: Regulated Commercial, Islamic, and Microfinance Banking Institutions

#### 4. Habib Bank Limited (HBL)
- **Institution:** Habib Bank Limited
- **Institution Abbreviation:** `HBL`
- **Institution Type:** `COMMERCIAL_BANK`
- **Country:** Pakistan (`PK`)
- **Jurisdiction:** Commercial Banking
- **Source Tier:** Tier 2 (`TIER_2`)
- **Official Domain:** `hbl.com`
- **Relevant Document Categories:** `FEE_SCHEDULE`, `TERMS_AND_CONDITIONS`, `PRODUCT_INFORMATION`, `ANNUAL_REPORT`
- **Expected Languages:** `en`, `ur`
- **Research Relevance:** Regulated conventional commercial bank; baseline for Schedule of Bank Charges (SOC), consumer terms, debit card tariffs, and account specifications.
- **Acquisition Priority:** `P2 (High)`
- **Verification Status:** `REQUIRES MANUAL VERIFICATION`
- **Notes:** Conventional retail commercial bank baseline.

#### 5. MCB Bank Limited (MCB)
- **Institution:** MCB Bank Limited
- **Institution Abbreviation:** `MCB`
- **Institution Type:** `COMMERCIAL_BANK`
- **Country:** Pakistan (`PK`)
- **Jurisdiction:** Commercial Banking
- **Source Tier:** Tier 2 (`TIER_2`)
- **Official Domain:** `mcb.com.pk`
- **Relevant Document Categories:** `FEE_SCHEDULE`, `TERMS_AND_CONDITIONS`, `PRODUCT_INFORMATION`
- **Expected Languages:** `en`, `ur`
- **Research Relevance:** Regulated conventional commercial bank; cross-institutional comparison for commercial tariffs and account disclosures.
- **Acquisition Priority:** `P3 (Medium)`
- **Verification Status:** `REQUIRES MANUAL VERIFICATION`
- **Notes:** Secondary conventional bank baseline.

#### 6. Meezan Bank Limited (MEEZAN)
- **Institution:** Meezan Bank Limited
- **Institution Abbreviation:** `MEEZAN`
- **Institution Type:** `ISLAMIC_BANK`
- **Country:** Pakistan (`PK`)
- **Jurisdiction:** Islamic Banking
- **Source Tier:** Tier 2 (`TIER_2`)
- **Official Domain:** `meezanbank.com`
- **Relevant Document Categories:** `FEE_SCHEDULE`, `TERMS_AND_CONDITIONS`, `PRODUCT_INFORMATION`, `PUBLIC_DISCLOSURE`
- **Expected Languages:** `en`, `ur`
- **Research Relevance:** Full-fledged Islamic commercial bank; key for Shariah-compliant product terminology, profit-sharing disclosures, and Islamic tariff structures.
- **Acquisition Priority:** `P2 (High)`
- **Verification Status:** `REQUIRES MANUAL VERIFICATION`
- **Notes:** Anchor source for Islamic banking products and Shariah compliance terminology.

#### 7. Telenor Microfinance Bank / Easypaisa
- **Institution:** Telenor Microfinance Bank Limited
- **Institution Abbreviation:** `EASYPAISA`
- **Institution Type:** `MICROFINANCE_BANK`
- **Country:** Pakistan (`PK`)
- **Jurisdiction:** Microfinance & Branchless Banking
- **Source Tier:** Tier 2 (`TIER_2`)
- **Official Domain:** `easypaisa.com.pk`
- **Relevant Document Categories:** `FEE_SCHEDULE`, `TERMS_AND_CONDITIONS`, `PRODUCT_INFORMATION`, `CONSUMER_GUIDANCE`
- **Expected Languages:** `en`, `ur`
- **Research Relevance:** Regulated microfinance bank operating the Easypaisa branchless banking platform; relevant for wallet transaction limits, money transfer fee tariffs, and digital account terms.
- **Acquisition Priority:** `P2 (High)`
- **Verification Status:** `REQUIRES MANUAL VERIFICATION`
- **Notes:** Regulated microfinance bank operating a branchless banking service.

#### 8. Mobilink Microfinance Bank / JazzCash
- **Institution:** Mobilink Microfinance Bank Limited
- **Institution Abbreviation:** `JAZZCASH`
- **Institution Type:** `MICROFINANCE_BANK`
- **Country:** Pakistan (`PK`)
- **Jurisdiction:** Microfinance & Branchless Banking
- **Source Tier:** Tier 2 (`TIER_2`)
- **Official Domain:** `jazzcash.com.pk`
- **Relevant Document Categories:** `FEE_SCHEDULE`, `TERMS_AND_CONDITIONS`, `PRODUCT_INFORMATION`, `CONSUMER_GUIDANCE`
- **Expected Languages:** `en`, `ur`
- **Research Relevance:** Regulated microfinance bank operating the JazzCash branchless banking platform; relevant for branchless wallet schedules, transfer fee structures, and consumer account disclosures.
- **Acquisition Priority:** `P3 (Medium)`
- **Verification Status:** `REQUIRES MANUAL VERIFICATION`
- **Notes:** Regulated microfinance bank operating a branchless banking service.

#### 9. NayaPay Private Limited
- **Institution:** NayaPay Private Limited
- **Institution Abbreviation:** `NAYAPAY`
- **Institution Type:** `ELECTRONIC_MONEY_INSTITUTION`
- **Country:** Pakistan (`PK`)
- **Jurisdiction:** Digital Payment Institution
- **Source Tier:** Tier 2 (`TIER_2`)
- **Official Domain:** `nayapay.com`
- **Relevant Document Categories:** `FEE_SCHEDULE`, `TERMS_AND_CONDITIONS`, `PRODUCT_INFORMATION`
- **Expected Languages:** `en`, `ur`
- **Research Relevance:** Licensed Electronic Money Institution (EMI); relevant for consumer digital wallet terms, debit card issuance tariffs, and electronic money fee schedules.
- **Acquisition Priority:** `P3 (Medium)`
- **Verification Status:** `REQUIRES MANUAL VERIFICATION`
- **Notes:** Specialized EMI licensee.

---

### 3.3 Tier 3: Recognized International Financial Institutions

#### 10. International Monetary Fund (IMF)
- **Institution:** International Monetary Fund
- **Institution Abbreviation:** `IMF`
- **Institution Type:** `INTERNATIONAL_FINANCIAL_INSTITUTION`
- **Country:** Global (`GLOBAL`)
- **Jurisdiction:** International
- **Source Tier:** Tier 3 (`TIER_3`)
- **Official Domain:** `imf.org`
- **Relevant Document Categories:** `PUBLIC_DISCLOSURE`, `BANKING_STATISTICS`
- **Expected Languages:** `en`
- **Research Relevance:** Recognized international financial institution publishing country reports, financial system stability assessments (FSAP), and macroeconomic reviews.
- **Acquisition Priority:** `P3 (Medium)`
- **Verification Status:** `REQUIRES MANUAL VERIFICATION`
- **Notes:** Recognized international financial assessment baseline.

#### 11. World Bank Group
- **Institution:** World Bank Group
- **Institution Abbreviation:** `WORLDBANK`
- **Institution Type:** `INTERNATIONAL_FINANCIAL_INSTITUTION`
- **Country:** Global (`GLOBAL`)
- **Jurisdiction:** International
- **Source Tier:** Tier 3 (`TIER_3`)
- **Official Domain:** `worldbank.org`
- **Relevant Document Categories:** `PUBLIC_DISCLOSURE`, `CONSUMER_GUIDANCE`
- **Expected Languages:** `en`
- **Research Relevance:** Recognized international financial institution publishing financial inclusion indicators, remittance flow reports, and retail payment system studies.
- **Acquisition Priority:** `P3 (Medium)`
- **Verification Status:** `REQUIRES MANUAL VERIFICATION`
- **Notes:** Global financial inclusion benchmark context.

#### 12. Bank for International Settlements (BIS)
- **Institution:** Bank for International Settlements
- **Institution Abbreviation:** `BIS`
- **Institution Type:** `INTERNATIONAL_FINANCIAL_INSTITUTION`
- **Country:** Global (`GLOBAL`)
- **Jurisdiction:** International
- **Source Tier:** Tier 3 (`TIER_3`)
- **Official Domain:** `bis.org`
- **Relevant Document Categories:** `PRUDENTIAL_REGULATION`, `PAYMENT_SYSTEM_REPORT`
- **Expected Languages:** `en`
- **Research Relevance:** Recognized international financial institution publishing Basel Committee guidance and CPMI payment system standards.
- **Acquisition Priority:** `P3 (Medium)`
- **Verification Status:** `REQUIRES MANUAL VERIFICATION`
- **Notes:** Global regulatory standards baseline.

---

## 4. Summary Matrix of Candidate Sources

| Institution | Abbr. | Institution Type | Tier | Official Domain | Priority | Verification Status |
|---|---|---|---|---|---|---|
| State Bank of Pakistan | `SBP` | `CENTRAL_BANK_REGULATOR` | Tier 1 (`TIER_1`) | `sbp.org.pk` | P1 | REQUIRES MANUAL VERIFICATION |
| Securities & Exchange Comm. | `SECP` | `GOVERNMENT_FINANCIAL_AUTHORITY` | Tier 1 (`TIER_1`) | `secp.gov.pk` | P2 | REQUIRES MANUAL VERIFICATION |
| Ministry of Finance | `MOF_PK` | `GOVERNMENT_FINANCIAL_AUTHORITY` | Tier 1 (`TIER_1`) | `finance.gov.pk` | P3 | REQUIRES MANUAL VERIFICATION |
| Habib Bank Limited | `HBL` | `COMMERCIAL_BANK` | Tier 2 (`TIER_2`) | `hbl.com` | P2 | REQUIRES MANUAL VERIFICATION |
| MCB Bank Limited | `MCB` | `COMMERCIAL_BANK` | Tier 2 (`TIER_2`) | `mcb.com.pk` | P3 | REQUIRES MANUAL VERIFICATION |
| Meezan Bank Limited | `MEEZAN` | `ISLAMIC_BANK` | Tier 2 (`TIER_2`) | `meezanbank.com` | P2 | REQUIRES MANUAL VERIFICATION |
| Telenor Microfinance / Easypaisa | `EASYPAISA` | `MICROFINANCE_BANK` | Tier 2 (`TIER_2`) | `easypaisa.com.pk` | P2 | REQUIRES MANUAL VERIFICATION |
| Mobilink Microfinance / JazzCash | `JAZZCASH` | `MICROFINANCE_BANK` | Tier 2 (`TIER_2`) | `jazzcash.com.pk` | P3 | REQUIRES MANUAL VERIFICATION |
| NayaPay Private Limited | `NAYAPAY` | `ELECTRONIC_MONEY_INSTITUTION` | Tier 2 (`TIER_2`) | `nayapay.com` | P3 | REQUIRES MANUAL VERIFICATION |
| International Monetary Fund | `IMF` | `INTERNATIONAL_FINANCIAL_INSTITUTION` | Tier 3 (`TIER_3`) | `imf.org` | P3 | REQUIRES MANUAL VERIFICATION |
| World Bank Group | `WORLDBANK` | `INTERNATIONAL_FINANCIAL_INSTITUTION` | Tier 3 (`TIER_3`) | `worldbank.org` | P3 | REQUIRES MANUAL VERIFICATION |
| Bank for International Settlements | `BIS` | `INTERNATIONAL_FINANCIAL_INSTITUTION` | Tier 3 (`TIER_3`) | `bis.org` | P3 | REQUIRES MANUAL VERIFICATION |

---

## 5. Domain Verification Guidelines

1. **Domain Authorization:** Any candidate source link must resolve to the registered domain of the publishing body. Third-party mirrors, personal blogs, slides aggregators, or non-official document hosting services are strictly prohibited.
2. **Verification Protocol:** Prior to triggering Phase 1B acquisition scripts, each URL must be manually or programmatically verified to ensure HTTP 200 response, valid SSL/TLS certificate, matching host identity, and uncorrupted PDF header (`%PDF-`).
3. **No Guessing:** Domain paths must originate from verifiable web indices or direct site navigation. Unchecked speculative links must retain `Verification Status: REQUIRES MANUAL VERIFICATION`.
