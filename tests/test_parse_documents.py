"""Offline Unit Tests for SBP Document Parsing & Normalization Pipeline (Phase 1C)."""

import json
from pathlib import Path
import tempfile
import pytest
from pydantic import ValidationError

from app.schemas.processed_document import (
    ExtractionStatus,
    ProcessedDocumentManifestEntry,
    ProcessedPage,
)
from scripts.parse_documents import (
    classify_page_extraction_status,
    compute_sha256,
    normalize_text,
    run_parsing_pipeline,
)


def test_conservative_whitespace_normalization():
    """Test 1: Conservative whitespace normalization (CRLF -> LF, line-internal space collapse, blank line cap)."""
    raw_input = "  Header Title \r\n\r\n\r\n  Line 1   with   extra   spaces  \r Line  2 \n\n\n\n Line 3  "
    expected = "Header Title\n\nLine 1 with extra spaces\nLine 2\n\nLine 3"
    result = normalize_text(raw_input)
    assert result == expected


def test_unicode_text_preservation():
    """Test 2: Non-ASCII Unicode characters preservation."""
    unicode_input = "State Bank of Pakistan — Circular № 01 / 2022 © All Rights Reserved €100,000 §4.2."
    result = normalize_text(unicode_input)
    assert "—" in result
    assert "№" in result
    assert "©" in result
    assert "€" in result
    assert "§" in result
    assert result == unicode_input


def test_urdu_text_preservation():
    """Test 3: Urdu script characters preservation."""
    urdu_input = "اسٹیٹ بینک آف پاکستان - کسٹمر آن بورڈنگ فریم ورک 2025"
    result = normalize_text(urdu_input)
    assert "اسٹیٹ بینک آف پاکستان" in result
    assert "کسٹمر آن بورڈنگ فریم ورک" in result
    assert result == urdu_input


def test_punctuation_and_numeric_preservation():
    """Test 4: Punctuation, currency symbols, and numeric tokens preservation."""
    financial_input = "BPRD Circular No. 04 of 2025: Total Capital Adequacy Ratio = 11.50%! Price: Rs. 5,000,000 & USD $1,250.75."
    result = normalize_text(financial_input)
    assert "BPRD Circular No. 04 of 2025:" in result
    assert "11.50%!" in result
    assert "Rs. 5,000,000" in result
    assert "USD $1,250.75." in result
    assert result == financial_input


def test_deterministic_page_ordering():
    """Test 5: Deterministic page ordering (1-based ascending sequence)."""
    p1 = ProcessedPage(
        document_id="PK-SBP-TEST-2025-0001",
        source_file_name="test.pdf",
        source_sha256="a" * 64,
        page_number=1,
        raw_text="Page 1",
        normalized_text="Page 1",
        character_count=6,
        word_count=2,
        contains_table_like_content=False,
        extraction_status=ExtractionStatus.EXTRACTED,
    )
    p2 = ProcessedPage(
        document_id="PK-SBP-TEST-2025-0001",
        source_file_name="test.pdf",
        source_sha256="a" * 64,
        page_number=2,
        raw_text="Page 2",
        normalized_text="Page 2",
        character_count=6,
        word_count=2,
        contains_table_like_content=False,
        extraction_status=ExtractionStatus.EXTRACTED,
    )
    pages = [p2, p1]
    pages.sort(key=lambda p: (p.document_id, p.page_number))
    assert [p.page_number for p in pages] == [1, 2]


class MockPage:
    def __init__(self, has_images=False):
        self._has_images = has_images

    def get_images(self):
        return [("img",)] if self._has_images else []


def test_low_text_classification():
    """Test 6: Low-text classification logic."""
    mock_page = MockPage(has_images=False)
    raw = "Short text"
    norm = normalize_text(raw)
    status = classify_page_extraction_status(raw, norm, mock_page)
    assert status == ExtractionStatus.LOW_TEXT


def test_empty_text_classification():
    """Test 7: Empty-text classification logic."""
    mock_page = MockPage(has_images=False)
    raw = "   \n\n  "
    norm = normalize_text(raw)
    status = classify_page_extraction_status(raw, norm, mock_page)
    assert status == ExtractionStatus.EMPTY_TEXT


def test_sha256_integrity_rejection(monkeypatch, tmp_path):
    """Test 8: Rejection when local raw PDF SHA-256 does not match manifest SHA-256."""
    fake_pdf = tmp_path / "fake.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 Fake content")
    fake_sha = compute_sha256(fake_pdf)
    wrong_sha = "f" * 64

    manifest_file = tmp_path / "sbp_acquisition_manifest.jsonl"
    record = {
        "document_id": "PK-SBP-DIGITAL_BANKING_POLICY-2022-0001",
        "file_name": "fake.pdf",
        "local_raw_path": str(fake_pdf.relative_to(tmp_path)),
        "sha256": wrong_sha,
        "acquisition_status": "ACQUIRED",
    }
    manifest_file.write_text(json.dumps(record) + "\n")

    monkeypatch.setattr("scripts.parse_documents.ACQUISITION_MANIFEST_PATH", manifest_file)
    monkeypatch.setattr("scripts.parse_documents.PROJECT_ROOT", tmp_path)

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        run_parsing_pipeline()


def test_only_acquired_records_eligible(monkeypatch, tmp_path):
    """Test 9: Verify that FAILED_DOCUMENT_IDENTITY or non-acquired records are filtered out."""
    manifest_file = tmp_path / "sbp_acquisition_manifest.jsonl"
    record_failed = {
        "document_id": "PK-SBP-FINTECH_REGULATION-2025-0001",
        "file_name": "failed.pdf",
        "local_raw_path": "data/raw/sbp/failed.pdf",
        "sha256": "0" * 64,
        "acquisition_status": "FAILED_DOCUMENT_IDENTITY",
    }
    manifest_file.write_text(json.dumps(record_failed) + "\n")

    monkeypatch.setattr("scripts.parse_documents.ACQUISITION_MANIFEST_PATH", manifest_file)
    monkeypatch.setattr("scripts.parse_documents.PROJECT_ROOT", tmp_path)

    pages, manifest_entries = run_parsing_pipeline()
    assert len(pages) == 0
    assert len(manifest_entries) == 0


def test_processed_page_schema_validation():
    """Test 10: Pydantic ProcessedPage and ProcessedDocumentManifestEntry schema validations."""
    valid_page = ProcessedPage(
        document_id="PK-SBP-DIGITAL_BANKING_POLICY-2022-0001",
        source_file_name="bprd-circular-no-01-of-2022.pdf",
        source_sha256="517071f7b6e5c0a79d52c4a36f935fac7b85a543a8fe069eb46291a7c39cf282",
        page_number=1,
        raw_text="Test",
        normalized_text="Test",
        character_count=4,
        word_count=1,
        contains_table_like_content=False,
        extraction_status=ExtractionStatus.EXTRACTED,
    )
    assert valid_page.page_number == 1
    assert valid_page.source_sha256 == "517071f7b6e5c0a79d52c4a36f935fac7b85a543a8fe069eb46291a7c39cf282"

    # Test invalid SHA-256 length
    with pytest.raises(ValidationError):
        ProcessedPage(
            document_id="PK-SBP-TEST-2025-0001",
            source_file_name="test.pdf",
            source_sha256="invalid_hash",
            page_number=1,
            raw_text="Test",
            normalized_text="Test",
            character_count=4,
            word_count=1,
            contains_table_like_content=False,
            extraction_status=ExtractionStatus.EXTRACTED,
        )

    # Test invalid page number (< 1)
    with pytest.raises(ValidationError):
        ProcessedPage(
            document_id="PK-SBP-TEST-2025-0001",
            source_file_name="test.pdf",
            source_sha256="a" * 64,
            page_number=0,
            raw_text="Test",
            normalized_text="Test",
            character_count=4,
            word_count=1,
            contains_table_like_content=False,
            extraction_status=ExtractionStatus.EXTRACTED,
        )

    # Test manifest entry validation
    manifest_entry = ProcessedDocumentManifestEntry(
        document_id="PK-SBP-DIGITAL_BANKING_POLICY-2022-0001",
        source_file_name="bprd-circular-no-01-of-2022.pdf",
        source_sha256="517071f7b6e5c0a79d52c4a36f935fac7b85a543a8fe069eb46291a7c39cf282",
        processed_at="2026-09-18T20:00:00Z",
        total_pages=42,
        pages_extracted=42,
        empty_pages=0,
        low_text_pages=1,
        pages_requiring_ocr_review=0,
        pages_with_table_like_content=12,
        total_extracted_characters=50000,
        output_file="data/processed/sbp/sbp_pages.jsonl",
    )
    assert manifest_entry.total_pages == 42
