# Research Methodology: TrustFin AI

This document establishes the scientific and methodological framework for the TrustFin AI research initiative. 

> [!NOTE]
> This framework serves as a structured protocol for upcoming experimental phases. No experimental results are reported or fabricated at this stage.

---

## 1. Problem Definition
Access to reliable, accurate, and evidence-grounded financial information remains severely limited for speakers of low-resource and regional languages. In jurisdictions where official financial disclosures, regulatory circulars, and banking tariffs are predominantly written in English, millions of consumers and small businesses navigate financial products in Urdu or conversational Roman Urdu. 

Standard generative language models frequently hallucinate quantitative figures, fail to ground responses in authoritative documents, or produce unfaithful translations of financial conditions. TrustFin AI investigates the design of trustworthy, multilingual Retrieval-Augmented Generation (RAG) pipelines that enforce strict factual grounding, verifiable citation attribution, and principled abstention on unanswerable queries.

---

## 2. Research Hypotheses
- **H1 (Cross-Lingual Retrieval):** Mapping Urdu and Roman Urdu queries into an aligned multilingual embedding space will retrieve relevant English regulatory passages with competitive Recall@k compared to native monolingual queries.
- **H2 (Hybrid Retrieval Synergy):** A hybrid retrieval strategy combining sparse lexical matching (e.g., BM25 for precise financial codes, entity names, and account types) and dense vector retrieval will significantly improve MRR and NDCG over either single-modality retriever.
- **H3 (Evidence Verification & Hallucination):** Incorporating an explicit evidence-verification step prior to answer presentation will measurably reduce unsupported factual claims and hallucinated financial figures.
- **H4 (Principled Abstention):** Calibrated confidence thresholds on retrieved evidence relevance can enable reliable identification and rejection of unanswerable or out-of-scope inquiries.

---

## 3. Dataset
### 3.1 Corpus Collection (Planned)
- Central bank circulars, regulatory guidelines, consumer protection frameworks.
- Commercial bank schedule of charges (SOC), fee disclosures, account terms.
- Multilingual annual financial reports and audited disclosures.

### 3.2 Languages
- English (EN)
- Urdu (Nastaliq script) (UR)
- Roman Urdu (Latin transliteration) (Roman UR)

### 3.3 Data Annotation & Validation Protocol
- Expert financial review for question formulation and ground-truth evidence attribution.
- Inclusion of explicit unanswerable query splits to test abstention.

---

## 4. Baselines
To benchmark the proposed multilingual financial RAG pipeline, the following comparative baselines are planned:
- **Zero-shot Closed-Book Generation:** Monolingual and multilingual LLM generation without context retrieval.
- **Translate-Then-Retrieve:** Automatic translation of Roman Urdu / Urdu queries to English using open translation models, followed by standard English retrieval.
- **Pure Lexical Retrieval (BM25):** Monolingual and cross-lingual lexical matching.
- **Pure Dense Retrieval:** Bi-encoder multilingual sentence embeddings without lexical augmentation or re-ranking.

---

## 5. Retrieval Methods
- **Sparse Retrieval:** BM25, tokenized representations optimized for multilingual and transliterated morphology.
- **Dense Retrieval:** Multilingual bi-encoder models fine-tuned or evaluated on semantic retrieval.
- **Hybrid Fusion:** Reciprocal Rank Fusion (RRF) and convex combination weighting between sparse and dense scores.
- **Re-ranking:** Multilingual cross-encoders for secondary precision re-ranking of top-$k$ retrieved documents.

---

## 6. Generation Models
Experiments will evaluate open-weight multilingual models (e.g., small-to-medium parameter open architectures evaluated on hosted or research compute infrastructure such as Colab/Kaggle) subjected to structured context prompts:
- Strict evidence conditioning.
- Explicit inline citation token formatting.
- Constrained refusal triggers for unanswerable inputs.

---

## 7. Evaluation Metrics
### 7.1 Retrieval Metrics
- **Recall@k** ($k \in \{3, 5, 10\}$)
- **Mean Reciprocal Rank (MRR@10)**
- **Normalized Discounted Cumulative Gain (NDCG@10)**

### 7.2 Generation & Factuality Metrics
- **Faithfulness / Groundedness:** Proportion of claims directly supported by retrieved passages.
- **Citation Precision & Recall:** Accuracy of attributed document/passage links.
- **Answer Relevance:** Semantic alignment with the user's intent.
- **Abstention Accuracy / Calibration:** F1-score on unanswerable query detection.

---

## 8. Ablation Studies
Planned component ablations include:
- Removing sparse lexical retrieval in hybrid configurations.
- Disabling the re-ranking stage.
- Removing evidence verification layers.
- Comparing native query retrieval against translate-then-retrieve baselines.
- Evaluating impact of script variations (Nastaliq script vs. Roman Urdu transliteration).

---

## 9. Error Analysis
A qualitative and quantitative taxonomy of failure modes:
- **Retrieval Failures:** Lexical mismatches, transliteration spelling variations, missing context.
- **Reasoning Failures:** Arithmetic mistakes on tabular financial data, date confusion.
- **Attribution Failures:** Correct answers paired with hallucinated or irrelevant citations.
- **Language Bias:** Systemic disparity in answer completeness between English and low-resource language variants.

---

## 10. Limitations
- Roman Urdu lacks standard orthography; variations in phonetic spelling present challenges for tokenizers and lexical matchers.
- Complex financial tables (multi-level headers, footnotes) require specialized table-parsing strategies beyond simple passage chunking.
- Local compute constraints necessitate running heavier parameter experiments on external research GPUs.

---

## 11. Ethical Considerations
- **Financial Risk & Disclaimers:** Automated financial QA systems must never provide unauthorized investment, legal, or fiduciary financial advice without explicit disclaimers.
- **Data Privacy:** Raw training/testing data must exclude personal personally identifiable information (PII) or confidential banking customer records.
- **Fairness & Access:** Ensuring low-resource language speakers receive information of equal reliability, safety, and fidelity as English speakers.
