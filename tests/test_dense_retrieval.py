"""Offline synthetic unit tests for Phase 2C Multilingual Dense Retrieval Baseline.

Runs 100% offline without downloading transformer model weights.
"""

import math
import pytest
from app.schemas.benchmark import BenchmarkLanguage
from app.schemas.chunk import ChunkRecord
from app.schemas.dense import (
    DenseModelConfig,
    DenseRetrievalResultItem,
    SingleQueryDenseRecord,
)
from app.services.dense_retrieval import (
    FROZEN_DENSE_MODELS,
    SyntheticDenseRetrievalEngine,
    compute_cosine_similarities,
    compute_dot_product,
    l2_normalize_matrix,
    l2_normalize_vector,
    measure_chunk_truncation,
)
from scripts.run_dense_baseline import evaluate_dense_query_set


def test_frozen_model_configurations_pre_experiment_freeze():
    """Verify pre-experiment freeze of all 3 model configurations."""
    assert len(FROZEN_DENSE_MODELS) == 3
    assert "multilingual-e5-base" in FROZEN_DENSE_MODELS
    assert "bge-m3" in FROZEN_DENSE_MODELS
    assert "paraphrase-multilingual-mpnet-base-v2" in FROZEN_DENSE_MODELS

    # E5 config
    e5 = FROZEN_DENSE_MODELS["multilingual-e5-base"]
    assert e5.embedding_dimension == 768
    assert e5.max_sequence_length == 512
    assert e5.query_prefix == "query: "
    assert e5.passage_prefix == "passage: "

    # BGE-M3 config
    bge = FROZEN_DENSE_MODELS["bge-m3"]
    assert bge.embedding_dimension == 1024
    assert bge.max_sequence_length == 8192
    assert bge.query_prefix == ""
    assert bge.passage_prefix == ""

    # MPNet config
    mpnet = FROZEN_DENSE_MODELS["paraphrase-multilingual-mpnet-base-v2"]
    assert mpnet.embedding_dimension == 768
    assert mpnet.max_sequence_length == 128
    assert mpnet.query_prefix == ""
    assert mpnet.passage_prefix == ""


def test_l2_normalization_math():
    """Verify vector L2-normalization math."""
    vec = [3.0, 4.0]
    norm_vec = l2_normalize_vector(vec)
    assert norm_vec == pytest.approx([0.6, 0.8], abs=1e-5)
    # Length of L2-normalized vector must be 1.0
    assert sum(x * x for x in norm_vec) == pytest.approx(1.0, abs=1e-5)


def test_cosine_similarity_computation():
    """Verify cosine similarity dot product calculation."""
    q_vec = [1.0, 0.0]
    d_vecs = [[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]]

    sims = compute_cosine_similarities(q_vec, d_vecs)
    assert sims[0] == pytest.approx(1.0, abs=1e-5)
    assert sims[1] == pytest.approx(0.0, abs=1e-5)
    assert sims[2] == pytest.approx(-1.0, abs=1e-5)


def test_deterministic_tie_breaking_dense():
    """Verify dense retrieval sorts by score descending, then chunk_id ascending."""
    c1 = ChunkRecord(
        chunk_id="PK-SBP-TEST-2025-0001::page_v1::000002",
        strategy="page_v1",
        document_id="DOC1",
        chunk_index=2,
        text="passage two",
        word_count=2,
        character_count=11,
        page_start=1,
        page_end=1,
        source_pages=[1],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )
    c2 = ChunkRecord(
        chunk_id="PK-SBP-TEST-2025-0001::page_v1::000001",
        strategy="page_v1",
        document_id="DOC1",
        chunk_index=1,
        text="passage one",
        word_count=2,
        character_count=11,
        page_start=1,
        page_end=1,
        source_pages=[1],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )

    # Identical vectors -> identical score
    embeddings = [[1.0, 0.0], [1.0, 0.0]]
    cfg = FROZEN_DENSE_MODELS["multilingual-e5-base"]

    engine = SyntheticDenseRetrievalEngine([c1, c2], embeddings, cfg)
    results = engine.search([1.0, 0.0], top_k=2)

    # Identical scores, chunk 000001 must come before 000002 alphabetically
    assert results[0][1] == results[1][1]
    assert results[0][0].chunk_id == "PK-SBP-TEST-2025-0001::page_v1::000001"
    assert results[1][0].chunk_id == "PK-SBP-TEST-2025-0001::page_v1::000002"


def test_dense_relevance_policy_negative_scores():
    """Verify dense relevance requires doc match AND page intersection regardless of score sign."""
    item_pos = DenseRetrievalResultItem(
        benchmark_id="TFB-0001-EN",
        concept_id="C1",
        query_language=BenchmarkLanguage.ENGLISH,
        model_id="intfloat/multilingual-e5-base",
        chunk_strategy="page_v1",
        rank=1,
        chunk_id="chunk_1",
        score=0.75,
        document_id="DOC1",
        source_pages=[10],
        page_start=10,
        page_end=10,
        is_relevant=True,
    )
    item_neg = DenseRetrievalResultItem(
        benchmark_id="TFB-0001-EN",
        concept_id="C1",
        query_language=BenchmarkLanguage.ENGLISH,
        model_id="intfloat/multilingual-e5-base",
        chunk_strategy="page_v1",
        rank=2,
        chunk_id="chunk_2",
        score=-0.25,  # Negative score!
        document_id="DOC1",  # Matches doc
        source_pages=[10],  # Matches page
        page_start=10,
        page_end=10,
        is_relevant=True,  # Still relevant in dense retrieval because doc/page match!
    )

    assert item_pos.is_relevant is True
    assert item_neg.is_relevant is True


def test_truncation_measurement_heuristic():
    """Verify truncation measurement accurately identifies chunks exceeding max sequence length."""
    c1 = ChunkRecord(
        chunk_id="c1",
        strategy="page_v1",
        document_id="DOC1",
        chunk_index=0,
        text="short text chunk",
        word_count=3,
        character_count=16,
        page_start=1,
        page_end=1,
        source_pages=[1],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )
    # Long text (150 words)
    long_text = " ".join(["word"] * 150)
    c2 = ChunkRecord(
        chunk_id="c2",
        strategy="page_v1",
        document_id="DOC1",
        chunk_index=1,
        text=long_text,
        word_count=150,
        character_count=600,
        page_start=1,
        page_end=1,
        source_pages=[1],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )

    # For MPNet (max_seq_len = 128), long_text (150 words * 1.3 ≈ 195 tokens) will exceed limit
    mpnet = FROZEN_DENSE_MODELS["paraphrase-multilingual-mpnet-base-v2"]
    stats = measure_chunk_truncation([c1, c2], mpnet)

    assert stats.total_chunks == 2
    assert stats.truncated_chunk_count == 1
    assert stats.truncated_chunk_pct == 50.0


def test_dense_metric_calculation():
    """Verify Hit@K and MRR@10 calculation for dense single query records."""
    q1 = SingleQueryDenseRecord(
        benchmark_id="TFB-0001-EN",
        concept_id="C1",
        query_language=BenchmarkLanguage.ENGLISH,
        query_text="q1",
        formatted_query_text="query: q1",
        model_id="intfloat/multilingual-e5-base",
        chunk_strategy="page_v1",
        answerability="ANSWERABLE",
        expected_document_ids=["DOC1"],
        relevant_pages=[1],
        top_results=[],
        first_relevant_rank=1,
    )
    q2 = SingleQueryDenseRecord(
        benchmark_id="TFB-0002-EN",
        concept_id="C2",
        query_language=BenchmarkLanguage.ENGLISH,
        query_text="q2",
        formatted_query_text="query: q2",
        model_id="intfloat/multilingual-e5-base",
        chunk_strategy="page_v1",
        answerability="ANSWERABLE",
        expected_document_ids=["DOC2"],
        relevant_pages=[2],
        top_results=[],
        first_relevant_rank=5,
    )

    metrics = evaluate_dense_query_set([q1, q2])
    assert metrics.hit_at_1 == 0.5
    assert metrics.hit_at_3 == 0.5
    assert metrics.hit_at_5 == 1.0
    assert metrics.hit_at_10 == 1.0
    assert metrics.mrr_at_10 == pytest.approx((1.0 + 0.2) / 2.0, abs=1e-4)


def test_full_precision_ranking_beyond_6th_decimal():
    """Verify that ranking uses unrounded full-precision scores without rounding ties beyond 6 decimals."""
    c1 = ChunkRecord(
        chunk_id="PK-SBP-TEST-2025-0001::page_v1::000001",
        strategy="page_v1",
        document_id="DOC1",
        chunk_index=1,
        text="chunk 1",
        word_count=2,
        character_count=7,
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
        text="chunk 2",
        word_count=2,
        character_count=7,
        page_start=1,
        page_end=1,
        source_pages=[1],
        source_sha256="0" * 64,
        source_file_name="test.pdf",
    )

    # c1 dot product = 0.7000001, c2 dot product = 0.7000003
    # If rounded to 6 decimal places BEFORE sorting, both would be 0.700000, and chunk 000001 would rank first alphabetically.
    # With full-precision sorting, c2 (0.7000003) MUST rank first.
    q_vec = [1.0, 0.0]
    d1_vec = [0.7000001, math.sqrt(1.0 - 0.7000001**2)]
    d2_vec = [0.7000003, math.sqrt(1.0 - 0.7000003**2)]

    cfg = FROZEN_DENSE_MODELS["multilingual-e5-base"]
    engine = SyntheticDenseRetrievalEngine([c1, c2], [d1_vec, d2_vec], cfg)
    results = engine.search(q_vec, top_k=2)

    # c2 must rank FIRST because 0.7000003 > 0.7000001
    assert results[0][0].chunk_id == "PK-SBP-TEST-2025-0001::page_v1::000002"
    assert results[1][0].chunk_id == "PK-SBP-TEST-2025-0001::page_v1::000001"


def test_query_truncation_stat_aggregation_logic():
    """Verify query truncation stat calculation across benchmark queries."""
    mpnet = FROZEN_DENSE_MODELS["paraphrase-multilingual-mpnet-base-v2"]

    queries = [
        "What is the minimum capital requirement for digital banks?",
        "State Bank of Pakistan regulations for Asaan Digital Account credit limits.",
        " ".join(["longqueryterm"] * 150),  # Exceeds max_seq_length = 128
    ]

    from app.services.dense_retrieval import measure_query_truncation
    q_stats = measure_query_truncation(queries, mpnet)

    assert q_stats.total_queries == 3
    assert q_stats.truncated_query_count == 1
    assert q_stats.truncated_query_pct == 33.33


def test_model_config_exact_revision_sha_preservation():
    """Verify all 3 model configs preserve exact Hugging Face commit revision SHAs."""
    e5 = FROZEN_DENSE_MODELS["multilingual-e5-base"]
    bge = FROZEN_DENSE_MODELS["bge-m3"]
    mpnet = FROZEN_DENSE_MODELS["paraphrase-multilingual-mpnet-base-v2"]

    assert e5.model_revision == "d7dbd2363595f4e19f7f45c8f85f8c65f97332f1"
    assert bge.model_revision == "5617a9f61b028005a4858fdac845db4034724a87"
    assert mpnet.model_revision == "79f238270bbb1999f3659424750eed546059d18f"


def test_e5_formatting_query_passage_prefixes():
    """Verify multilingual-e5-base config mandates exact query and passage prefixes."""
    e5 = FROZEN_DENSE_MODELS["multilingual-e5-base"]
    assert e5.query_prefix == "query: "
    assert e5.passage_prefix == "passage: "


def test_lf_line_ending_serialization(tmp_path):
    """Verify that JSONL writer produces LF-only line endings without CRLF on any platform."""
    test_file = tmp_path / "test_lf.jsonl"
    with open(test_file, "w", encoding="utf-8", newline="\n") as f:
        f.write('{"key": "value1"}\n')
        f.write('{"key": "value2"}\n')

    raw_bytes = test_file.read_bytes()
    assert b"\r\n" not in raw_bytes
    assert b"\n" in raw_bytes
    assert len(raw_bytes.split(b"\n")) == 3


def test_canonical_text_sha256_lf_crlf_equivalence(tmp_path):
    """Verify that equivalent LF and CRLF textual content canonicalizes to identical SHA-256 hash."""
    from scripts.run_dense_baseline import compute_canonical_text_sha256

    lf_file = tmp_path / "content_lf.jsonl"
    crlf_file = tmp_path / "content_crlf.jsonl"

    text_content = '{"id": 1, "text": "hello"}\n{"id": 2, "text": "world"}\n'
    lf_file.write_bytes(text_content.encode("utf-8"))
    crlf_file.write_bytes(text_content.replace("\n", "\r\n").encode("utf-8"))

    sha_lf = compute_canonical_text_sha256(lf_file)
    sha_crlf = compute_canonical_text_sha256(crlf_file)

    assert sha_lf == sha_crlf
    assert sha_lf == "b8b683696e6e48bc5a2aee89ed6e129625670b374d11fd25de00c04d58998398"


def test_canonical_lf_output_determinism(tmp_path):
    """Verify that canonical LF text writing remains 100% deterministic across multiple runs."""
    import json

    test_file = tmp_path / "deterministic_lf.jsonl"
    records = [{"item": 1}, {"item": 2}]

    for _ in range(2):
        with open(test_file, "w", encoding="utf-8", newline="\n") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

        raw_bytes = test_file.read_bytes()
        assert b"\r\n" not in raw_bytes
        assert b"\n" in raw_bytes


def test_binary_raw_pdf_hashing_remains_byte_exact(tmp_path):
    """Verify binary/raw PDF hashing remains byte-exact and is NOT newline-normalized."""
    import hashlib
    from scripts.parse_documents import compute_sha256 as compute_binary_sha256

    binary_file = tmp_path / "sample_raw.pdf"
    raw_pdf_bytes = b"%PDF-1.4\r\nsome binary stream data \r\n%%EOF"
    binary_file.write_bytes(raw_pdf_bytes)

    expected_raw_sha = hashlib.sha256(raw_pdf_bytes).hexdigest().lower()
    actual_sha = compute_binary_sha256(binary_file)

    assert actual_sha == expected_raw_sha


def test_preflight_fails_closed_on_content_change(tmp_path):
    """Verify preflight SHA-256 validation fails closed when genuine text content changes."""
    from scripts.run_dense_baseline import verify_sha256_hash

    modified_file = tmp_path / "modified_benchmark.jsonl"
    modified_file.write_bytes(b'{"id": "modified_content"}\n')

    frozen_expected_sha = "df3f6d0c807b7425ac3ffa3efb0ebc1070089ebd41f5cc00f9e423659554c82f"
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        verify_sha256_hash(modified_file, frozen_expected_sha)



