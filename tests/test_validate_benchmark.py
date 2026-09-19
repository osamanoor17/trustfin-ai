"""Offline unit tests for Phase 2A FinUrdu retrieval benchmark validator."""

import json
import pytest
from pathlib import Path
from scripts.validate_benchmark import validate_benchmark_file
from app.schemas.benchmark import (
    BenchmarkRecord,
    BenchmarkLanguage,
    BenchmarkScript,
    BenchmarkAnswerability,
    BenchmarkDifficulty,
    BenchmarkQueryType,
    EvidenceSpan,
)

SAMPLE_DOC_1 = "PK-SBP-DIGITAL_BANKING_POLICY-2022-0001"
SAMPLE_DOC_2 = "PK-SBP-AML_KYC_GUIDANCE-2025-0001"
SAMPLE_DOC_3 = "PK-SBP-AML_KYC_GUIDANCE-2026-0001"
SAMPLE_DOC_4 = "PK-SBP-CONSUMER_GUIDANCE-2025-0001"


@pytest.fixture
def mock_pages_file(tmp_path):
    """Create a temporary normalized pages file for test verification."""
    pages_path = tmp_path / "mock_pages.jsonl"
    pages_data = [
        {
            "document_id": SAMPLE_DOC_1,
            "page_number": 1,
            "normalized_text": "Digital banking framework policy guidelines.",
        },
        {
            "document_id": SAMPLE_DOC_2,
            "page_number": 1,
            "normalized_text": "Customer onboarding instructions and KYC requirements.",
        },
        {
            "document_id": SAMPLE_DOC_3,
            "page_number": 1,
            "normalized_text": "Roshan Digital Account expansion for non-residents.",
        },
        {
            "document_id": SAMPLE_DOC_4,
            "page_number": 1,
            "normalized_text": "Consumer protection guidelines and complaint resolution.",
        },
    ]
    with open(pages_path, "w", encoding="utf-8") as f:
        for p in pages_data:
            f.write(json.dumps(p) + "\n")
    return pages_path


def create_valid_triplet(concept_id="CONCEPT_001", seq="0001"):
    """Helper to create a valid 3-record concept triplet covering all 4 docs across calls."""
    en = BenchmarkRecord(
        benchmark_id=f"TFB-{seq}-EN",
        concept_id=concept_id,
        query_text="What are the digital banking guidelines?",
        query_language=BenchmarkLanguage.ENGLISH,
        query_script=BenchmarkScript.LATIN,
        query_type=BenchmarkQueryType.REGULATORY_REQUIREMENT,
        difficulty=BenchmarkDifficulty.EASY,
        expected_document_ids=[SAMPLE_DOC_1],
        relevant_pages=[1],
        evidence_spans=[
            EvidenceSpan(
                document_id=SAMPLE_DOC_1,
                page_number=1,
                verbatim_text="Digital banking framework policy guidelines.",
            )
        ],
        answerability=BenchmarkAnswerability.ANSWERABLE,
    )
    ur = BenchmarkRecord(
        benchmark_id=f"TFB-{seq}-UR",
        concept_id=concept_id,
        query_text="ڈیجیٹل بینکنگ کے رہنما اصول کیا ہیں؟",
        query_language=BenchmarkLanguage.URDU,
        query_script=BenchmarkScript.ARABIC,
        query_type=BenchmarkQueryType.REGULATORY_REQUIREMENT,
        difficulty=BenchmarkDifficulty.EASY,
        expected_document_ids=[SAMPLE_DOC_1],
        relevant_pages=[1],
        evidence_spans=[
            EvidenceSpan(
                document_id=SAMPLE_DOC_1,
                page_number=1,
                verbatim_text="Digital banking framework policy guidelines.",
            )
        ],
        answerability=BenchmarkAnswerability.ANSWERABLE,
    )
    ru = BenchmarkRecord(
        benchmark_id=f"TFB-{seq}-RU",
        concept_id=concept_id,
        query_text="Digital banking ke rahnuma asool kya hain?",
        query_language=BenchmarkLanguage.ROMAN_URDU,
        query_script=BenchmarkScript.LATIN,
        query_type=BenchmarkQueryType.REGULATORY_REQUIREMENT,
        difficulty=BenchmarkDifficulty.EASY,
        expected_document_ids=[SAMPLE_DOC_1],
        relevant_pages=[1],
        evidence_spans=[
            EvidenceSpan(
                document_id=SAMPLE_DOC_1,
                page_number=1,
                verbatim_text="Digital banking framework policy guidelines.",
            )
        ],
        answerability=BenchmarkAnswerability.ANSWERABLE,
    )
    return [en, ur, ru]


def write_benchmark_file(path, records):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r.model_dump(), ensure_ascii=False) + "\n")


def create_four_doc_triplets():
    """Helper creating 4 concept triplets covering all 4 trusted SBP documents."""
    c1 = create_valid_triplet("CONCEPT_001", "0001")
    
    # Doc 2
    c2 = [
        BenchmarkRecord(
            benchmark_id="TFB-0002-EN",
            concept_id="CONCEPT_002",
            query_text="What are onboarding requirements?",
            query_language=BenchmarkLanguage.ENGLISH,
            query_script=BenchmarkScript.LATIN,
            query_type=BenchmarkQueryType.REGULATORY_REQUIREMENT,
            difficulty=BenchmarkDifficulty.EASY,
            expected_document_ids=[SAMPLE_DOC_2],
            relevant_pages=[1],
            evidence_spans=[EvidenceSpan(document_id=SAMPLE_DOC_2, page_number=1, verbatim_text="Customer onboarding instructions and KYC requirements.")],
            answerability=BenchmarkAnswerability.ANSWERABLE,
        ),
        BenchmarkRecord(
            benchmark_id="TFB-0002-UR",
            concept_id="CONCEPT_002",
            query_text="آن بورڈنگ کے تقاضے کیا ہیں؟",
            query_language=BenchmarkLanguage.URDU,
            query_script=BenchmarkScript.ARABIC,
            query_type=BenchmarkQueryType.REGULATORY_REQUIREMENT,
            difficulty=BenchmarkDifficulty.EASY,
            expected_document_ids=[SAMPLE_DOC_2],
            relevant_pages=[1],
            evidence_spans=[EvidenceSpan(document_id=SAMPLE_DOC_2, page_number=1, verbatim_text="Customer onboarding instructions and KYC requirements.")],
            answerability=BenchmarkAnswerability.ANSWERABLE,
        ),
        BenchmarkRecord(
            benchmark_id="TFB-0002-RU",
            concept_id="CONCEPT_002",
            query_text="Onboarding ke taqazay kya hain?",
            query_language=BenchmarkLanguage.ROMAN_URDU,
            query_script=BenchmarkScript.LATIN,
            query_type=BenchmarkQueryType.REGULATORY_REQUIREMENT,
            difficulty=BenchmarkDifficulty.EASY,
            expected_document_ids=[SAMPLE_DOC_2],
            relevant_pages=[1],
            evidence_spans=[EvidenceSpan(document_id=SAMPLE_DOC_2, page_number=1, verbatim_text="Customer onboarding instructions and KYC requirements.")],
            answerability=BenchmarkAnswerability.ANSWERABLE,
        ),
    ]

    # Doc 3
    c3 = [
        BenchmarkRecord(
            benchmark_id="TFB-0003-EN",
            concept_id="CONCEPT_003",
            query_text="What is Roshan Digital Account expansion?",
            query_language=BenchmarkLanguage.ENGLISH,
            query_script=BenchmarkScript.LATIN,
            query_type=BenchmarkQueryType.REGULATORY_REQUIREMENT,
            difficulty=BenchmarkDifficulty.EASY,
            expected_document_ids=[SAMPLE_DOC_3],
            relevant_pages=[1],
            evidence_spans=[EvidenceSpan(document_id=SAMPLE_DOC_3, page_number=1, verbatim_text="Roshan Digital Account expansion for non-residents.")],
            answerability=BenchmarkAnswerability.ANSWERABLE,
        ),
        BenchmarkRecord(
            benchmark_id="TFB-0003-UR",
            concept_id="CONCEPT_003",
            query_text="روشن ڈیجیٹل اکاؤنٹ کی توسیعات کیا ہیں؟",
            query_language=BenchmarkLanguage.URDU,
            query_script=BenchmarkScript.ARABIC,
            query_type=BenchmarkQueryType.REGULATORY_REQUIREMENT,
            difficulty=BenchmarkDifficulty.EASY,
            expected_document_ids=[SAMPLE_DOC_3],
            relevant_pages=[1],
            evidence_spans=[EvidenceSpan(document_id=SAMPLE_DOC_3, page_number=1, verbatim_text="Roshan Digital Account expansion for non-residents.")],
            answerability=BenchmarkAnswerability.ANSWERABLE,
        ),
        BenchmarkRecord(
            benchmark_id="TFB-0003-RU",
            concept_id="CONCEPT_003",
            query_text="Roshan Digital Account ki tauseeat kya hain?",
            query_language=BenchmarkLanguage.ROMAN_URDU,
            query_script=BenchmarkScript.LATIN,
            query_type=BenchmarkQueryType.REGULATORY_REQUIREMENT,
            difficulty=BenchmarkDifficulty.EASY,
            expected_document_ids=[SAMPLE_DOC_3],
            relevant_pages=[1],
            evidence_spans=[EvidenceSpan(document_id=SAMPLE_DOC_3, page_number=1, verbatim_text="Roshan Digital Account expansion for non-residents.")],
            answerability=BenchmarkAnswerability.ANSWERABLE,
        ),
    ]

    # Doc 4
    c4 = [
        BenchmarkRecord(
            benchmark_id="TFB-0004-EN",
            concept_id="CONCEPT_004",
            query_text="What are consumer protection guidelines?",
            query_language=BenchmarkLanguage.ENGLISH,
            query_script=BenchmarkScript.LATIN,
            query_type=BenchmarkQueryType.REGULATORY_REQUIREMENT,
            difficulty=BenchmarkDifficulty.EASY,
            expected_document_ids=[SAMPLE_DOC_4],
            relevant_pages=[1],
            evidence_spans=[EvidenceSpan(document_id=SAMPLE_DOC_4, page_number=1, verbatim_text="Consumer protection guidelines and complaint resolution.")],
            answerability=BenchmarkAnswerability.ANSWERABLE,
        ),
        BenchmarkRecord(
            benchmark_id="TFB-0004-UR",
            concept_id="CONCEPT_004",
            query_text="صارفین کے تحفظ کی ہدایات کیا ہیں؟",
            query_language=BenchmarkLanguage.URDU,
            query_script=BenchmarkScript.ARABIC,
            query_type=BenchmarkQueryType.REGULATORY_REQUIREMENT,
            difficulty=BenchmarkDifficulty.EASY,
            expected_document_ids=[SAMPLE_DOC_4],
            relevant_pages=[1],
            evidence_spans=[EvidenceSpan(document_id=SAMPLE_DOC_4, page_number=1, verbatim_text="Consumer protection guidelines and complaint resolution.")],
            answerability=BenchmarkAnswerability.ANSWERABLE,
        ),
        BenchmarkRecord(
            benchmark_id="TFB-0004-RU",
            concept_id="CONCEPT_004",
            query_text="Consumer protection ki hidayat kya hain?",
            query_language=BenchmarkLanguage.ROMAN_URDU,
            query_script=BenchmarkScript.LATIN,
            query_type=BenchmarkQueryType.REGULATORY_REQUIREMENT,
            difficulty=BenchmarkDifficulty.EASY,
            expected_document_ids=[SAMPLE_DOC_4],
            relevant_pages=[1],
            evidence_spans=[EvidenceSpan(document_id=SAMPLE_DOC_4, page_number=1, verbatim_text="Consumer protection guidelines and complaint resolution.")],
            answerability=BenchmarkAnswerability.ANSWERABLE,
        ),
    ]

    return c1 + c2 + c3 + c4


# 1. Duplicate benchmark ID rejection
def test_duplicate_benchmark_id_rejection(tmp_path, mock_pages_file):
    bm_path = tmp_path / "bm.jsonl"
    recs = create_four_doc_triplets()
    recs[1].benchmark_id = recs[0].benchmark_id  # Duplicate ID
    write_benchmark_file(bm_path, recs)
    
    is_valid, errors, _ = validate_benchmark_file(bm_path, mock_pages_file)
    assert not is_valid
    assert any("Duplicate benchmark_id" in e for e in errors)


# 2. Missing language variant rejection
def test_missing_language_variant_rejection(tmp_path, mock_pages_file):
    bm_path = tmp_path / "bm.jsonl"
    recs = create_four_doc_triplets()
    recs.pop()  # Remove Roman Urdu from concept 4
    write_benchmark_file(bm_path, recs)

    is_valid, errors, _ = validate_benchmark_file(bm_path, mock_pages_file)
    assert not is_valid
    assert any("missing required language triad" in e for e in errors)


# 3. Invalid language/script combination
def test_invalid_language_script_combination(tmp_path, mock_pages_file):
    bm_path = tmp_path / "bm.jsonl"
    recs = create_four_doc_triplets()
    recs[0].query_script = BenchmarkScript.ARABIC  # English with ARABIC script
    write_benchmark_file(bm_path, recs)

    is_valid, errors, _ = validate_benchmark_file(bm_path, mock_pages_file)
    assert not is_valid
    assert any("English query must use LATIN script" in e for e in errors)


# 4. Urdu script validation
def test_urdu_script_validation(tmp_path, mock_pages_file):
    bm_path = tmp_path / "bm.jsonl"
    recs = create_four_doc_triplets()
    recs[1].query_text = "English text in Urdu field without Arabic characters"
    write_benchmark_file(bm_path, recs)

    is_valid, errors, _ = validate_benchmark_file(bm_path, mock_pages_file)
    assert not is_valid
    assert any("Urdu query lacks Arabic script characters" in e for e in errors)


# 5. Roman Urdu script validation
def test_roman_urdu_script_validation(tmp_path, mock_pages_file):
    bm_path = tmp_path / "bm.jsonl"
    recs = create_four_doc_triplets()
    recs[2].query_text = "Roman urdu text with اردو characters"
    write_benchmark_file(bm_path, recs)

    is_valid, errors, _ = validate_benchmark_file(bm_path, mock_pages_file)
    assert not is_valid
    assert any("Roman Urdu query contains Arabic script characters" in e for e in errors)


# 6. Invalid document ID rejection
def test_invalid_document_id_rejection(tmp_path, mock_pages_file):
    bm_path = tmp_path / "bm.jsonl"
    recs = create_four_doc_triplets()
    recs[0].expected_document_ids = ["PK-INVALID-DOC-2025-0001"]
    recs[0].evidence_spans[0].document_id = "PK-INVALID-DOC-2025-0001"
    write_benchmark_file(bm_path, recs)

    is_valid, errors, _ = validate_benchmark_file(bm_path, mock_pages_file)
    assert not is_valid
    assert any("Invalid target document_id" in e for e in errors)


# 7. Invalid page rejection
def test_invalid_page_rejection(tmp_path, mock_pages_file):
    bm_path = tmp_path / "bm.jsonl"
    recs = create_four_doc_triplets()
    recs[0].evidence_spans[0].page_number = 999  # Non-existent page
    write_benchmark_file(bm_path, recs)

    is_valid, errors, _ = validate_benchmark_file(bm_path, mock_pages_file)
    assert not is_valid
    assert any("references missing page" in e for e in errors)


# 8. Missing evidence span rejection
def test_missing_evidence_span_rejection(tmp_path, mock_pages_file):
    bm_path = tmp_path / "bm.jsonl"
    recs = create_four_doc_triplets()
    recs[0].evidence_spans = []  # Empty evidence span for answerable
    write_benchmark_file(bm_path, recs)

    is_valid, errors, _ = validate_benchmark_file(bm_path, mock_pages_file)
    assert not is_valid
    assert any("Answerable query has empty evidence_spans" in e for e in errors)


# 9. Non-verbatim evidence rejection
def test_non_verbatim_evidence_rejection(tmp_path, mock_pages_file):
    bm_path = tmp_path / "bm.jsonl"
    recs = create_four_doc_triplets()
    recs[0].evidence_spans[0].verbatim_text = "This text is fabricated and not in page."
    write_benchmark_file(bm_path, recs)

    is_valid, errors, _ = validate_benchmark_file(bm_path, mock_pages_file)
    assert not is_valid
    assert any("not found in" in e for e in errors)


# 10. Answerable-without-evidence rejection
def test_answerable_without_evidence_rejection(tmp_path, mock_pages_file):
    bm_path = tmp_path / "bm.jsonl"
    recs = create_four_doc_triplets()
    recs[0].expected_document_ids = []
    recs[0].relevant_pages = []
    recs[0].evidence_spans = []
    write_benchmark_file(bm_path, recs)

    is_valid, errors, _ = validate_benchmark_file(bm_path, mock_pages_file)
    assert not is_valid
    assert any("Answerable query has empty" in e for e in errors)


# 11. Unanswerable-with-evidence rejection
def test_unanswerable_with_evidence_rejection(tmp_path, mock_pages_file):
    bm_path = tmp_path / "bm.jsonl"
    recs = create_four_doc_triplets()
    recs[0].answerability = BenchmarkAnswerability.UNANSWERABLE
    # Retains evidence spans, which is invalid for unanswerable
    write_benchmark_file(bm_path, recs)

    is_valid, errors, _ = validate_benchmark_file(bm_path, mock_pages_file)
    assert not is_valid
    assert any("Unanswerable query must have empty" in e for e in errors)


# 12. Duplicate query detection
def test_duplicate_query_detection(tmp_path, mock_pages_file):
    bm_path = tmp_path / "bm.jsonl"
    recs = create_four_doc_triplets()
    recs[3].query_text = recs[0].query_text  # Duplicate EN query
    write_benchmark_file(bm_path, recs)

    is_valid, errors, _ = validate_benchmark_file(bm_path, mock_pages_file)
    assert not is_valid
    assert any("Duplicate query text within language" in e for e in errors)


# 13. Valid multilingual concept triplet passes
def test_valid_multilingual_concept_triplet_passes(tmp_path, mock_pages_file):
    bm_path = tmp_path / "bm.jsonl"
    recs = create_four_doc_triplets()
    write_benchmark_file(bm_path, recs)

    is_valid, errors, sha256 = validate_benchmark_file(bm_path, mock_pages_file)
    assert is_valid
    assert len(errors) == 0
    assert len(sha256) == 64


# 14. Deterministic benchmark ordering
def test_deterministic_benchmark_ordering(tmp_path, mock_pages_file):
    bm_path1 = tmp_path / "bm1.jsonl"
    bm_path2 = tmp_path / "bm2.jsonl"
    recs1 = create_four_doc_triplets()
    recs2 = create_four_doc_triplets()
    write_benchmark_file(bm_path1, recs1)
    write_benchmark_file(bm_path2, recs2)

    _, _, sha1 = validate_benchmark_file(bm_path1, mock_pages_file)
    _, _, sha2 = validate_benchmark_file(bm_path2, mock_pages_file)
    assert sha1 == sha2


# 15. All-document coverage validation
def test_all_document_coverage_validation(tmp_path, mock_pages_file):
    bm_path = tmp_path / "bm.jsonl"
    # Only cover 3 of 4 docs
    recs = create_four_doc_triplets()[:9]  # Missing concept 4 (doc 4)
    write_benchmark_file(bm_path, recs)

    is_valid, errors, _ = validate_benchmark_file(bm_path, mock_pages_file)
    assert not is_valid
    assert any("do not cover all trusted SBP documents" in e for e in errors)


# 16. EvidenceSpan non-emptiness and document/page structural linkage
def test_evidence_span_structural_linkage_and_non_emptiness(tmp_path, mock_pages_file):
    bm_path = tmp_path / "bm.jsonl"
    recs = create_four_doc_triplets()
    # Modify evidence span to point to wrong document ID relative to expected_document_ids
    recs[0].evidence_spans[0].document_id = SAMPLE_DOC_2
    write_benchmark_file(bm_path, recs)

    is_valid, errors, _ = validate_benchmark_file(bm_path, mock_pages_file)
    assert not is_valid
    assert any("references missing page" in e or "not found in" in e for e in errors)


