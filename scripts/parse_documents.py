"""Deterministic SBP PDF Document Parsing & Normalization Pipeline for TrustFin AI.

Phase 1C: Converts trusted raw SBP PDF documents into a clean, reproducible,
page-aware processed JSONL corpus (data/processed/sbp/sbp_pages.jsonl) and
manifest (data/manifest/sbp_processed_manifest.jsonl).
"""

from datetime import datetime, timezone
import hashlib
import json
import logging
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pymupdf

from app.schemas.processed_document import (
    ExtractionStatus,
    ProcessedDocumentManifestEntry,
    ProcessedPage,
)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("trustfin.parser")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ACQUISITION_MANIFEST_PATH = PROJECT_ROOT / "data" / "manifest" / "sbp_acquisition_manifest.jsonl"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "sbp"
PROCESSED_PAGE_CORPUS_PATH = PROCESSED_DIR / "sbp_pages.jsonl"
PROCESSED_MANIFEST_PATH = PROJECT_ROOT / "data" / "manifest" / "sbp_processed_manifest.jsonl"

# Trusted pilot document IDs
EXPECTED_TRUSTED_IDS = [
    "PK-SBP-DIGITAL_BANKING_POLICY-2022-0001",
    "PK-SBP-AML_KYC_GUIDANCE-2025-0001",
    "PK-SBP-AML_KYC_GUIDANCE-2026-0001",
    "PK-SBP-CONSUMER_GUIDANCE-2025-0001",
]


def compute_sha256(file_path: Path) -> str:
    """Compute lowercase 64-character SHA-256 digest of a local file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest().lower()


def is_valid_pdf_magic_bytes(file_path: Path) -> bool:
    """Verify that file content begins with %PDF- magic header."""
    try:
        with open(file_path, "rb") as f:
            header = f.read(10)
        return header.startswith(b"%PDF-")
    except Exception:
        return False


def normalize_text(text: str) -> str:
    """Conservatively normalize raw extracted text.

    Preserves exact wording, legal/regulatory terms, numbers, punctuation,
    currency symbols, Urdu text, and Unicode characters without altering semantics.
    """
    if not text:
        return ""

    # 1. Normalize line endings (CRLF and CR to LF)
    clean = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Remove null bytes and non-breaking / zero-width space artifacts
    clean = clean.replace("\x00", "")
    clean = clean.replace("\u00a0", " ")  # Non-breaking space -> space
    clean = clean.replace("\u200b", "")  # Zero-width space -> strip

    # 3. Normalize line-internal whitespace while preserving line structure
    lines = clean.split("\n")
    norm_lines = []
    for line in lines:
        # Replace multiple spaces/tabs within a single line with a single space
        norm_line = re.sub(r"[ \t]+", " ", line).strip()
        norm_lines.append(norm_line)
    clean = "\n".join(norm_lines)

    # 4. Reduce excessive blank lines (3 or more newlines reduced to 2)
    clean = re.sub(r"\n{3,}", "\n\n", clean)

    # 5. Trim leading and trailing document/page whitespace
    return clean.strip()


def detect_table_like_content(page: pymupdf.Page, raw_text: str) -> bool:
    """Detect whether page contains observable tabular data structures.

    Non-destructive observation using PyMuPDF table finder and pattern signals.
    """
    # Signal 1: PyMuPDF find_tables()
    try:
        tables = page.find_tables()
        if tables and len(tables.tables) > 0:
            return True
    except Exception as e:
        logger.debug(f"PyMuPDF find_tables exception (non-fatal): {e}")

    # Signal 2: Line pattern inspection for multiple aligned numbers or columns
    lines = raw_text.split("\n")
    numeric_column_lines = 0
    for line in lines:
        # Check if line contains 3+ separate numeric or monetary tokens (e.g. 100 200 300 or Rs. 50 20%)
        numbers = re.findall(r"\b\d+(?:[\.,]\d+)?%?\b", line)
        if len(numbers) >= 3:
            numeric_column_lines += 1

    if numeric_column_lines >= 3:
        return True

    return False


def classify_page_extraction_status(
    raw_text: str, norm_text: str, page: pymupdf.Page
) -> ExtractionStatus:
    """Classify page extraction quality and flag scanned or low-text pages."""
    raw_stripped = raw_text.strip()
    norm_len = len(norm_text)
    word_count = len(norm_text.split())

    # Check for embedded raster images
    try:
        images = page.get_images()
        has_images = len(images) > 0
    except Exception:
        has_images = False

    if not raw_stripped or norm_len == 0:
        if has_images:
            return ExtractionStatus.REQUIRES_OCR_REVIEW
        return ExtractionStatus.EMPTY_TEXT

    if norm_len < 50 or word_count < 10:
        if has_images:
            return ExtractionStatus.REQUIRES_OCR_REVIEW
        return ExtractionStatus.LOW_TEXT

    if has_images and norm_len < 100:
        return ExtractionStatus.REQUIRES_OCR_REVIEW

    return ExtractionStatus.EXTRACTED


def parse_single_pdf(
    candidate: Dict[str, Any], raw_path: Path
) -> Tuple[List[ProcessedPage], ProcessedDocumentManifestEntry, List[str]]:
    """Parse a single verified raw PDF into page records and manifest summary."""
    doc_id = candidate["document_id"]
    file_name = candidate["file_name"]
    source_sha = candidate["sha256"]

    doc = pymupdf.open(raw_path)
    total_pages = len(doc)

    pages: List[ProcessedPage] = []
    empty_pages_count = 0
    low_text_pages_count = 0
    ocr_review_count = 0
    table_pages_count = 0
    total_chars = 0
    header_footer_candidates: List[str] = []

    for idx, page in enumerate(doc):
        page_num = idx + 1  # 1-based page index
        try:
            raw_text = page.get_text("text")
        except Exception as e:
            logger.error(f"Failed to extract text from {doc_id} page {page_num}: {e}")
            raw_text = ""

        norm_text = normalize_text(raw_text)
        char_count = len(norm_text)
        word_count = len(norm_text.split())
        total_chars += char_count

        contains_table = detect_table_like_content(page, raw_text)
        if contains_table:
            table_pages_count += 1

        status = classify_page_extraction_status(raw_text, norm_text, page)
        if status == ExtractionStatus.EMPTY_TEXT:
            empty_pages_count += 1
        elif status == ExtractionStatus.LOW_TEXT:
            low_text_pages_count += 1
        elif status == ExtractionStatus.REQUIRES_OCR_REVIEW:
            ocr_review_count += 1

        # Record header/footer sample (first and last non-empty lines)
        lines = [l for l in norm_text.split("\n") if l.strip()]
        if lines:
            header_footer_candidates.append(lines[0])
            if len(lines) > 1:
                header_footer_candidates.append(lines[-1])

        page_record = ProcessedPage(
            document_id=doc_id,
            source_file_name=file_name,
            source_sha256=source_sha,
            page_number=page_num,
            raw_text=raw_text,
            normalized_text=norm_text,
            character_count=char_count,
            word_count=word_count,
            contains_table_like_content=contains_table,
            extraction_status=status,
        )
        pages.append(page_record)

    doc.close()

    manifest_entry = ProcessedDocumentManifestEntry(
        document_id=doc_id,
        source_file_name=file_name,
        source_sha256=source_sha,
        parser_name="TrustFin SBP PyMuPDF Parser",
        parser_version="1.0.0",
        processed_at=datetime.now(timezone.utc).isoformat(),
        total_pages=total_pages,
        pages_extracted=len(pages),
        empty_pages=empty_pages_count,
        low_text_pages=low_text_pages_count,
        pages_requiring_ocr_review=ocr_review_count,
        pages_with_table_like_content=table_pages_count,
        total_extracted_characters=total_chars,
        output_file="data/processed/sbp/sbp_pages.jsonl",
        processing_status="PROCESSED_SUCCESSFULLY",
    )

    return pages, manifest_entry, header_footer_candidates


def run_parsing_pipeline() -> Tuple[List[ProcessedPage], List[ProcessedDocumentManifestEntry]]:
    """Execute main parsing pipeline for all trusted SBP documents."""
    logger.info("Starting Phase 1C SBP Document Parsing & Normalization Pipeline...")

    if not ACQUISITION_MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Acquisition manifest not found at: {ACQUISITION_MANIFEST_PATH}")

    # Load acquisition manifest records
    acquisition_records: List[Dict[str, Any]] = []
    with open(ACQUISITION_MANIFEST_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                acquisition_records.append(json.loads(line))

    # Filter strictly eligible trusted documents
    eligible_records = [
        r for r in acquisition_records
        if r.get("document_id") in EXPECTED_TRUSTED_IDS
        and r.get("acquisition_status") in ("ACQUIRED", "DUPLICATE_IDENTICAL")
    ]

    # Sort deterministically by document_id
    eligible_records.sort(key=lambda r: r["document_id"])

    logger.info(f"Loaded {len(acquisition_records)} manifest records. Found {len(eligible_records)} eligible trusted records.")

    all_pages: List[ProcessedPage] = []
    manifest_entries: List[ProcessedDocumentManifestEntry] = []

    for record in eligible_records:
        doc_id = record["document_id"]
        rel_path = record.get("local_raw_path")
        if not rel_path:
            logger.error(f"Record [{doc_id}] missing local_raw_path. Skipping.")
            continue

        raw_path = PROJECT_ROOT / rel_path
        logger.info(f"Pre-parse verification for [{doc_id}]: {raw_path.name}")

        # Pre-parsing verification
        if not raw_path.exists():
            raise FileNotFoundError(f"Raw PDF file does not exist: {raw_path}")

        if not is_valid_pdf_magic_bytes(raw_path):
            raise ValueError(f"Raw file {raw_path.name} failed %PDF- magic bytes check!")

        actual_sha = compute_sha256(raw_path)
        expected_sha = record["sha256"].lower()
        if actual_sha != expected_sha:
            raise ValueError(
                f"SHA-256 mismatch for [{doc_id}]! Expected {expected_sha}, got {actual_sha}"
            )

        logger.info(f"Pre-parse integrity verified for [{doc_id}] (SHA-256: {actual_sha[:12]}...). Parsing...")

        pages, manifest_entry, _ = parse_single_pdf(record, raw_path)
        all_pages.extend(pages)
        manifest_entries.append(manifest_entry)

        logger.info(
            f"Successfully parsed [{doc_id}]: {manifest_entry.total_pages} pages, "
            f"{manifest_entry.total_extracted_characters:,} chars, "
            f"{manifest_entry.pages_with_table_like_content} table-like pages."
        )

    # Ensure output directories exist
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Sort all pages deterministically (document_id, page_number)
    all_pages.sort(key=lambda p: (p.document_id, p.page_number))

    # Write processed JSONL corpus with explicit LF line endings
    with open(PROCESSED_PAGE_CORPUS_PATH, "w", encoding="utf-8", newline="\n") as f:
        for page in all_pages:
            f.write(page.model_dump_json() + "\n")

    # Write processed manifest JSONL with explicit LF line endings
    with open(PROCESSED_MANIFEST_PATH, "w", encoding="utf-8", newline="\n") as f:
        for entry in manifest_entries:
            f.write(entry.model_dump_json() + "\n")

    logger.info(f"Wrote {len(all_pages)} page records to {PROCESSED_PAGE_CORPUS_PATH}")
    logger.info(f"Wrote {len(manifest_entries)} document manifest records to {PROCESSED_MANIFEST_PATH}")

    return all_pages, manifest_entries


if __name__ == "__main__":
    run_parsing_pipeline()
