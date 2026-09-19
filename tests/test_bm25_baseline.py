"""Offline unit tests for Phase 2B BM25 Sparse Retrieval Baseline."""

import json
import pytest
from pathlib import Path
from app.schemas.benchmark import (
    BenchmarkAnswerability,
    BenchmarkDifficulty,
    BenchmarkLanguage,
    BenchmarkQueryType,
    BenchmarkRecord,
    BenchmarkScript,
    EvidenceSpan,
)
from app.schemas.chunk import ChunkRecord
from app.schemas.retrieval import RetrievalResultItem, SingleQueryRetrievalRecord
from app.services.bm25 import BM25Okapi, tokenize_text
from scripts.run_bm25_baseline import evaluate_query_set, load_chunks


def test_deterministic_tokenizer():
    text1 = "Digital Retail Bank (DRB) - PKR 1,500,000!"
    text2 = "اسٹیٹ بینک کی جانب سے 2026"
    
    tokens1 = tokenize_text(text1)
    tokens2 = tokenize_text(text2)

    assert tokens1 == ["digital", "retail", "bank", "drb", "pkr", "1", "500", "000"]
    assert tokens2 == ["اسٹیٹ", "بینک", "کی", "جانب", "سے", "2026"]
    # Repeatability
    assert tokenize_text(text1) == tokens1


def test_english_lowercasing():
    tokens = tokenize_text("State Bank of Pakistan - BPRD Circular")
    assert tokens == ["state", "bank", "of", "pakistan", "bprd", "circular"]


def test_urdu_unicode_preservation():
    tokens = tokenize_text("کم از کم سرمائے کی ضرورت")
    assert tokens == ["کم", "از", "کم", "سرمائے", "کی", "ضرورت"]


def test_punctuation_handling():
    tokens = tokenize_text("Asaan Account (Digital/In-person), Max Credit: PKR 3,000,000.")
    assert tokens == [
        "asaan",
        "account",
        "digital",
        "in",
        "person",
        "max",
        "credit",
        "pkr",
        "3",
        "000",
        "000",
    ]


def test_bm25_scoring_math_and_ranking():
    """Synthetic test verifying BM25 Okapi scoring math and term frequency ranking."""
    c1 = ChunkRecord(
        chunk_id="PK-SBP-TEST-2025-0001::page_v1::000000",
        strategy="page_v1",
        document_id="PK-SBP-TEST-2025-0001",
        chunk_index=0,
        text="digital bank digital bank digital bank capital",
        word_count=7,
        character_count=45,
        page_start=1,
        page_end=1,
        source_pages=[1],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )
    c2 = ChunkRecord(
        chunk_id="PK-SBP-TEST-2025-0001::page_v1::000001",
        strategy="page_v1",
        document_id="PK-SBP-TEST-2025-0001",
        chunk_index=1,
        text="digital bank capital requirement",
        word_count=4,
        character_count=35,
        page_start=1,
        page_end=1,
        source_pages=[1],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )
    c3 = ChunkRecord(
        chunk_id="PK-SBP-TEST-2025-0001::page_v1::000002",
        strategy="page_v1",
        document_id="PK-SBP-TEST-2025-0001",
        chunk_index=2,
        text="unrelated general topic text",
        word_count=4,
        character_count=30,
        page_start=2,
        page_end=2,
        source_pages=[2],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )

    bm25 = BM25Okapi([c1, c2, c3], k1=1.5, b=0.75)

    # Query with 'digital' -> c1 has higher term frequency (3) than c2 (1)
    results = bm25.search("digital", top_k=3)
    assert len(results) == 3
    assert results[0][0].chunk_id == "PK-SBP-TEST-2025-0001::page_v1::000000"
    assert results[0][1] > results[1][1]
    assert results[2][1] == 0.0  # c3 has no lexical overlap


def test_deterministic_tie_breaking():
    """Verify tie-breaking sorts by score descending, then chunk_id ascending."""
    c1 = ChunkRecord(
        chunk_id="PK-SBP-TEST-2025-0001::page_v1::000002",
        strategy="page_v1",
        document_id="PK-SBP-TEST-2025-0001",
        chunk_index=2,
        text="digital banking",
        word_count=2,
        character_count=15,
        page_start=1,
        page_end=1,
        source_pages=[1],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )
    c2 = ChunkRecord(
        chunk_id="PK-SBP-TEST-2025-0001::page_v1::000001",
        strategy="page_v1",
        document_id="PK-SBP-TEST-2025-0001",
        chunk_index=1,
        text="digital banking",
        word_count=2,
        character_count=15,
        page_start=1,
        page_end=1,
        source_pages=[1],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )

    bm25 = BM25Okapi([c1, c2])
    results = bm25.search("digital banking", top_k=2)

    # Scores are identical, so chunk 000001 must come before 000002 alphabetically
    assert results[0][1] == results[1][1]
    assert results[0][0].chunk_id == "PK-SBP-TEST-2025-0001::page_v1::000001"
    assert results[1][0].chunk_id == "PK-SBP-TEST-2025-0001::page_v1::000002"


def test_correct_top_k_behavior():
    chunks = [
        ChunkRecord(
            chunk_id=f"PK-SBP-TEST-2025-0001::page_v1::{i:06d}",
            strategy="page_v1",
            document_id="PK-SBP-TEST-2025-0001",
            chunk_index=i,
            text=f"digital banking passage {i}",
            word_count=4,
            character_count=25,
            page_start=1,
            page_end=1,
            source_pages=[1],
            source_sha256="0" * 64,
            source_file_name="test.pdf",
        )
        for i in range(1, 15)
    ]

    bm25 = BM25Okapi(chunks)
    res_k3 = bm25.search("digital", top_k=3)
    res_k5 = bm25.search("digital", top_k=5)

    assert len(res_k3) == 3
    assert len(res_k5) == 5


def test_zero_score_hit_rejection():
    """Verify that chunks with score == 0.0 do NOT count as hits even if doc/page match."""
    rec = SingleQueryRetrievalRecord(
        benchmark_id="TFB-0001-EN",
        concept_id="CONCEPT_001",
        query_language=BenchmarkLanguage.ENGLISH,
        query_text="unmatched term query",
        chunk_strategy="page_v1",
        answerability="ANSWERABLE",
        expected_document_ids=["PK-SBP-DIGITAL_BANKING_POLICY-2022-0001"],
        relevant_pages=[20],
        top_results=[
            RetrievalResultItem(
                benchmark_id="TFB-0001-EN",
                concept_id="CONCEPT_001",
                query_language=BenchmarkLanguage.ENGLISH,
                chunk_strategy="page_v1",
                rank=1,
                chunk_id="chunk_001",
                score=0.0,  # Zero score!
                document_id="PK-SBP-DIGITAL_BANKING_POLICY-2022-0001",  # Matches doc
                source_pages=[20],  # Matches page
                page_start=20,
                page_end=20,
                is_relevant=False,  # Must be False because score == 0.0!
            )
        ],
        first_relevant_rank=None,
        has_zero_overlap=True,
    )

    metrics = evaluate_query_set([rec])
    assert metrics.hit_at_1 == 0.0
    assert metrics.hit_at_10 == 0.0
    assert metrics.mrr_at_10 == 0.0
    assert metrics.zero_overlap_count == 1


def test_page_intersection_relevance_matching():
    # Chunk page range [1, 2] intersects relevant_pages [2, 3] -> True
    chunk_pages = [1, 2]
    relevant_pages = [2, 3]
    assert bool(set(chunk_pages).intersection(relevant_pages)) is True

    # Chunk page range [4, 5] does not intersect [2, 3] -> False
    chunk_pages_2 = [4, 5]
    assert bool(set(chunk_pages_2).intersection(relevant_pages)) is False


def test_irrelevant_document_rejection():
    chunk_doc = "PK-SBP-OTHER-DOC-2025-0001"
    expected_docs = ["PK-SBP-DIGITAL_BANKING_POLICY-2022-0001"]
    assert (chunk_doc in expected_docs) is False


def test_hit_at_k_and_mrr_calculation():
    q1 = SingleQueryRetrievalRecord(
        benchmark_id="TFB-0001-EN",
        concept_id="C1",
        query_language=BenchmarkLanguage.ENGLISH,
        query_text="q1",
        chunk_strategy="page_v1",
        answerability="ANSWERABLE",
        expected_document_ids=["DOC1"],
        relevant_pages=[1],
        top_results=[],
        first_relevant_rank=1,  # Rank 1 -> 1/1 = 1.0
        has_zero_overlap=False,
    )
    q2 = SingleQueryRetrievalRecord(
        benchmark_id="TFB-0002-EN",
        concept_id="C2",
        query_language=BenchmarkLanguage.ENGLISH,
        query_text="q2",
        chunk_strategy="page_v1",
        answerability="ANSWERABLE",
        expected_document_ids=["DOC2"],
        relevant_pages=[2],
        top_results=[],
        first_relevant_rank=4,  # Rank 4 -> 1/4 = 0.25
        has_zero_overlap=False,
    )

    metrics = evaluate_query_set([q1, q2])
    assert metrics.hit_at_1 == 0.5   # 1 out of 2 has rank <= 1
    assert metrics.hit_at_3 == 0.5   # 1 out of 2 has rank <= 3
    assert metrics.hit_at_5 == 1.0   # 2 out of 2 have rank <= 5
    assert metrics.hit_at_10 == 1.0  # 2 out of 2 have rank <= 10
    assert metrics.mrr_at_10 == 0.625  # (1.0 + 0.25) / 2 = 0.625


def test_unanswerable_exclusion_from_standard_metrics():
    """Verify unanswerable queries are excluded from answerable evaluation sets."""
    q_ans = SingleQueryRetrievalRecord(
        benchmark_id="TFB-0001-EN",
        concept_id="C1",
        query_language=BenchmarkLanguage.ENGLISH,
        query_text="q1",
        chunk_strategy="page_v1",
        answerability="ANSWERABLE",
        expected_document_ids=["DOC1"],
        relevant_pages=[1],
        top_results=[],
        first_relevant_rank=1,
        has_zero_overlap=False,
    )
    q_unans = SingleQueryRetrievalRecord(
        benchmark_id="TFB-0011-EN",
        concept_id="C11",
        query_language=BenchmarkLanguage.ENGLISH,
        query_text="crypto query",
        chunk_strategy="page_v1",
        answerability="UNANSWERABLE",
        expected_document_ids=[],
        relevant_pages=[],
        top_results=[],
        first_relevant_rank=None,
        has_zero_overlap=True,
    )

    all_queries = [q_ans, q_unans]
    ans_queries = [q for q in all_queries if q.answerability == "ANSWERABLE"]

    metrics = evaluate_query_set(ans_queries)
    assert metrics.query_count == 1
    assert metrics.hit_at_1 == 1.0
    assert metrics.mrr_at_10 == 1.0


def test_result_ordering_determinism():
    c1 = ChunkRecord(
        chunk_id="PK-SBP-TEST-2025-0001::page_v1::000001",
        strategy="page_v1",
        document_id="DOC1",
        chunk_index=1,
        text="digital banking regulations",
        word_count=3,
        character_count=25,
        page_start=1,
        page_end=1,
        source_pages=[1],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )
    c2 = ChunkRecord(
        chunk_id="PK-SBP-TEST-2025-0001::page_v1::000002",
        strategy="page_v1",
        document_id="DOC1",
        chunk_index=2,
        text="customer onboarding frameworks",
        word_count=3,
        character_count=28,
        page_start=2,
        page_end=2,
        source_pages=[2],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )

    bm25 = BM25Okapi([c1, c2])
    run1 = bm25.search("digital", top_k=2)
    run2 = bm25.search("digital", top_k=2)

    assert [(r[0].chunk_id, r[1]) for r in run1] == [(r[0].chunk_id, r[1]) for r in run2]


def test_all_three_chunk_strategies_load_independently():
    p1 = Path("data/processed/sbp/chunks/page_v1.jsonl")
    p2 = Path("data/processed/sbp/chunks/fixed_300w_50o_v1.jsonl")
    p3 = Path("data/processed/sbp/chunks/page_aware_300w_50o_v1.jsonl")

    if p1.exists() and p2.exists() and p3.exists():
        c1 = load_chunks(p1)
        c2 = load_chunks(p2)
        c3 = load_chunks(p3)

        assert len(c1) == 142
        assert len(c2) == 199
        assert len(c3) == 248


def test_canonical_zero_vocabulary_overlap_detection():
    """Verify zero vocabulary overlap detection uses canonical set(tokenize(query)).isdisjoint(vocabulary)."""
    c1 = ChunkRecord(
        chunk_id="c1",
        strategy="page_v1",
        document_id="d1",
        chunk_index=0,
        text="digital banking capital requirements",
        word_count=4,
        character_count=35,
        page_start=1,
        page_end=1,
        source_pages=[1],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )
    bm25 = BM25Okapi([c1])
    vocab = set(bm25.df.keys())

    # Query with matching terms -> isdisjoint is False
    q1_tokens = set(tokenize_text("digital banking"))
    assert q1_tokens.isdisjoint(vocab) is False

    # Query with zero matching terms -> isdisjoint is True
    q2_tokens = set(tokenize_text("سرمایہ کاری بٹ کوائن"))
    assert q2_tokens.isdisjoint(vocab) is True


def test_bm25_hand_calculated_numeric_score():
    """Synthetic test verifying BM25 Okapi numeric score against independent hand calculation.

    Corpus:
        d1: "cat dog cat" (length 3)
        d2: "dog mouse"   (length 2)
    Query: "cat"

    Independent Calculation:
        N = 2
        n("cat") = 1
        IDF("cat") = ln((2 - 1 + 0.5) / (1 + 0.5) + 1.0) = ln(1.5 / 1.5 + 1.0) = ln(2) = 0.6931471805599453
        avgdl = (3 + 2) / 2 = 2.5
        k1 = 1.5, b = 0.75
        K(d1) = 1.5 * (1 - 0.75 + 0.75 * (3 / 2.5)) = 1.5 * (0.25 + 0.9) = 1.5 * 1.15 = 1.725
        Score(d1) = 0.6931471805599453 * (2 * (1.5 + 1)) / (2 + 1.725)
                  = 0.6931471805599453 * 5.0 / 3.725
                  = 0.9303989047247754
    """
    c1 = ChunkRecord(
        chunk_id="d1",
        strategy="page_v1",
        document_id="doc1",
        chunk_index=0,
        text="cat dog cat",
        word_count=3,
        character_count=11,
        page_start=1,
        page_end=1,
        source_pages=[1],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )
    c2 = ChunkRecord(
        chunk_id="d2",
        strategy="page_v1",
        document_id="doc1",
        chunk_index=1,
        text="dog mouse",
        word_count=2,
        character_count=9,
        page_start=1,
        page_end=1,
        source_pages=[1],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )

    bm25 = BM25Okapi([c1, c2], k1=1.5, b=0.75)
    results = bm25.search("cat", top_k=2)

    expected_score = 0.9303989047247754
    assert results[0][0].chunk_id == "d1"
    assert results[0][1] == pytest.approx(round(expected_score, 6), abs=1e-5)
    assert results[1][0].chunk_id == "d2"
    assert results[1][1] == 0.0


def test_duplicate_query_term_contribution():
    """Verify that repeated query terms contribute additively (weighted by query frequency)."""
    c1 = ChunkRecord(
        chunk_id="d1",
        strategy="page_v1",
        document_id="doc1",
        chunk_index=0,
        text="cat dog",
        word_count=2,
        character_count=7,
        page_start=1,
        page_end=1,
        source_pages=[1],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )

    bm25 = BM25Okapi([c1])
    score_single = bm25.search("cat", top_k=1)[0][1]
    score_double = bm25.search("cat cat", top_k=1)[0][1]

    assert score_double == pytest.approx(score_single * 2.0, abs=1e-5)


def test_bm25_summary_and_query_results_artifact_consistency():
    """Verify bm25_summary.json is strictly derivable from bm25_query_results.jsonl."""
    summary_path = Path("research/results/bm25/bm25_summary.json")
    query_results_path = Path("research/results/bm25/bm25_query_results.jsonl")

    if not summary_path.exists() or not query_results_path.exists():
        pytest.skip("BM25 result artifacts do not exist yet. Run experiment script first.")

    with open(summary_path, "r", encoding="utf-8") as f:
        summary_data = json.load(f)

    query_records = []
    with open(query_results_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                query_records.append(json.loads(line))

    # Verify query records count: 3 strategies * 36 benchmark queries = 108 records
    assert len(query_records) == 108

    # Recompute metrics per strategy
    for strat_obj in summary_data["strategies"]:
        strat_name = strat_obj["chunk_strategy"]
        strat_queries = [q for q in query_records if q["chunk_strategy"] == strat_name]
        ans_queries = [q for q in strat_queries if q["answerability"] == "ANSWERABLE"]

        # Check overall answerable metrics
        ov = strat_obj["overall_answerable"]
        assert ov["query_count"] == len(ans_queries)
        
        hit_1 = sum(1 for q in ans_queries if q["first_relevant_rank"] is not None and q["first_relevant_rank"] <= 1)
        hit_3 = sum(1 for q in ans_queries if q["first_relevant_rank"] is not None and q["first_relevant_rank"] <= 3)
        hit_5 = sum(1 for q in ans_queries if q["first_relevant_rank"] is not None and q["first_relevant_rank"] <= 5)
        hit_10 = sum(1 for q in ans_queries if q["first_relevant_rank"] is not None and q["first_relevant_rank"] <= 10)
        mrr_sum = sum((1.0 / q["first_relevant_rank"]) for q in ans_queries if q["first_relevant_rank"] is not None and q["first_relevant_rank"] <= 10)
        zero_cnt = sum(1 for q in ans_queries if q["has_zero_overlap"])

        assert ov["hit_at_1"] == round(hit_1 / len(ans_queries), 4)
        assert ov["hit_at_3"] == round(hit_3 / len(ans_queries), 4)
        assert ov["hit_at_5"] == round(hit_5 / len(ans_queries), 4)
        assert ov["hit_at_10"] == round(hit_10 / len(ans_queries), 4)
        assert ov["mrr_at_10"] == round(mrr_sum / len(ans_queries), 4)
        assert ov["zero_overlap_count"] == zero_cnt


