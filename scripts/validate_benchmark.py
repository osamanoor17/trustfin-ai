#!/usr/bin/env python3
"""Validation script for FinUrdu Phase 2A Retrieval Benchmark.

Validates schema correctness, provenance anchoring, script compliance, verbatim evidence,
and answerability rules for data/benchmarks/finurdu_pilot_v0_1.jsonl.
"""

import sys
import json
import re
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Ensure app package is importable regardless of working directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.benchmark import (
    BenchmarkAnswerability,
    BenchmarkDifficulty,
    BenchmarkLanguage,
    BenchmarkQueryType,
    BenchmarkRecord,
    BenchmarkScript,
    EvidenceSpan,
)

TRUSTED_DOCUMENT_IDS = {
    "PK-SBP-DIGITAL_BANKING_POLICY-2022-0001",
    "PK-SBP-AML_KYC_GUIDANCE-2025-0001",
    "PK-SBP-AML_KYC_GUIDANCE-2026-0001",
    "PK-SBP-CONSUMER_GUIDANCE-2025-0001",
}


def load_normalized_pages(pages_path: Path) -> Dict[Tuple[str, int], str]:
    """Load normalized text indexed by (document_id, page_number)."""
    pages = {}
    if not pages_path.exists():
        raise FileNotFoundError(f"Normalized pages file not found at {pages_path}")
    with open(pages_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            if not line.strip():
                continue
            data = json.loads(line)
            doc_id = data.get("document_id")
            page_num = data.get("page_number")
            norm_text = data.get("normalized_text", "")
            pages[(doc_id, page_num)] = norm_text
    return pages


def validate_benchmark_file(
    benchmark_path: Path, pages_path: Path
) -> Tuple[bool, List[str], str]:
    """Execute all benchmark validation checks."""
    errors = []
    
    if not benchmark_path.exists():
        return False, [f"Benchmark file not found: {benchmark_path}"], ""

    # Compute SHA-256
    sha256_hash = hashlib.sha256()
    with open(benchmark_path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    benchmark_sha256 = sha256_hash.hexdigest()

    pages = load_normalized_pages(pages_path)
    
    records: List[BenchmarkRecord] = []
    seen_ids: Set[str] = set()
    queries_by_lang: Dict[BenchmarkLanguage, Set[str]] = defaultdict(set)
    records_by_concept: Dict[str, List[BenchmarkRecord]] = defaultdict(list)
    represented_docs: Set[str] = set()

    with open(benchmark_path, "r", encoding="utf-8") as f:
        for line_idx, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                record = BenchmarkRecord.model_validate(data)
            except Exception as e:
                errors.append(f"Line {line_idx}: Failed Pydantic validation: {e}")
                continue

            records.append(record)

            # Check 1: Unique benchmark_id
            if record.benchmark_id in seen_ids:
                errors.append(f"Line {line_idx}: Duplicate benchmark_id '{record.benchmark_id}'")
            else:
                seen_ids.add(record.benchmark_id)

            # Check 2: Non-empty query text
            if not record.query_text.strip():
                errors.append(f"Line {line_idx}: Empty query text in item {record.benchmark_id}")

            # Check 3: Language & Script validation
            query = record.query_text
            lang = record.query_language
            script = record.query_script

            if lang == BenchmarkLanguage.ENGLISH:
                if script != BenchmarkScript.LATIN:
                    errors.append(f"{record.benchmark_id}: English query must use LATIN script")
                if re.search(r"[\u0600-\u06FF]", query):
                    errors.append(f"{record.benchmark_id}: English query contains Arabic script characters")

            elif lang == BenchmarkLanguage.URDU:
                if script != BenchmarkScript.ARABIC:
                    errors.append(f"{record.benchmark_id}: Urdu query must use ARABIC script")
                if not re.search(r"[\u0600-\u06FF]", query):
                    errors.append(f"{record.benchmark_id}: Urdu query lacks Arabic script characters")

            elif lang == BenchmarkLanguage.ROMAN_URDU:
                if script != BenchmarkScript.LATIN:
                    errors.append(f"{record.benchmark_id}: Roman Urdu query must use LATIN script")
                if re.search(r"[\u0600-\u06FF]", query):
                    errors.append(f"{record.benchmark_id}: Roman Urdu query contains Arabic script characters")

            # Check 4: Duplicate query detection per language
            if query in queries_by_lang[lang]:
                errors.append(f"{record.benchmark_id}: Duplicate query text within language '{lang.value}'")
            else:
                queries_by_lang[lang].add(query)

            # Check 5: Answerability vs Evidence consistency
            if record.answerability == BenchmarkAnswerability.ANSWERABLE:
                if not record.expected_document_ids:
                    errors.append(f"{record.benchmark_id}: Answerable query has empty expected_document_ids")
                if not record.relevant_pages:
                    errors.append(f"{record.benchmark_id}: Answerable query has empty relevant_pages")
                if not record.evidence_spans:
                    errors.append(f"{record.benchmark_id}: Answerable query has empty evidence_spans")

                # Track represented documents
                for doc_id in record.expected_document_ids:
                    if doc_id not in TRUSTED_DOCUMENT_IDS:
                        errors.append(f"{record.benchmark_id}: Invalid target document_id '{doc_id}'")
                    else:
                        represented_docs.add(doc_id)

                # Check evidence spans verbatim in normalized text
                for span in record.evidence_spans:
                    if span.document_id not in TRUSTED_DOCUMENT_IDS:
                        errors.append(f"{record.benchmark_id}: Evidence span references invalid document_id '{span.document_id}'")
                    key = (span.document_id, span.page_number)
                    if key not in pages:
                        errors.append(f"{record.benchmark_id}: Evidence span references missing page ({span.document_id}, P{span.page_number})")
                    else:
                        page_text = pages[key]
                        if span.verbatim_text not in page_text:
                            errors.append(
                                f"{record.benchmark_id}: Evidence span verbatim text not found in ({span.document_id}, P{span.page_number})\n"
                                f"  Target Span: {repr(span.verbatim_text)}"
                            )

            elif record.answerability == BenchmarkAnswerability.UNANSWERABLE:
                if record.expected_document_ids:
                    errors.append(f"{record.benchmark_id}: Unanswerable query must have empty expected_document_ids")
                if record.relevant_pages:
                    errors.append(f"{record.benchmark_id}: Unanswerable query must have empty relevant_pages")
                if record.evidence_spans:
                    errors.append(f"{record.benchmark_id}: Unanswerable query must have empty evidence_spans")

            records_by_concept[record.concept_id].append(record)

    # Check 6: Concept grouping integrity
    for concept_id, concept_records in records_by_concept.items():
        if len(concept_records) != 3:
            errors.append(f"Concept '{concept_id}' has {len(concept_records)} query records (expected exactly 3)")
        
        langs_in_concept = {r.query_language for r in concept_records}
        expected_langs = {BenchmarkLanguage.ENGLISH, BenchmarkLanguage.URDU, BenchmarkLanguage.ROMAN_URDU}
        if langs_in_concept != expected_langs:
            errors.append(f"Concept '{concept_id}' missing required language triad EN/UR/RU (found: {langs_in_concept})")

        # Verify semantic alignment fields match across all language variants in concept
        first = concept_records[0]
        for other in concept_records[1:]:
            if other.query_type != first.query_type:
                errors.append(f"Concept '{concept_id}': Mismatched query_type between {first.benchmark_id} and {other.benchmark_id}")
            if other.difficulty != first.difficulty:
                errors.append(f"Concept '{concept_id}': Mismatched difficulty between {first.benchmark_id} and {other.benchmark_id}")
            if other.answerability != first.answerability:
                errors.append(f"Concept '{concept_id}': Mismatched answerability between {first.benchmark_id} and {other.benchmark_id}")
            if other.expected_document_ids != first.expected_document_ids:
                errors.append(f"Concept '{concept_id}': Mismatched expected_document_ids between {first.benchmark_id} and {other.benchmark_id}")
            if other.relevant_pages != first.relevant_pages:
                errors.append(f"Concept '{concept_id}': Mismatched relevant_pages between {first.benchmark_id} and {other.benchmark_id}")

    # Check 7: All 4 trusted documents represented among answerable concepts
    missing_docs = TRUSTED_DOCUMENT_IDS - represented_docs
    if missing_docs:
        errors.append(f"Answerable benchmark concepts do not cover all trusted SBP documents. Missing: {missing_docs}")

    is_valid = len(errors) == 0
    return is_valid, errors, benchmark_sha256


def main():
    benchmark_file = Path("data/benchmarks/finurdu_pilot_v0_1.jsonl")
    pages_file = Path("data/processed/sbp/sbp_pages.jsonl")

    print(f"Validating benchmark artifact: {benchmark_file}")
    is_valid, errors, sha256_hash = validate_benchmark_file(benchmark_file, pages_file)

    if not is_valid:
        print(f"\n[FAIL] Benchmark validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f" - {err}")
        sys.exit(1)

    print("\n[SUCCESS] All benchmark validation checks passed successfully!")
    print(f"Benchmark File SHA-256: {sha256_hash}")


if __name__ == "__main__":
    main()
