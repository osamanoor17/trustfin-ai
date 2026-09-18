"""Offline Unit Tests for SBP Document Chunking & Provenance Pipeline (Phase 1D)."""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import pytest
from pydantic import ValidationError

from app.schemas.chunk import ChunkingManifestEntry, ChunkRecord
from app.schemas.processed_document import ExtractionStatus, ProcessedPage
from scripts.chunk_documents import (
    chunk_strategy_fixed_window,
    chunk_strategy_page,
    chunk_strategy_page_aware_window,
    compute_sha256,
    count_words,
    run_chunking_pipeline,
    tokenize_words,
    validate_strategy_coverage,
)


def create_sample_pages() -> Dict[str, List[ProcessedPage]]:
    """Helper to construct synthetic ProcessedPage records across 2 documents."""
    page_1_1 = ProcessedPage(
        document_id="PK-SBP-TEST-2025-0001",
        source_file_name="test1.pdf",
        source_sha256="a" * 64,
        page_number=1,
        raw_text="Page 1 cover title word1 word2 word3",
        normalized_text="Page 1 cover title word1 word2 word3",
        character_count=35,
        word_count=6,
        contains_table_like_content=False,
        extraction_status=ExtractionStatus.LOW_TEXT,
    )
    # Page 1_2 with 350 words to test splitting
    text_350_words = " ".join([f"w{i}" for i in range(1, 351)])
    page_1_2 = ProcessedPage(
        document_id="PK-SBP-TEST-2025-0001",
        source_file_name="test1.pdf",
        source_sha256="a" * 64,
        page_number=2,
        raw_text=text_350_words,
        normalized_text=text_350_words,
        character_count=len(text_350_words),
        word_count=350,
        contains_table_like_content=True,
        extraction_status=ExtractionStatus.EXTRACTED,
    )

    page_2_1 = ProcessedPage(
        document_id="PK-SBP-TEST-2025-0002",
        source_file_name="test2.pdf",
        source_sha256="b" * 64,
        page_number=1,
        raw_text="Doc 2 Page 1 text " + " ".join([f"item{i}" for i in range(100)]),
        normalized_text="Doc 2 Page 1 text " + " ".join([f"item{i}" for i in range(100)]),
        character_count=500,
        word_count=104,
        contains_table_like_content=False,
        extraction_status=ExtractionStatus.EXTRACTED,
    )

    return {
        "PK-SBP-TEST-2025-0001": [page_1_1, page_1_2],
        "PK-SBP-TEST-2025-0002": [page_2_1],
    }


def test_deterministic_chunk_ids():
    """Test 1: Chunk IDs follow deterministic format {doc_id}::{strategy}::{chunk_index:06d}."""
    sample = create_sample_pages()
    chunks = chunk_strategy_page(sample)
    assert chunks[0].chunk_id == "PK-SBP-TEST-2025-0001::page_v1::000000"
    assert chunks[1].chunk_id == "PK-SBP-TEST-2025-0001::page_v1::000001"
    assert chunks[2].chunk_id == "PK-SBP-TEST-2025-0002::page_v1::000000"


def test_page_strategy_preserves_page_boundaries():
    """Test 2: PAGE strategy preserves 1 page = 1 chunk without merging."""
    sample = create_sample_pages()
    chunks = chunk_strategy_page(sample)
    assert len(chunks) == 3
    assert chunks[0].page_start == 1 and chunks[0].page_end == 1
    assert chunks[1].page_start == 2 and chunks[1].page_end == 2


def test_fixed_window_respects_target_size():
    """Test 3: Fixed window strategy enforces maximum target word size."""
    sample = create_sample_pages()
    chunks = chunk_strategy_fixed_window(sample, target_words=300, overlap_words=50)
    for c in chunks:
        assert c.word_count <= 300


def test_fixed_overlap_behaves_correctly():
    """Test 4: Fixed window strategy creates exact 50-word overlap between consecutive full chunks."""
    sample = create_sample_pages()
    chunks = chunk_strategy_fixed_window(sample, target_words=300, overlap_words=50)

    # Filter chunks for document 1
    doc1_chunks = [c for c in chunks if c.document_id == "PK-SBP-TEST-2025-0001"]
    assert len(doc1_chunks) >= 2

    c0_words = tokenize_words(doc1_chunks[0].text)
    c1_words = tokenize_words(doc1_chunks[1].text)

    # The last 50 words of c0 should match the first 50 words of c1
    overlap_from_c0 = c0_words[-50:]
    overlap_from_c1 = c1_words[:50]
    assert overlap_from_c0 == overlap_from_c1


def test_no_cross_document_chunks():
    """Test 5: Chunks never combine text across different documents."""
    sample = create_sample_pages()
    for strat_func in [chunk_strategy_page, chunk_strategy_fixed_window, chunk_strategy_page_aware_window]:
        chunks = strat_func(sample)
        for c in chunks:
            # All source pages must belong strictly to one document_id
            doc_pages = [p.page_number for p in sample[c.document_id]]
            assert all(p in doc_pages for p in c.source_pages)


def test_fixed_window_page_provenance_mapping():
    """Test 6: Fixed window page provenance accurately maps contributing pages."""
    sample = create_sample_pages()
    chunks = chunk_strategy_fixed_window(sample, target_words=300, overlap_words=50)
    c0 = chunks[0]
    # c0 spans words from Page 1 (6 words) and Page 2 (294 words)
    assert c0.page_start == 1
    assert c0.page_end == 2
    assert c0.source_pages == [1, 2]


def test_page_aware_provenance_mapping():
    """Test 7: Page-aware strategy records exact source pages."""
    sample = create_sample_pages()
    chunks = chunk_strategy_page_aware_window(sample, target_words=300, overlap_words=50)
    for c in chunks:
        assert c.source_pages == sorted(list(set(c.source_pages)))
        assert c.page_start == min(c.source_pages)
        assert c.page_end == max(c.source_pages)


def test_source_pages_sorted_unique():
    """Test 8: source_pages is always sorted and unique."""
    sample = create_sample_pages()
    for strat_func in [chunk_strategy_page, chunk_strategy_fixed_window, chunk_strategy_page_aware_window]:
        chunks = strat_func(sample)
        for c in chunks:
            assert c.source_pages == sorted(list(set(c.source_pages)))


def test_page_start_page_end_consistency():
    """Test 9: page_start equals min(source_pages) and page_end equals max(source_pages)."""
    sample = create_sample_pages()
    for strat_func in [chunk_strategy_page, chunk_strategy_fixed_window, chunk_strategy_page_aware_window]:
        chunks = strat_func(sample)
        for c in chunks:
            assert c.page_start == min(c.source_pages)
            assert c.page_end == max(c.source_pages)


def test_low_text_page_preservation():
    """Test 10: LOW_TEXT page status is preserved in chunk metadata."""
    sample = create_sample_pages()
    chunks = chunk_strategy_page(sample)
    # Page 1 of Doc 1 is LOW_TEXT
    c_low = [c for c in chunks if c.page_start == 1 and c.document_id == "PK-SBP-TEST-2025-0001"][0]
    assert c_low.is_low_text is True


def test_empty_page_does_not_create_empty_chunk():
    """Test 11: Empty pages do not emit 0-word chunks."""
    sample = create_sample_pages()
    empty_page = ProcessedPage(
        document_id="PK-SBP-TEST-2025-0001",
        source_file_name="test1.pdf",
        source_sha256="a" * 64,
        page_number=3,
        raw_text="   \n",
        normalized_text="",
        character_count=0,
        word_count=0,
        contains_table_like_content=False,
        extraction_status=ExtractionStatus.EMPTY_TEXT,
    )
    sample["PK-SBP-TEST-2025-0001"].append(empty_page)

    for strat_func in [chunk_strategy_page, chunk_strategy_fixed_window, chunk_strategy_page_aware_window]:
        chunks = strat_func(sample)
        for c in chunks:
            assert c.word_count >= 1
            assert len(c.text.strip()) > 0


def test_table_like_metadata_propagation():
    """Test 12: contains_table_like_content is True if ANY contributing page had table signal."""
    sample = create_sample_pages()
    chunks = chunk_strategy_fixed_window(sample, target_words=300, overlap_words=50)
    # Chunk 0 spans Page 1 (table=False) and Page 2 (table=True) -> result must be True
    c0 = chunks[0]
    assert c0.contains_table_like_content is True


def test_deterministic_strategy_ordering():
    """Test 13: Chunk indices are 0-based and increment sequentially per document."""
    sample = create_sample_pages()
    for strat_func in [chunk_strategy_page, chunk_strategy_fixed_window, chunk_strategy_page_aware_window]:
        chunks = strat_func(sample)
        doc1_indices = [c.chunk_index for c in chunks if c.document_id == "PK-SBP-TEST-2025-0001"]
        assert doc1_indices == list(range(len(doc1_indices)))


def test_chunk_schema_validation():
    """Test 14: Pydantic ChunkRecord validation rules."""
    valid_record = ChunkRecord(
        chunk_id="PK-SBP-TEST::page_v1::000000",
        strategy="page_v1",
        document_id="PK-SBP-TEST",
        chunk_index=0,
        text="Valid chunk text",
        word_count=3,
        character_count=16,
        page_start=1,
        page_end=2,
        source_pages=[1, 2],
        source_sha256="a" * 64,
        source_file_name="test.pdf",
        contains_table_like_content=False,
        is_low_text=False,
    )
    assert valid_record.word_count == 3

    # Test invalid page_end < page_start
    with pytest.raises(ValidationError):
        ChunkRecord(
            chunk_id="PK-SBP-TEST::page_v1::000000",
            strategy="page_v1",
            document_id="PK-SBP-TEST",
            chunk_index=0,
            text="Test",
            word_count=1,
            character_count=4,
            page_start=5,
            page_end=2,
            source_pages=[2, 5],
            source_sha256="a" * 64,
            source_file_name="test.pdf",
        )

    # Test unsorted source_pages
    with pytest.raises(ValidationError):
        ChunkRecord(
            chunk_id="PK-SBP-TEST::page_v1::000000",
            strategy="page_v1",
            document_id="PK-SBP-TEST",
            chunk_index=0,
            text="Test",
            word_count=1,
            character_count=4,
            page_start=1,
            page_end=2,
            source_pages=[2, 1],
            source_sha256="a" * 64,
            source_file_name="test.pdf",
        )


def test_invalid_sha_rejection(monkeypatch, tmp_path):
    """Test 15: Invalid input corpus SHA-256 triggers error."""
    bad_file = tmp_path / "sbp_pages.jsonl"
    bad_file.write_text("invalid JSON content\n")

    monkeypatch.setattr("scripts.chunk_documents.INPUT_PAGE_CORPUS_PATH", bad_file)

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        run_chunking_pipeline()


def test_complete_source_coverage():
    """Test 16: Position-aware complete source coverage across all 3 strategies."""
    sample = create_sample_pages()
    for strat_name, strat_func in [
        ("page_v1", chunk_strategy_page),
        ("fixed_300w_50o_v1", lambda p: chunk_strategy_fixed_window(p, 300, 50)),
        ("page_aware_300w_50o_v1", lambda p: chunk_strategy_page_aware_window(p, 300, 50)),
    ]:
        chunks = strat_func(sample)
        assert validate_strategy_coverage(sample, chunks, strat_name) is True


def test_coverage_validator_detects_dropped_repeated_token():
    """Test 18: Position-aware coverage validator fails if a repeated token occurrence is dropped."""
    pages = {
        "DOC1": [
            ProcessedPage(
                document_id="DOC1",
                page_number=1,
                source_sha256="a" * 64,
                source_file_name="test.pdf",
                raw_text="bank account bank customer",
                normalized_text="bank account bank customer",
                character_count=26,
                word_count=4,
            )
        ]
    }

    # Chunks omitting second "bank" occurrence (token position 2)
    incomplete_chunks = [
        ChunkRecord(
            chunk_id="DOC1::test::000000",
            strategy="test",
            document_id="DOC1",
            chunk_index=0,
            text="bank account",
            word_count=2,
            character_count=12,
            page_start=1,
            page_end=1,
            source_pages=[1],
            source_sha256="a" * 64,
            source_file_name="test.pdf",
        ),
        ChunkRecord(
            chunk_id="DOC1::test::000001",
            strategy="test",
            document_id="DOC1",
            chunk_index=1,
            text="customer",
            word_count=1,
            character_count=8,
            page_start=1,
            page_end=1,
            source_pages=[1],
            source_sha256="a" * 64,
            source_file_name="test.pdf",
        ),
    ]

    assert validate_strategy_coverage(pages, incomplete_chunks, "test") is False


def test_coverage_validator_detects_token_reordering():
    """Test 19: Sequence validator fails if chunk text tokens are reordered."""
    pages = {
        "DOC1": [
            ProcessedPage(
                document_id="DOC1",
                page_number=1,
                source_sha256="a" * 64,
                source_file_name="test.pdf",
                raw_text="bank account bank customer",
                normalized_text="bank account bank customer",
                character_count=26,
                word_count=4,
            )
        ]
    }

    reordered_chunks = [
        ChunkRecord(
            chunk_id="DOC1::test::000000",
            strategy="test",
            document_id="DOC1",
            chunk_index=0,
            text="account bank bank customer",
            word_count=4,
            character_count=26,
            page_start=1,
            page_end=1,
            source_pages=[1],
            source_sha256="a" * 64,
            source_file_name="test.pdf",
        )
    ]

    assert validate_strategy_coverage(pages, reordered_chunks, "test") is False


def test_coverage_validator_passes_valid_overlapping_chunks():
    """Test 20: Position-aware coverage validator succeeds on valid overlapping chunks."""
    pages = {
        "DOC1": [
            ProcessedPage(
                document_id="DOC1",
                page_number=1,
                source_sha256="a" * 64,
                source_file_name="test.pdf",
                raw_text="bank account bank customer",
                normalized_text="bank account bank customer",
                character_count=26,
                word_count=4,
            )
        ]
    }

    valid_overlapping_chunks = [
        ChunkRecord(
            chunk_id="DOC1::test::000000",
            strategy="test",
            document_id="DOC1",
            chunk_index=0,
            text="bank account bank",
            word_count=3,
            character_count=17,
            page_start=1,
            page_end=1,
            source_pages=[1],
            source_sha256="a" * 64,
            source_file_name="test.pdf",
        ),
        ChunkRecord(
            chunk_id="DOC1::test::000001",
            strategy="test",
            document_id="DOC1",
            chunk_index=1,
            text="bank customer",
            word_count=2,
            character_count=13,
            page_start=1,
            page_end=1,
            source_pages=[1],
            source_sha256="a" * 64,
            source_file_name="test.pdf",
        ),
    ]

    assert validate_strategy_coverage(pages, valid_overlapping_chunks, "test") is True


def test_identical_input_produces_byte_identical_output(tmp_path, monkeypatch):
    """Test 17: Consecutive runs on identical input produce byte-identical SHA-256 digests."""
    sample = create_sample_pages()
    chunks1 = chunk_strategy_fixed_window(sample, 300, 50)
    chunks2 = chunk_strategy_fixed_window(sample, 300, 50)

    json1 = "\n".join(c.model_dump_json() for c in chunks1)
    json2 = "\n".join(c.model_dump_json() for c in chunks2)

    sha1 = compute_sha256_bytes(json1.encode("utf-8"))
    sha2 = compute_sha256_bytes(json2.encode("utf-8"))

    assert sha1 == sha2


def compute_sha256_bytes(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest().lower()

