# TrustFin AI: Research Questions

> [!NOTE]
> **Status:** Preliminary & Subject to Refinement
> The research questions outlined below form the exploratory foundation for investigating trustworthy multilingual financial question-answering and Retrieval-Augmented Generation (RAG). As empirical benchmarks, corpus collections, and preliminary baselines develop, these questions will be iteratively refined and operationalized.

---

### **RQ1: Language Performance Disparity**
> *How does financial question-answering performance differ across English, Urdu, and Roman Urdu?*
- **Focus:** Benchmarking comprehension, numerical reasoning, and financial terminology understanding across standard English, Nastaliq-script Urdu, and transliterated Roman Urdu.
- **Key Dimension:** Evaluating whether language resource disparity directly correlates with reasoning fidelity in domain-specific financial tasks.

---

### **RQ2: Cross-Lingual Financial Retrieval**
> *Can cross-lingual retrieval improve financial QA for low-resource languages?*
- **Focus:** Assessing scenarios where queries formulated in Urdu or Roman Urdu retrieve authoritative evidence documents primarily published in English (e.g., central bank regulations, corporate financial statements, public disclosures).
- **Key Dimension:** Cross-lingual alignment, query translation versus joint embedding retrieval, and asymmetric dual-encoder efficacy.

---

### **RQ3: Retrieval Modality Optimization (Hybrid Retrieval)**
> *Does hybrid sparse+dense retrieval outperform either approach independently in financial contexts?*
- **Focus:** Comparing lexical/sparse matching (BM25, exact entity and numerical identifiers, account terms) against semantic/dense vector embeddings across low-resource multilingual representations.
- **Key Dimension:** Evaluating reciprocal rank fusion (RRF) and learned weighting mechanisms on mixed tabular-textual financial passages.

---

### **RQ4: Hallucination Mitigation via Evidence Grounding**
> *Can evidence verification reduce unsupported claims and hallucinations in financial answer generation?*
- **Focus:** Developing post-generation and in-generation verification mechanisms to ensure all quantitative values, dates, policy constraints, and conclusions are strictly supported by retrieved context.
- **Key Dimension:** Fact-checking consistency, natural language inference (NLI) scoring, and token-level attribution.

---

### **RQ5: Multilingual Citation Accuracy & Granularity**
> *How accurately can multilingual RAG systems cite the evidence used to produce financial answers?*
- **Focus:** Measuring the precision, recall, and granularity (document-level, page-level, passage-level, sentence-level) of generated citations when synthesizing answers from English, Urdu, and Roman Urdu source texts.
- **Key Dimension:** Eliminating deceptive or misattributed citations in regulatory and consumer banking advice contexts.

---

### **RQ6: Abstention & Unanswerable Question Handling**
> *How reliably can the system identify questions that cannot be answered from the available evidence?*
- **Focus:** Measuring model calibration and abstention accuracy when user inquiries fall outside available corpus knowledge or contradict financial policy disclosures.
- **Key Dimension:** Quantifying false positive answering rates versus principled abstention ("I do not have sufficient evidence in the provided documents to answer this question").
