#!/usr/bin/env python3
"""Script to execute Phase 2B BM25 Sparse Retrieval Baseline experiment.

Evaluates BM25 retrieval over three chunking strategies (page_v1, fixed_300w_50o_v1, page_aware_300w_50o_v1)
against the FinUrdu retrieval benchmark (data/benchmarks/finurdu_pilot_v0_1.jsonl).
"""

import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

# Ensure app package is importable regardless of working directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.benchmark import (
    BenchmarkAnswerability,
    BenchmarkLanguage,
    BenchmarkRecord,
)
from app.schemas.chunk import ChunkRecord
from app.schemas.retrieval import (
    ConceptRankComparison,
    MetricBreakdown,
    RetrievalResultItem,
    SingleQueryRetrievalRecord,
    StrategyEvaluationSummary,
)
from app.services.bm25 import BM25Okapi, tokenize_text

EXPECTED_SHA256_HASHES = {
    "benchmark": (
        Path("data/benchmarks/finurdu_pilot_v0_1.jsonl"),
        "ea2d964656145a6c058fa9239eff6fd324195a34a6dafda68fce293b9d0b61c4",
    ),
    "page_v1": (
        Path("data/processed/sbp/chunks/page_v1.jsonl"),
        "74062cb22bffff87995bbb0d247c37ff55caec89e7877998ba0aac07358be3e8",
    ),
    "fixed_300w_50o_v1": (
        Path("data/processed/sbp/chunks/fixed_300w_50o_v1.jsonl"),
        "2f107d2c63f7b5be5ff99741d1f017639ea6fcd26f3977c56b7f7ceeced7803d",
    ),
    "page_aware_300w_50o_v1": (
        Path("data/processed/sbp/chunks/page_aware_300w_50o_v1.jsonl"),
        "96ed48beb00ae44fc05b2541f1f4e5d83f8cca305f7adcb4d538599e183d15f6",
    ),
}


def verify_sha256_hash(file_path: Path, expected_hash: str) -> None:
    """Verify SHA-256 hash of a file against expected value."""
    if not file_path.exists():
        raise FileNotFoundError(f"Required file not found: {file_path}")
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    actual_hash = sha256_hash.hexdigest().lower()
    if actual_hash != expected_hash.lower():
        raise ValueError(
            f"SHA-256 mismatch for {file_path}.\n"
            f"Expected: {expected_hash}\n"
            f"Actual:   {actual_hash}"
        )


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


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


def evaluate_query_set(
    query_records: List[SingleQueryRetrievalRecord],
) -> MetricBreakdown:
    """Compute Hit@K, MRR@10, and zero-overlap statistics for a query subset."""
    n = len(query_records)
    if n == 0:
        return MetricBreakdown(
            query_count=0,
            zero_overlap_count=0,
            zero_overlap_pct=0.0,
            hit_at_1=0.0,
            hit_at_3=0.0,
            hit_at_5=0.0,
            hit_at_10=0.0,
            mrr_at_10=0.0,
        )

    zero_overlap_cnt = sum(1 for q in query_records if q.has_zero_overlap)
    hit_1 = sum(1 for q in query_records if q.first_relevant_rank is not None and q.first_relevant_rank <= 1)
    hit_3 = sum(1 for q in query_records if q.first_relevant_rank is not None and q.first_relevant_rank <= 3)
    hit_5 = sum(1 for q in query_records if q.first_relevant_rank is not None and q.first_relevant_rank <= 5)
    hit_10 = sum(1 for q in query_records if q.first_relevant_rank is not None and q.first_relevant_rank <= 10)

    mrr_sum = sum(
        (1.0 / q.first_relevant_rank) for q in query_records if q.first_relevant_rank is not None and q.first_relevant_rank <= 10
    )

    return MetricBreakdown(
        query_count=n,
        zero_overlap_count=zero_overlap_cnt,
        zero_overlap_pct=round((zero_overlap_cnt / n) * 100.0, 2),
        hit_at_1=round(hit_1 / n, 4),
        hit_at_3=round(hit_3 / n, 4),
        hit_at_5=round(hit_5 / n, 4),
        hit_at_10=round(hit_10 / n, 4),
        mrr_at_10=round(mrr_sum / n, 4),
    )


def run_experiment() -> Tuple[Dict, List[Dict]]:
    """Execute complete BM25 evaluation across all three strategies."""
    # Step 1: Verify SHA-256 hashes of input files
    for name, (path, expected_hash) in EXPECTED_SHA256_HASHES.items():
        verify_sha256_hash(path, expected_hash)

    benchmark = load_benchmark(EXPECTED_SHA256_HASHES["benchmark"][0])
    strategies = ["page_v1", "fixed_300w_50o_v1", "page_aware_300w_50o_v1"]

    all_query_records: List[SingleQueryRetrievalRecord] = []
    strategy_summaries: List[StrategyEvaluationSummary] = []
    concept_alignments_by_strategy: Dict[str, List[ConceptRankComparison]] = {}

    for strat in strategies:
        chunk_path = EXPECTED_SHA256_HASHES[strat][0]
        chunks = load_chunks(chunk_path)
        bm25 = BM25Okapi(chunks)

        strat_query_records: List[SingleQueryRetrievalRecord] = []
        concept_ranks: Dict[str, Dict[str, int]] = {}

        for b_rec in benchmark:
            search_results = bm25.search(b_rec.query_text, top_k=10)

            retrieved_items: List[RetrievalResultItem] = []
            first_rel_rank = None
            q_tokens = set(tokenize_text(b_rec.query_text))
            has_zero_overlap = q_tokens.isdisjoint(bm25.df.keys())

            for rank_idx, (chunk, score) in enumerate(search_results, start=1):
                # STRICT RELEVANCE RULE: score > 0.0 AND doc match AND page intersection
                doc_match = chunk.document_id in b_rec.expected_document_ids
                page_intersect = bool(
                    set(chunk.source_pages).intersection(b_rec.relevant_pages)
                )
                is_rel = (score > 0.0) and doc_match and page_intersect

                if is_rel and first_rel_rank is None:
                    first_rel_rank = rank_idx

                retrieved_items.append(
                    RetrievalResultItem(
                        benchmark_id=b_rec.benchmark_id,
                        concept_id=b_rec.concept_id,
                        query_language=b_rec.query_language,
                        chunk_strategy=strat,
                        rank=rank_idx,
                        chunk_id=chunk.chunk_id,
                        score=score,
                        document_id=chunk.document_id,
                        source_pages=chunk.source_pages,
                        page_start=chunk.page_start,
                        page_end=chunk.page_end,
                        is_relevant=is_rel,
                    )
                )

            query_record = SingleQueryRetrievalRecord(
                benchmark_id=b_rec.benchmark_id,
                concept_id=b_rec.concept_id,
                query_language=b_rec.query_language,
                query_text=b_rec.query_text,
                chunk_strategy=strat,
                answerability=b_rec.answerability.value,
                expected_document_ids=b_rec.expected_document_ids,
                relevant_pages=b_rec.relevant_pages,
                top_results=retrieved_items,
                first_relevant_rank=first_rel_rank,
                has_zero_overlap=has_zero_overlap,
            )

            strat_query_records.append(query_record)
            all_query_records.append(query_record)

            if b_rec.answerability == BenchmarkAnswerability.ANSWERABLE:
                if b_rec.concept_id not in concept_ranks:
                    concept_ranks[b_rec.concept_id] = {}
                concept_ranks[b_rec.concept_id][b_rec.query_language.value] = first_rel_rank

        # Filter answerable queries for evaluation
        answerable_records = [
            q for q in strat_query_records if q.answerability == "ANSWERABLE"
        ]
        en_records = [
            q for q in answerable_records if q.query_language == BenchmarkLanguage.ENGLISH
        ]
        ur_records = [
            q for q in answerable_records if q.query_language == BenchmarkLanguage.URDU
        ]
        ru_records = [
            q for q in answerable_records if q.query_language == BenchmarkLanguage.ROMAN_URDU
        ]

        summary = StrategyEvaluationSummary(
            chunk_strategy=strat,
            total_indexed_chunks=len(chunks),
            overall_answerable=evaluate_query_set(answerable_records),
            english=evaluate_query_set(en_records),
            urdu=evaluate_query_set(ur_records),
            roman_urdu=evaluate_query_set(ru_records),
            unanswerable_query_count=sum(
                1 for q in strat_query_records if q.answerability == "UNANSWERABLE"
            ),
        )
        strategy_summaries.append(summary)

        alignments = []
        for cid in sorted(concept_ranks.keys()):
            r_dict = concept_ranks[cid]
            alignments.append(
                ConceptRankComparison(
                    concept_id=cid,
                    english_rank=r_dict.get("ENGLISH"),
                    urdu_rank=r_dict.get("URDU"),
                    roman_urdu_rank=r_dict.get("ROMAN_URDU"),
                )
            )
        concept_alignments_by_strategy[strat] = alignments

    # Output directory
    results_dir = Path("research/results/bm25")
    results_dir.mkdir(parents=True, exist_ok=True)

    summary_file = results_dir / "bm25_summary.json"
    query_results_file = results_dir / "bm25_query_results.jsonl"

    summary_data = {
        "experiment_name": "Phase 2B BM25 Sparse Retrieval Baseline",
        "bm25_parameters": {"k1": 1.5, "b": 0.75, "idf_formula": "smoothed_non_negative_okapi"},
        "tokenizer": r"re.findall(r'[^\W_]+', text.lower())",
        "benchmark_file": str(EXPECTED_SHA256_HASHES["benchmark"][0]),
        "benchmark_sha256": EXPECTED_SHA256_HASHES["benchmark"][1],
        "strategies": [s.model_dump() for s in strategy_summaries],
        "concept_alignments": {
            strat: [c.model_dump() for c in concept_alignments_by_strategy[strat]]
            for strat in strategies
        },
    }

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(summary_data, indent=2, ensure_ascii=False) + "\n")

    with open(query_results_file, "w", encoding="utf-8") as f:
        for q_rec in all_query_records:
            f.write(json.dumps(q_rec.model_dump(), ensure_ascii=False) + "\n")

    return summary_data, [q.model_dump() for q in all_query_records]


def main():
    print("Executing Phase 2B BM25 Sparse Retrieval Baseline Experiment...")
    
    # Run 1
    run_experiment()
    hash_summary_1 = compute_sha256(Path("research/results/bm25/bm25_summary.json"))
    hash_queries_1 = compute_sha256(Path("research/results/bm25/bm25_query_results.jsonl"))

    # Run 2 (Reproducibility verification)
    run_experiment()
    hash_summary_2 = compute_sha256(Path("research/results/bm25/bm25_summary.json"))
    hash_queries_2 = compute_sha256(Path("research/results/bm25/bm25_query_results.jsonl"))

    print("\n=== Reproducibility Dual-Run Hashing ===")
    print(f"Summary JSON Run 1:   {hash_summary_1}")
    print(f"Summary JSON Run 2:   {hash_summary_2}")
    print(f"Query Results Run 1:  {hash_queries_1}")
    print(f"Query Results Run 2:  {hash_queries_2}")

    if hash_summary_1 != hash_summary_2 or hash_queries_1 != hash_queries_2:
        print("\n[FAIL] Non-deterministic experiment outputs detected!")
        sys.exit(1)

    print("\n[SUCCESS] Experiment outputs are 100% BYTE-IDENTICAL across dual runs!")

    # Print Summary Table
    with open("research/results/bm25/bm25_summary.json", "r", encoding="utf-8") as f:
        summary_obj = json.load(f)

    print("\n" + "=" * 80)
    print("BM25 SPARSE RETRIEVAL BASELINE RESULTS")
    print("=" * 80)
    for strat in summary_obj["strategies"]:
        print(f"\n--- Strategy: {strat['chunk_strategy']} ({strat['total_indexed_chunks']} chunks) ---")
        ov = strat["overall_answerable"]
        en = strat["english"]
        ur = strat["urdu"]
        ru = strat["roman_urdu"]
        print(f"OVERALL ANSWERABLE (N={ov['query_count']}): Hit@1={ov['hit_at_1']:.4f}, Hit@3={ov['hit_at_3']:.4f}, Hit@5={ov['hit_at_5']:.4f}, Hit@10={ov['hit_at_10']:.4f}, MRR@10={ov['mrr_at_10']:.4f}, Zero-Overlap={ov['zero_overlap_count']}/{ov['query_count']} ({ov['zero_overlap_pct']}%)")
        print(f"ENGLISH            (N={en['query_count']}): Hit@1={en['hit_at_1']:.4f}, Hit@3={en['hit_at_3']:.4f}, Hit@5={en['hit_at_5']:.4f}, Hit@10={en['hit_at_10']:.4f}, MRR@10={en['mrr_at_10']:.4f}, Zero-Overlap={en['zero_overlap_count']}/{en['query_count']} ({en['zero_overlap_pct']}%)")
        print(f"URDU               (N={ur['query_count']}): Hit@1={ur['hit_at_1']:.4f}, Hit@3={ur['hit_at_3']:.4f}, Hit@5={ur['hit_at_5']:.4f}, Hit@10={ur['hit_at_10']:.4f}, MRR@10={ur['mrr_at_10']:.4f}, Zero-Overlap={ur['zero_overlap_count']}/{ur['query_count']} ({ur['zero_overlap_pct']}%)")
        print(f"ROMAN URDU         (N={ru['query_count']}): Hit@1={ru['hit_at_1']:.4f}, Hit@3={ru['hit_at_3']:.4f}, Hit@5={ru['hit_at_5']:.4f}, Hit@10={ru['hit_at_10']:.4f}, MRR@10={ru['mrr_at_10']:.4f}, Zero-Overlap={ru['zero_overlap_count']}/{ru['query_count']} ({ru['zero_overlap_pct']}%)")
    print("=" * 80)


if __name__ == "__main__":
    main()
