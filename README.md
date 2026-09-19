# TrustFin AI: Trustworthy Multilingual Financial Intelligence for Low-Resource Languages

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)]()
[![Status: Phase 2A — Multilingual Retrieval Benchmark Foundation](https://img.shields.io/badge/Status-Phase%202A%20%E2%80%94%20Multilingual%20Retrieval%20Benchmark%20Foundation-informational.svg)]()

TrustFin AI is an open-source research project investigating **trustworthy multilingual Retrieval-Augmented Generation (RAG)** for financial, banking, and regulatory documents, initially focused on **English**, **Urdu**, and **Roman Urdu**.

This repository is **not** a generic consumer chatbot wrapper. It is designed as a rigorous empirical experimentation framework to evaluate factual consistency, cross-lingual retrieval fidelity, verifiable citations, and principled hallucination mitigation in high-stakes financial domains.

---

## 📌 Current Development Status

- **Phase 0 — Foundation:** **Complete** (Repository architecture, API base, config, health check, testing baseline, research scaffolding).
- **Phase 1A — Corpus Specification:** **Complete** (Research dataset design, metadata schema, target categories, authority hierarchy, dataset card, data governance).
- **Phase 1B.1 — Source Registry & Acquisition Planning:** **Complete** (Official source registry, candidate institution catalog, acquisition workflow, status lifecycle, selection log schema).
- **Phase 1B.2 — Verified Document Discovery & Selection:** **Complete** (Official SBP candidate discovery inventory, entry point validation, candidate manifest compilation).
- **Phase 1B.3 — Controlled Document Acquisition & Identity Verification:** **Complete** (Official SBP PDF HTTP acquisition, SHA-256 binary integrity hashing, two-stage semantic identity verification).
- **Phase 1C — Document Parsing & Normalization:** **Complete** (PyMuPDF page-aware extraction, conservative normalization, 142 pages extracted across 4 trusted SBP pilot documents, reproduciblity manifest).
- **Phase 1D — Chunking & Provenance Design:** **Complete** (Experimental page, fixed-window, and page-aware window chunking variants, strict provenance schemas, coverage validation, reproducibility manifest).
- **Phase 2A — Multilingual Retrieval Benchmark Foundation:** **Complete** (FinUrdu pilot benchmark v0.1: 12 concepts, 36 multilingual query records across EN/UR/RU, Pydantic schemas, verbatim evidence validation, dataset card, specification, and unit test suite).

> [!NOTE]
> *Corpus design, metadata schemas, source registry, acquisition pipeline, document normalization, chunking variants, and the FinUrdu pilot retrieval benchmark are formally established. Retrieval experiments (BM25, dense indices), vector databases, embeddings, and LLM calls are deferred to subsequent research phases.*

---

## 🔬 Research Motivation & Problem Statement

Access to transparent, accurate, and evidence-grounded financial information is critical for financial inclusion. In multi-lingual economies such as Pakistan and South Asia, authoritative banking circulars, schedules of bank charges, and financial regulations are overwhelmingly published in English. However, millions of everyday consumers, micro-merchants, and small business owners communicate and query financial services in Urdu (Nastaliq script) or Roman Urdu (Latin-script transliteration).

When general-purpose Large Language Models (LLMs) are tasked with answering financial questions in these languages, they present severe failure modes:
1. **Financial Hallucinations:** Inventing interest rates, fee schedules, or policy terms.
2. **Cross-Lingual Information Gaps:** Failing to retrieve relevant English regulatory guidance when prompted in low-resource or transliterated languages.
3. **Lack of Attribution:** Providing unsupported answers with absent or fabricated citations.
4. **False Confidence on Unanswerable Inquiries:** Generating plausible-sounding guesses instead of abstaining when documents do not contain the answer.

TrustFin AI investigates how hybrid retrieval, cross-lingual alignment, and evidence verification mechanisms can ensure reliable financial intelligence for low-resource languages.

---

## 🌐 Initial Languages

- **English (EN):** Primary language of formal banking regulations, disclosures, and financial reports.
- **Urdu (UR):** National language written in Perso-Arabic (Nastaliq) script; low-resource in digital NLP benchmarks.
- **Roman Urdu (Roman UR):** Phonetic Urdu written in Latin script, prevalent in messaging and consumer search queries, characterized by non-standardized orthography.

---

## 🎯 Proposed Research Areas

1. **Cross-lingual financial question answering:** Evaluating cross-lingual semantic matching where queries and retrieved evidence span different languages.
2. **Hybrid retrieval (Sparse + Dense):** Combining lexical precision (BM25 for financial terminology, account codes, tariff rates) with dense multilingual semantic embeddings.
3. **Evidence-grounded answer generation:** Constraining generative outputs strictly to verifiable context.
4. **Citation accuracy & granularity:** Measuring sentence- and passage-level attribution fidelity.
5. **Hallucination detection:** Developing verifiable post-generation and in-generation verification checks.
6. **Unanswerable question handling:** Calibrating model abstention when evidence is insufficient or conflicting.
7. **Multilingual model evaluation:** Benchmarking open-weight multilingual models.
8. **Financial table and document reasoning:** Parsing and reasoning over complex financial tables and multi-column circulars.
9. **Retrieval and generation benchmarking:** Establishing reproducible evaluation suites.
10. **Cost, latency, and accuracy trade-offs:** Designing practical pipelines viable on resource-constrained infrastructure.

---

## 🏗️ Architecture Overview

```
trustfin-ai/
│
├── app/                  # FastAPI Application Source Code
│   ├── api/              # API router and endpoints
│   │   └── routes/       # Sub-routers (e.g. /health)
│   ├── core/             # Application configuration and settings (Pydantic Settings)
│   ├── models/           # Domain models and ORM entities (future phases)
│   ├── schemas/          # Pydantic schemas and serialization models
│   ├── services/         # Business logic and service orchestration
│   └── main.py           # FastAPI application factory and entrypoint
│
├── research/             # Scientific Research Scaffolding
│   ├── research_questions.md # Formalized preliminary research questions (RQ1-RQ6)
│   ├── methodology.md    # Experimental protocols, metrics, and hypotheses
│   ├── experiments/      # Experiment configuration and tracking scripts
│   └── results/          # Tabulated experimental evaluations and metrics
│
├── data/                 # Data Pipeline Assets (excluded from VCS)
│   ├── raw/              # Raw PDFs, regulatory circulars, bank schedules
│   ├── processed/        # Cleaned, chunked, and normalized passages
│   └── benchmarks/       # Curated QA pairs and ground-truth retrieval sets
│
├── notebooks/            # Exploratory research and analysis notebooks
├── tests/                # Automated pytest suite
├── scripts/              # Data collection and utility automation scripts
├── docs/                 # Documentation and technical architecture notes
│
├── .env.example          # Environment variable template
├── .gitignore            # Git exclusion rules for Python, models, datasets, etc.
├── requirements.txt      # Minimal Phase 0 dependencies
├── LICENSE               # MIT License
└── README.md             # Project overview and documentation
```

---

## 🚀 Quickstart & Installation

### Prerequisites

- Python 3.11 or higher
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/trustfin-ai.git
cd trustfin-ai
```

### 2. Create and Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example configuration file:

```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

---

## 💻 Running the Application

Start the local development server with Uvicorn:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, access:
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Interactive OpenAPI Documentation (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Health Endpoint Specification

**Request:**
```http
GET /health HTTP/1.1
Host: 127.0.0.1:8000
```

**Response:**
```json
{
  "status": "healthy",
  "project": "TrustFin AI",
  "version": "0.1.0"
}
```

---

## 🧪 Running Tests

Execute the automated test suite with pytest:

```bash
pytest
```

For verbose output:

```bash
pytest -v
```

---

## 🗺️ Research Roadmap

The planned phases of the TrustFin AI research lifecycle are structured as follows:

| Phase | Description | Status | Target Environment |
|---|---|---|---|
| **Phase 0 — Foundation** | Project architecture, API base, config, research questions, methodology scaffolding | **Complete** | Local Machine |
| **Phase 1A — Corpus Specification** | Research dataset design, metadata schema, target categories, authority hierarchy, data governance | **Complete** | Local Machine |
| **Phase 1B.1 — Source Registry & Acquisition Plan** | Candidate authoritative source catalog, acquisition workflow SOPs, status lifecycle | **Complete** | Local Machine |
| **Phase 1B.2 — Document Discovery & Selection** | Candidate SBP document discovery, entry point verification, candidate manifest compilation | **Complete** | Local Machine |
| **Phase 1B.3 — Acquisition & Identity Verification** | Official PDF acquisition, SHA-256 binary validation, multi-signal identity verification | **Complete** | Local Machine |
| **Phase 1C — Document Parsing & Normalization** | PyMuPDF page-aware text extraction, conservative normalization, reproducibility manifest | **Complete** | Local Machine |
| **Phase 1D — Chunking & Provenance Design** | Experimental page, fixed-window, and page-aware window chunking variants, reproducibility manifest | **Complete** | Local Machine |
| **Phase 2 — Baseline Retrieval & Evaluation** | Implementation of BM25, dense bi-encoder retrieval, and cross-lingual retrieval benchmarks | Planned | Local / Colab |
| **Phase 3 — Hybrid Retrieval & Reranking** | Sparse+dense fusion (RRF), cross-encoder reranking, and tabular retrieval optimization | Planned | Colab / Kaggle GPU |
| **Phase 4 — Generation & Evidence Grounding** | Open-weight LLM generation, citation attribution, and evidence verification pipelines | Planned | Colab / Kaggle GPU |
| **Phase 5 — Abstention & Hallucination Mitigation** | Calibrated refusal mechanisms, NLI-based verification, and hallucination stress testing | Planned | Colab / Kaggle GPU |
| **Phase 6 — Benchmarking & Publication** | Comprehensive empirical comparative study, ablation analysis, and open benchmark release | Planned | Compute Cluster |

---

## 📄 License

This project is licensed under the [MIT License](file:///d:/trustfin-ai/LICENSE).
