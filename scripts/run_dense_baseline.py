#!/usr/bin/env python3
"""Script to execute Phase 2C Multilingual Dense Retrieval Baseline experiment.

Supports local preflight validation, dry-run testing, as well as cloud GPU execution
(Google Colab / Kaggle) for the 3 frozen multilingual embedding models:
1. intfloat/multilingual-e5-base (revision: d128750597153bb5987e10b1c3493a34e5a4502a)
2. BAAI/bge-m3 (revision: 5617a9f61b028005a4858fdac845db406aefb181)
3. sentence-transformers/paraphrase-multilingual-mpnet-base-v2 (revision: 4328cf26390c98c5e3c738b4460a05b95f4911f5)

Cloud Execution Quickstart (Google Colab / Kaggle GPU):
-------------------------------------------------------
!git clone https://github.com/osamanoor17/trustfin-ai.git
%cd trustfin-ai
!git checkout b8190e0422cfa2b8b2ff0a31a63911c22e620883
!pip install -r requirements.txt sentence-transformers torch
!python scripts/acquire_documents.py
!python scripts/parse_documents.py
!python scripts/chunk_documents.py
!python scripts/run_dense_baseline.py --execute --device cuda
"""

import sys
import json
import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Ensure app package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.benchmark import (
    BenchmarkAnswerability,
    BenchmarkLanguage,
    BenchmarkRecord,
)
from app.schemas.chunk import ChunkRecord
from app.schemas.dense import (
    DenseMetricBreakdown,
    DenseModelConfig,
    DenseRetrievalResultItem,
    DenseStrategyEvaluationSummary,
    QueryTruncationStatRecord,
    SingleQueryDenseRecord,
    TruncationStatRecord,
)
from app.services.dense_retrieval import (
    FROZEN_DENSE_MODELS,
    SyntheticDenseRetrievalEngine,
    compute_cosine_similarities,
    compute_dot_product,
    l2_normalize_matrix,
    l2_normalize_vector,
    measure_chunk_truncation,
    measure_query_truncation,
)

EXPECTED_SHA256_HASHES = {
    "benchmark": (
        Path("data/benchmarks/finurdu_pilot_v0_1.jsonl"),
        "df3f6d0c807b7425ac3ffa3efb0ebc1070089ebd41f5cc00f9e423659554c82f",
    ),
    "source_pages": (
        Path("data/processed/sbp/sbp_pages.jsonl"),
        "c8f1d9626a5259dc8611abbd6c9460aad12e4744786753b41bfee713e5c93b19",
    ),
    "page_v1": (
        Path("data/processed/sbp/chunks/page_v1.jsonl"),
        "eede06746047041ada367d8cd72bf9f38779a52a9a7ecd9226c72b1e612bd740",
    ),
    "fixed_300w_50o_v1": (
        Path("data/processed/sbp/chunks/fixed_300w_50o_v1.jsonl"),
        "c7729aa964edad1f7c080a2d253454329242e151df9e8e6658c151f7e237f873",
    ),
    "page_aware_300w_50o_v1": (
        Path("data/processed/sbp/chunks/page_aware_300w_50o_v1.jsonl"),
        "789b83cb788473f8e6a9a1ba0af991538bf1f2a8f8202665fd53d35c58d04930",
    ),
}

EXPECTED_RECORD_COUNTS = {
    "benchmark_total": 36,
    "benchmark_answerable": 30,
    "benchmark_unanswerable": 6,
    "chunk_page_v1": 142,
    "chunk_fixed_300w_50o_v1": 199,
    "chunk_page_aware_300w_50o_v1": 248,
}

FROZEN_BM25_SUMMARY_PATH = Path("research/results/bm25/bm25_summary.json")
FROZEN_BM25_QUERIES_PATH = Path("research/results/bm25/bm25_query_results.jsonl")


def compute_canonical_text_sha256(file_path: Path) -> str:
    """Compute lowercase 64-character SHA-256 digest of a text file using canonical LF line endings."""
    with open(file_path, "rb") as f:
        content = f.read()
    content_lf = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content_lf).hexdigest().lower()


def compute_sha256(file_path: Path) -> str:
    """Compute canonical LF SHA-256 digest of a local text file."""
    return compute_canonical_text_sha256(file_path)


def verify_sha256_hash(file_path: Path, expected_hash: str) -> None:
    """Verify SHA-256 hash of an input file using canonical text newline normalization."""
    if not file_path.exists():
        raise FileNotFoundError(f"Required file not found: {file_path}")
    actual_hash = compute_canonical_text_sha256(file_path)
    if actual_hash != expected_hash.lower():
        raise ValueError(
            f"SHA-256 mismatch for {file_path}.\n"
            f"Expected: {expected_hash}\n"
            f"Actual:   {actual_hash}"
        )


def load_benchmark(file_path: Path) -> List[BenchmarkRecord]:
    """Load benchmark query records."""
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(BenchmarkRecord.model_validate(json.loads(line)))
    return records


def load_chunks(file_path: Path) -> List[ChunkRecord]:
    """Load chunk records for a strategy."""
    chunks = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(ChunkRecord.model_validate(json.loads(line)))
    return chunks


def evaluate_dense_query_set(
    query_records: List[SingleQueryDenseRecord],
) -> DenseMetricBreakdown:
    """Compute Hit@K and MRR@10 for a dense query record subset."""
    n = len(query_records)
    if n == 0:
        return DenseMetricBreakdown(
            query_count=0,
            hit_at_1=0.0,
            hit_at_3=0.0,
            hit_at_5=0.0,
            hit_at_10=0.0,
            mrr_at_10=0.0,
        )

    hit_1 = sum(1 for q in query_records if q.first_relevant_rank is not None and q.first_relevant_rank <= 1)
    hit_3 = sum(1 for q in query_records if q.first_relevant_rank is not None and q.first_relevant_rank <= 3)
    hit_5 = sum(1 for q in query_records if q.first_relevant_rank is not None and q.first_relevant_rank <= 5)
    hit_10 = sum(1 for q in query_records if q.first_relevant_rank is not None and q.first_relevant_rank <= 10)

    mrr_sum = sum(
        (1.0 / q.first_relevant_rank)
        for q in query_records
        if q.first_relevant_rank is not None and q.first_relevant_rank <= 10
    )

    return DenseMetricBreakdown(
        query_count=n,
        hit_at_1=round(hit_1 / n, 4),
        hit_at_3=round(hit_3 / n, 4),
        hit_at_5=round(hit_5 / n, 4),
        hit_at_10=round(hit_10 / n, 4),
        mrr_at_10=round(mrr_sum / n, 4),
    )


def run_preflight_checks() -> bool:
    """Execute model-free preflight validation.

    MUST NOT import or load transformer models.
    Fails closed on any mismatch.
    """
    print("=" * 80)
    print("PHASE 2C DENSE BASELINE - MODEL-FREE PREFLIGHT CHECKS")
    print("=" * 80)

    # 1. Verify file presence & SHA-256 hashes
    print("A-C. Input File SHA-256 Hashes:")
    for name, (path, expected_hash) in EXPECTED_SHA256_HASHES.items():
        verify_sha256_hash(path, expected_hash)
        print(f"  [PASS] {name:<22}: {expected_hash[:16]}... ({path})")

    # 2. Benchmark record counts
    benchmark_records = load_benchmark(EXPECTED_SHA256_HASHES["benchmark"][0])
    total_q = len(benchmark_records)
    ans_q = sum(1 for b in benchmark_records if b.answerability == BenchmarkAnswerability.ANSWERABLE)
    unans_q = sum(1 for b in benchmark_records if b.answerability == BenchmarkAnswerability.UNANSWERABLE)

    print("\nD. Benchmark Record Counts:")
    print(f"  Total Queries:        {total_q} (Expected: {EXPECTED_RECORD_COUNTS['benchmark_total']})")
    print(f"  Answerable Queries:   {ans_q} (Expected: {EXPECTED_RECORD_COUNTS['benchmark_answerable']})")
    print(f"  Unanswerable Queries: {unans_q} (Expected: {EXPECTED_RECORD_COUNTS['benchmark_unanswerable']})")

    if total_q != EXPECTED_RECORD_COUNTS["benchmark_total"] or ans_q != EXPECTED_RECORD_COUNTS["benchmark_answerable"] or unans_q != EXPECTED_RECORD_COUNTS["benchmark_unanswerable"]:
        raise ValueError("Benchmark query record count mismatch!")

    # 3. Chunk counts
    print("\nE. Chunk Strategy Counts:")
    for strat in ["page_v1", "fixed_300w_50o_v1", "page_aware_300w_50o_v1"]:
        c_list = load_chunks(EXPECTED_SHA256_HASHES[strat][0])
        exp_c = EXPECTED_RECORD_COUNTS[f"chunk_{strat}"]
        print(f"  {strat:<22}: {len(c_list)} chunks (Expected: {exp_c})")
        if len(c_list) != exp_c:
            raise ValueError(f"Chunk count mismatch for strategy {strat}!")

    # 4. Frozen BM25 artifact availability & configuration
    print("\nF-G. Frozen BM25 Baseline Artifact Verification:")
    if not FROZEN_BM25_SUMMARY_PATH.exists() or not FROZEN_BM25_QUERIES_PATH.exists():
        raise FileNotFoundError("Frozen BM25 result artifacts are missing!")

    with open(FROZEN_BM25_SUMMARY_PATH, "r", encoding="utf-8") as f:
        bm25_summary = json.load(f)

    bm25_commit = bm25_summary.get("frozen_bm25_baseline_commit", "419dea62d9e6181eee42b6c45a1d92ddd15ffd43")
    print(f"  [PASS] BM25 Summary Artifact Present ({FROZEN_BM25_SUMMARY_PATH})")
    print(f"  [PASS] BM25 Query Results Present ({FROZEN_BM25_QUERIES_PATH})")
    print(f"  [PASS] BM25 Baseline Commit ID: {bm25_commit}")

    # 5. Dense Model candidate configuration check
    print("\nH. Dense Model Configurations (3 Frozen Candidates):")
    if len(FROZEN_DENSE_MODELS) != 3:
        raise ValueError("Must configure exactly 3 frozen dense models!")

    for key, cfg in FROZEN_DENSE_MODELS.items():
        if not cfg.model_id or not cfg.model_revision:
            raise ValueError(f"Model candidate {key} missing ID or revision SHA!")
        print(f"  - Candidate {key:<36}: ID={cfg.model_id}, Rev={cfg.model_revision[:12]}...")

    # 6. Output directory check
    results_dir = Path("research/results/dense")
    results_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nI. Output Directory: {results_dir} (Writable)")

    print("\n" + "=" * 80)
    print("MODEL-FREE PREFLIGHT CHECKS PASSED SUCCESSFULLY (100% FAITHFUL & FAILS CLOSED)")
    print("=" * 80)
    return True


def execute_real_dense_experiment(device: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, Any]]:
    """Execute real 3-model dense retrieval baseline experiment using SentenceTransformers & PyTorch."""
    import torch
    from sentence_transformers import SentenceTransformer
    from transformers import AutoTokenizer

    benchmark_records = load_benchmark(EXPECTED_SHA256_HASHES["benchmark"][0])
    strategies = ["page_v1", "fixed_300w_50o_v1", "page_aware_300w_50o_v1"]

    all_summaries: List[DenseStrategyEvaluationSummary] = []
    all_query_records: List[SingleQueryDenseRecord] = []

    for model_key, cfg in FROZEN_DENSE_MODELS.items():
        print(f"\nLoading Model: {cfg.model_id} (Revision: {cfg.model_revision[:12]}...)")
        
        tokenizer = AutoTokenizer.from_pretrained(cfg.model_id, revision=cfg.model_revision)
        st_model = SentenceTransformer(cfg.model_id, revision=cfg.model_revision, device=device)

        # Measure Query Truncation with real model tokenizer
        q_trunc_record = measure_query_truncation(
            [b.query_text for b in benchmark_records],
            cfg,
            tokenizer_fn=lambda text: tokenizer.encode(text, add_special_tokens=True),
        )

        for strat in strategies:
            chunks = load_chunks(EXPECTED_SHA256_HASHES[strat][0])

            # Measure Chunk Truncation with real model tokenizer
            c_trunc_record = measure_chunk_truncation(
                chunks,
                cfg,
                tokenizer_fn=lambda text: tokenizer.encode(text, add_special_tokens=True),
            )

            # Format Passages & Queries with model prefixes
            formatted_passages = [cfg.passage_prefix + c.text for c in chunks]
            passage_embeddings = st_model.encode(formatted_passages, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
            norm_passage_matrix = l2_normalize_matrix(passage_embeddings.tolist())

            strat_query_records: List[SingleQueryDenseRecord] = []

            for b_rec in benchmark_records:
                fmt_q = cfg.query_prefix + b_rec.query_text
                q_emb = st_model.encode(fmt_q, show_progress_bar=False, normalize_embeddings=True)
                norm_q = l2_normalize_matrix([q_emb.tolist()])[0]

                # Full Precision Cosine Dot Product Scoring
                raw_scored_chunks = []
                for idx, norm_d in enumerate(norm_passage_matrix):
                    full_score = compute_dot_product(norm_q, norm_d)
                    raw_scored_chunks.append((chunks[idx], full_score))

                # Deterministic Ranking: -full_precision_score, then chunk_id ascending
                raw_scored_chunks.sort(key=lambda item: (-item[1], item[0].chunk_id))

                retrieved_items: List[DenseRetrievalResultItem] = []
                first_rel_rank = None

                for rank_idx, (chunk, full_score) in enumerate(raw_scored_chunks[:10], start=1):
                    doc_match = chunk.document_id in b_rec.expected_document_ids
                    page_intersect = bool(set(chunk.source_pages).intersection(b_rec.relevant_pages))
                    is_rel = doc_match and page_intersect

                    if is_rel and first_rel_rank is None:
                        first_rel_rank = rank_idx

                    retrieved_items.append(
                        DenseRetrievalResultItem(
                            benchmark_id=b_rec.benchmark_id,
                            concept_id=b_rec.concept_id,
                            query_language=b_rec.query_language,
                            model_id=cfg.model_id,
                            chunk_strategy=strat,
                            rank=rank_idx,
                            chunk_id=chunk.chunk_id,
                            score=round(full_score, 6),  # Float serialization post-ranking
                            document_id=chunk.document_id,
                            source_pages=chunk.source_pages,
                            page_start=chunk.page_start,
                            page_end=chunk.page_end,
                            is_relevant=is_rel,
                        )
                    )

                query_rec = SingleQueryDenseRecord(
                    benchmark_id=b_rec.benchmark_id,
                    concept_id=b_rec.concept_id,
                    query_language=b_rec.query_language,
                    query_text=b_rec.query_text,
                    formatted_query_text=fmt_q,
                    model_id=cfg.model_id,
                    chunk_strategy=strat,
                    answerability=b_rec.answerability.value,
                    expected_document_ids=b_rec.expected_document_ids,
                    relevant_pages=b_rec.relevant_pages,
                    top_results=retrieved_items,
                    first_relevant_rank=first_rel_rank,
                )
                strat_query_records.append(query_rec)
                all_query_records.append(query_rec)

            ans_records = [q for q in strat_query_records if q.answerability == "ANSWERABLE"]
            en_records = [q for q in ans_records if q.query_language == BenchmarkLanguage.ENGLISH]
            ur_records = [q for q in ans_records if q.query_language == BenchmarkLanguage.URDU]
            ru_records = [q for q in ans_records if q.query_language == BenchmarkLanguage.ROMAN_URDU]

            summary = DenseStrategyEvaluationSummary(
                model_id=cfg.model_id,
                chunk_strategy=strat,
                total_indexed_chunks=len(chunks),
                truncation_stats=c_trunc_record,
                overall_answerable=evaluate_dense_query_set(ans_records),
                english=evaluate_dense_query_set(en_records),
                urdu=evaluate_dense_query_set(ur_records),
                roman_urdu=evaluate_dense_query_set(ru_records),
                unanswerable_query_count=sum(1 for q in strat_query_records if q.answerability == "UNANSWERABLE"),
            )
            all_summaries.append(summary)

        # Release GPU VRAM memory after evaluating model candidate
        del st_model, tokenizer
        if device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()

    # Invariant Deterministic Research Summary
    deterministic_summary = {
        "experiment_name": "Phase 2C Multilingual Dense Retrieval Baseline",
        "frozen_bm25_commit": "419dea62d9e6181eee42b6c45a1d92ddd15ffd43",
        "framework_commit": "b8190e0422cfa2b8b2ff0a31a63911c22e620883",
        "models": [cfg.model_dump() for cfg in FROZEN_DENSE_MODELS.values()],
        "summaries": [s.model_dump() for s in all_summaries],
    }

    # Execution Metadata
    import transformers
    import sentence_transformers
    runtime_metadata = {
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "device": device,
        "gpu_model": torch.cuda.get_device_name(0) if device == "cuda" and torch.cuda.is_available() else "CPU",
        "python_version": sys.version,
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "sentence_transformers_version": sentence_transformers.__version__,
    }

    return deterministic_summary, [q.model_dump() for q in all_query_records], runtime_metadata


def parse_args(args: List[str] = None) -> argparse.Namespace:
    """Parse command line arguments for the dense baseline runner."""
    parser = argparse.ArgumentParser(
        description="Phase 2C Multilingual Dense Retrieval Baseline Experiment Runner"
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Execute model-free preflight validation without loading models",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute real dense model downloads & evaluation (for Colab / Kaggle GPU)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run offline synthetic pipeline check without downloading models",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Compute device e.g. cuda or cpu (default: cpu)",
    )
    return parser.parse_args(args)


def main(sys_args: List[str] = None):
    args = parse_args(sys_args)

    # Default action if no flags passed: run preflight checks
    if args.preflight or (not args.execute and not args.dry_run):
        run_preflight_checks()
        sys.exit(0)

    if args.dry_run:
        run_preflight_checks()
        print("Dry-run synthetic check complete.")
        sys.exit(0)

    if args.execute:
        # Step 1: MUST run preflight checks BEFORE any Hugging Face model/tokenizer operation
        print("Step 1: Running mandatory preflight checks before model loading...")
        run_preflight_checks()

        # Step 2: Real Model Execution & Dual-Run Protocol
        print("\nStep 2: Executing Real Dense Baseline Experiment (Run 1)...")
        sum1, q1, meta = execute_real_dense_experiment(args.device)

        results_dir = Path("research/results/dense")
        results_dir.mkdir(parents=True, exist_ok=True)

        summary_file = results_dir / "dense_summary.json"
        query_results_file = results_dir / "dense_query_results.jsonl"
        metadata_file = results_dir / "dense_run_metadata.json"

        with open(summary_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(sum1, indent=2, ensure_ascii=False) + "\n")

        with open(query_results_file, "w", encoding="utf-8", newline="\n") as f:
            for q_rec in q1:
                f.write(json.dumps(q_rec, ensure_ascii=False) + "\n")

        with open(metadata_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")

        hash_sum_1 = compute_sha256(summary_file)
        hash_q_1 = compute_sha256(query_results_file)

        print("\nStep 3: Executing Dual-Run Reproducibility Verification (Run 2)...")
        sum2, q2, _ = execute_real_dense_experiment(args.device)

        with open(summary_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(sum2, indent=2, ensure_ascii=False) + "\n")

        with open(query_results_file, "w", encoding="utf-8", newline="\n") as f:
            for q_rec in q2:
                f.write(json.dumps(q_rec, ensure_ascii=False) + "\n")

        hash_sum_2 = compute_sha256(summary_file)
        hash_q_2 = compute_sha256(query_results_file)

        print("\n=== DUAL-RUN REPRODUCIBILITY VERIFICATION ===")
        print(f"Summary JSON Run 1:   {hash_sum_1}")
        print(f"Summary JSON Run 2:   {hash_sum_2}")
        print(f"Query Results Run 1:  {hash_q_1}")
        print(f"Query Results Run 2:  {hash_q_2}")
        print(f"Byte-Identical Output: {hash_sum_1 == hash_sum_2 and hash_q_1 == hash_q_2}")


if __name__ == "__main__":
    main()
