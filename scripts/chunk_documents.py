"""Deterministic SBP Document Chunking & Provenance Pipeline for TrustFin AI.

Phase 1D: Converts page-aware processed corpus (data/processed/sbp/sbp_pages.jsonl)
into three reproducible experimental chunking variants:
1. page_v1 (Page-level baseline)
2. fixed_300w_50o_v1 (Fixed word-window with exact word-to-page provenance mapping)
3. page_aware_300w_50o_v1 (Page-aware window respecting page boundaries)
"""

from datetime import datetime, timezone
import hashlib
import json
import logging
from pathlib import Path
import statistics
import sys
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.schemas.chunk import ChunkingManifestEntry, ChunkRecord
from app.schemas.processed_document import ExtractionStatus, ProcessedPage

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("trustfin.chunker")

# Inputs and Outputs
INPUT_PAGE_CORPUS_PATH = PROJECT_ROOT / "data" / "processed" / "sbp" / "sbp_pages.jsonl"
EXPECTED_INPUT_SHA256 = "086af1f787c3bb62fdc1b69af47265502da006f23d8fff19445719c75f2d40a1"

CHUNKS_DIR = PROJECT_ROOT / "data" / "processed" / "sbp" / "chunks"
CHUNKING_MANIFEST_PATH = PROJECT_ROOT / "data" / "manifest" / "sbp_chunking_manifest.jsonl"


def compute_sha256(file_path: Path) -> str:
    """Compute lowercase 64-character SHA-256 digest of a local file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest().lower()


def tokenize_words(text: str) -> List[str]:
    """Single reusable tokenization rule: split on whitespace.

    A 'word' is defined as any non-whitespace character sequence resulting from text.split().
    Used consistently across chunking, overlap calculation, manifest statistics, and coverage validation.
    """
    if not text:
        return []
    return text.split()


def count_words(text: str) -> int:
    """Return word count using standardized tokenization rule."""
    return len(tokenize_words(text))


def load_and_verify_page_corpus(path: Path) -> Tuple[List[ProcessedPage], str]:
    """Load and validate processed page corpus from JSONL file."""
    if not path.exists():
        raise FileNotFoundError(f"Input page corpus not found: {path}")

    actual_sha = compute_sha256(path)
    if actual_sha != EXPECTED_INPUT_SHA256:
        raise ValueError(
            f"Input page corpus SHA-256 mismatch! Expected {EXPECTED_INPUT_SHA256}, got {actual_sha}"
        )

    pages: List[ProcessedPage] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if line.strip():
                try:
                    data = json.loads(line)
                    page = ProcessedPage(**data)
                    pages.append(page)
                except Exception as e:
                    raise ValueError(f"Failed to parse ProcessedPage line {line_num}: {e}")

    logger.info(f"Input page corpus verified (SHA-256: {actual_sha[:12]}...). Loaded {len(pages)} pages.")
    return pages, actual_sha


# ==============================================================================
# STRATEGY A: PAGE (page_v1)
# ==============================================================================

def chunk_strategy_page(pages_by_doc: Dict[str, List[ProcessedPage]]) -> List[ChunkRecord]:
    """Strategy A (page_v1): One extracted PDF page becomes one chunk."""
    strategy_id = "page_v1"
    chunks: List[ChunkRecord] = []

    for doc_id, pages in pages_by_doc.items():
        chunk_idx = 0
        for page in pages:
            norm_text = page.normalized_text.strip()
            if not norm_text:
                continue  # Omit empty text pages from producing empty chunks

            w_count = count_words(norm_text)
            c_count = len(norm_text)
            chunk_id = f"{doc_id}::{strategy_id}::{chunk_idx:06d}"

            record = ChunkRecord(
                chunk_id=chunk_id,
                strategy=strategy_id,
                document_id=doc_id,
                chunk_index=chunk_idx,
                text=norm_text,
                word_count=w_count,
                character_count=c_count,
                page_start=page.page_number,
                page_end=page.page_number,
                source_pages=[page.page_number],
                source_sha256=page.source_sha256,
                source_file_name=page.source_file_name,
                contains_table_like_content=page.contains_table_like_content,
                is_low_text=(page.extraction_status == ExtractionStatus.LOW_TEXT),
            )
            chunks.append(record)
            chunk_idx += 1

    return chunks


# ==============================================================================
# STRATEGY B: FIXED WINDOW (fixed_300w_50o_v1)
# ==============================================================================

def chunk_strategy_fixed_window(
    pages_by_doc: Dict[str, List[ProcessedPage]],
    target_words: int = 300,
    overlap_words: int = 50,
) -> List[ChunkRecord]:
    """Strategy B (fixed_300w_50o_v1): Continuous fixed word-window across document.

    Page boundaries DO NOT cut or influence windows. Exact word-level page origin
    mapping is maintained to record exact source_pages, page_start, and page_end.
    """
    strategy_id = f"fixed_{target_words}w_{overlap_words}o_v1"
    step_words = target_words - overlap_words
    chunks: List[ChunkRecord] = []

    for doc_id, pages in pages_by_doc.items():
        # Build continuous word stream with exact page origin mapping
        all_words: List[str] = []
        word_page_map: List[int] = []
        page_table_map: Dict[int, bool] = {}
        page_low_text_map: Dict[int, bool] = {}
        source_sha = pages[0].source_sha256
        source_filename = pages[0].source_file_name

        for page in pages:
            p_num = page.page_number
            page_table_map[p_num] = page.contains_table_like_content
            page_low_text_map[p_num] = (page.extraction_status == ExtractionStatus.LOW_TEXT)

            words = tokenize_words(page.normalized_text)
            for w in words:
                all_words.append(w)
                word_page_map.append(p_num)

        total_words = len(all_words)
        if total_words == 0:
            continue

        start_idx = 0
        chunk_idx = 0

        while start_idx < total_words:
            end_idx = min(start_idx + target_words, total_words)
            chunk_words = all_words[start_idx:end_idx]
            chunk_pages_slice = word_page_map[start_idx:end_idx]

            chunk_text = " ".join(chunk_words)
            w_count = len(chunk_words)
            c_count = len(chunk_text)

            unique_pages = sorted(list(set(chunk_pages_slice)))
            p_start = min(unique_pages)
            p_end = max(unique_pages)

            has_table = any(page_table_map[p] for p in unique_pages)
            is_low = any(page_low_text_map[p] for p in unique_pages)

            chunk_id = f"{doc_id}::{strategy_id}::{chunk_idx:06d}"

            record = ChunkRecord(
                chunk_id=chunk_id,
                strategy=strategy_id,
                document_id=doc_id,
                chunk_index=chunk_idx,
                text=chunk_text,
                word_count=w_count,
                character_count=c_count,
                page_start=p_start,
                page_end=p_end,
                source_pages=unique_pages,
                source_sha256=source_sha,
                source_file_name=source_filename,
                contains_table_like_content=has_table,
                is_low_text=is_low,
            )
            chunks.append(record)
            chunk_idx += 1

            if end_idx == total_words:
                break
            start_idx += step_words

    return chunks


# ==============================================================================
# STRATEGY C: PAGE-AWARE WINDOW (page_aware_300w_50o_v1)
# ==============================================================================

def chunk_strategy_page_aware_window(
    pages_by_doc: Dict[str, List[ProcessedPage]],
    target_words: int = 300,
    overlap_words: int = 50,
) -> List[ChunkRecord]:
    """Strategy C (page_aware_300w_50o_v1): Page-aware window respecting page boundaries.

    Constructs chunks from ordered page segments:
    - If a single page exceeds target_words, split that page internally using word window/overlap.
    - If pages are each <= target_words, accumulate whole page text across adjacent pages up to target_words.
    - Carry forward trailing overlap_words (50 words) from previous chunk to maintain overlap.
    - Every chunk explicitly records all contributing source_pages.
    """
    strategy_id = f"page_aware_{target_words}w_{overlap_words}o_v1"
    step_words = target_words - overlap_words
    chunks: List[ChunkRecord] = []

    for doc_id, pages in pages_by_doc.items():
        source_sha = pages[0].source_sha256
        source_filename = pages[0].source_file_name

        chunk_idx = 0
        page_idx = 0
        num_pages = len(pages)
        overlap_prefix_words: List[Tuple[str, int]] = []  # (word, page_num)

        while page_idx < num_pages:
            current_page = pages[page_idx]
            page_words = tokenize_words(current_page.normalized_text)

            if not page_words:
                page_idx += 1
                continue

            # Case A: Oversized single page (> target_words)
            if len(page_words) > target_words:
                full_page_word_tuples = list(overlap_prefix_words) + [(w, current_page.page_number) for w in page_words]
                total_w = len(full_page_word_tuples)
                start_w = 0

                while start_w < total_w:
                    end_w = min(start_w + target_words, total_w)
                    slice_tuples = full_page_word_tuples[start_w:end_w]
                    chunk_words = [w for w, _ in slice_tuples]
                    chunk_pages = sorted(list(set(p for _, p in slice_tuples)))
                    chunk_text = " ".join(chunk_words)

                    has_table = any(p.contains_table_like_content for p in pages if p.page_number in chunk_pages)
                    is_low = any(p.extraction_status == ExtractionStatus.LOW_TEXT for p in pages if p.page_number in chunk_pages)

                    chunk_id = f"{doc_id}::{strategy_id}::{chunk_idx:06d}"
                    record = ChunkRecord(
                        chunk_id=chunk_id,
                        strategy=strategy_id,
                        document_id=doc_id,
                        chunk_index=chunk_idx,
                        text=chunk_text,
                        word_count=len(chunk_words),
                        character_count=len(chunk_text),
                        page_start=min(chunk_pages),
                        page_end=max(chunk_pages),
                        source_pages=chunk_pages,
                        source_sha256=source_sha,
                        source_file_name=source_filename,
                        contains_table_like_content=has_table,
                        is_low_text=is_low,
                    )
                    chunks.append(record)
                    chunk_idx += 1

                    if end_w == total_w:
                        overlap_prefix_words = slice_tuples[-overlap_words:]
                        break
                    start_w += step_words

                page_idx += 1
                continue

            # Case B: Standard page accumulation (pages <= target_words)
            accumulated: List[Tuple[str, int]] = list(overlap_prefix_words)

            while page_idx < num_pages:
                p = pages[page_idx]
                p_words = tokenize_words(p.normalized_text)
                if not p_words:
                    page_idx += 1
                    continue

                if len(p_words) > target_words:
                    # Next page is oversized; stop accumulation here and process it in Case A next
                    break

                if len(accumulated) + len(p_words) <= target_words:
                    accumulated.extend([(w, p.page_number) for w in p_words])
                    page_idx += 1
                else:
                    if len(accumulated) == len(overlap_prefix_words):
                        # Prefix alone was present, accumulate entire current page
                        accumulated.extend([(w, p.page_number) for w in p_words])
                        page_idx += 1
                    break

            if accumulated:
                chunk_words = [w for w, _ in accumulated]
                chunk_pages = sorted(list(set(p for _, p in accumulated)))
                chunk_text = " ".join(chunk_words)

                has_table = any(p.contains_table_like_content for p in pages if p.page_number in chunk_pages)
                is_low = any(p.extraction_status == ExtractionStatus.LOW_TEXT for p in pages if p.page_number in chunk_pages)

                chunk_id = f"{doc_id}::{strategy_id}::{chunk_idx:06d}"
                record = ChunkRecord(
                    chunk_id=chunk_id,
                    strategy=strategy_id,
                    document_id=doc_id,
                    chunk_index=chunk_idx,
                    text=chunk_text,
                    word_count=len(chunk_words),
                    character_count=len(chunk_text),
                    page_start=min(chunk_pages),
                    page_end=max(chunk_pages),
                    source_pages=chunk_pages,
                    source_sha256=source_sha,
                    source_file_name=source_filename,
                    contains_table_like_content=has_table,
                    is_low_text=is_low,
                )
                chunks.append(record)
                chunk_idx += 1

                overlap_prefix_words = accumulated[-overlap_words:]

    return chunks


# ==============================================================================
# COVERAGE VALIDATION
# ==============================================================================

def validate_strategy_coverage(
    pages_by_doc: Dict[str, List[ProcessedPage]],
    chunks: List[ChunkRecord],
    strategy_id: str,
) -> bool:
    """Verify 100% position-aware source content coverage and sequence integrity.

    Ensures every source token occurrence (by 0-based position index) in every document
    is present in at least one chunk, and that each chunk's text represents a valid,
    ordered slice of the original source token sequence.
    """
    chunks_by_doc: Dict[str, List[ChunkRecord]] = {}
    for c in chunks:
        chunks_by_doc.setdefault(c.document_id, []).append(c)

    for doc_id, pages in pages_by_doc.items():
        doc_source_tokens: List[str] = []
        for p in pages:
            doc_source_tokens.extend(tokenize_words(p.normalized_text))

        doc_chunks = chunks_by_doc.get(doc_id, [])
        if not doc_chunks and doc_source_tokens:
            logger.error(f"Coverage error: Document [{doc_id}] has {len(doc_source_tokens)} words but 0 chunks!")
            return False

        covered_positions: set[int] = set()
        last_match_start = 0

        for c in doc_chunks:
            chunk_tokens = tokenize_words(c.text)
            if not chunk_tokens:
                logger.error(f"Coverage error in [{doc_id}] ({strategy_id}): Empty chunk text in {c.chunk_id}!")
                return False

            chunk_len = len(chunk_tokens)
            match_start = -1

            # Search for contiguous chunk_tokens in doc_source_tokens starting from last_match_start
            for s in range(last_match_start, len(doc_source_tokens) - chunk_len + 1):
                if doc_source_tokens[s : s + chunk_len] == chunk_tokens:
                    match_start = s
                    break

            # Fallback search from position 0 if last_match_start didn't hit
            if match_start == -1:
                for s in range(0, last_match_start):
                    if doc_source_tokens[s : s + chunk_len] == chunk_tokens:
                        match_start = s
                        break

            if match_start == -1:
                logger.error(
                    f"Sequence integrity error in [{doc_id}] ({strategy_id}) for chunk {c.chunk_id}: "
                    f"Token sequence (len={chunk_len}) not found in source document!"
                )
                return False

            for pos in range(match_start, match_start + chunk_len):
                covered_positions.add(pos)

            last_match_start = match_start

        expected_positions = set(range(len(doc_source_tokens)))
        missing_positions = expected_positions - covered_positions

        if missing_positions:
            logger.error(
                f"Position coverage error in [{doc_id}] ({strategy_id}): "
                f"{len(missing_positions)} token occurrences omitted from chunks! "
                f"Sample missing indices: {sorted(list(missing_positions))[:5]}"
            )
            return False

    return True


# ==============================================================================
# MANIFEST STATS GENERATION
# ==============================================================================

def generate_manifest_entry(
    strategy_id: str,
    config: Dict[str, Any],
    chunks: List[ChunkRecord],
    input_sha: str,
    output_rel_path: str,
) -> ChunkingManifestEntry:
    """Compute summary statistics and create manifest entry for a strategy."""
    word_counts = [c.word_count for c in chunks] if chunks else [0]
    crossing_pages = sum(1 for c in chunks if c.page_start != c.page_end)
    table_chunks = sum(1 for c in chunks if c.contains_table_like_content)
    total_docs = len(set(c.document_id for c in chunks))

    return ChunkingManifestEntry(
        strategy=strategy_id,
        configuration=config,
        source_page_corpus_sha256=input_sha,
        chunker_name="TrustFin SBP Document Chunker",
        chunker_version="1.0.0",
        processed_at=datetime.now(timezone.utc).isoformat(),
        total_documents=total_docs,
        total_chunks=len(chunks),
        total_words=sum(word_counts),
        min_chunk_words=min(word_counts),
        max_chunk_words=max(word_counts),
        mean_chunk_words=round(statistics.mean(word_counts), 2),
        median_chunk_words=round(statistics.median(word_counts), 2),
        chunks_crossing_pages=crossing_pages,
        chunks_with_table_like_content=table_chunks,
        output_file=output_rel_path,
        processing_status="CHUNKED_SUCCESSFULLY",
    )


# ==============================================================================
# MAIN PIPELINE EXECUTION
# ==============================================================================

def run_chunking_pipeline() -> Tuple[Dict[str, List[ChunkRecord]], List[ChunkingManifestEntry]]:
    """Execute complete Phase 1D chunking pipeline across all 3 strategies."""
    logger.info("Starting Phase 1D SBP Chunking & Provenance Pipeline...")

    pages, input_sha = load_and_verify_page_corpus(INPUT_PAGE_CORPUS_PATH)

    # Group pages by document and sort deterministically
    pages_by_doc: Dict[str, List[ProcessedPage]] = {}
    for p in pages:
        pages_by_doc.setdefault(p.document_id, []).append(p)

    for doc_id in pages_by_doc:
        pages_by_doc[doc_id].sort(key=lambda x: x.page_number)

    # Ensure output directories exist
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKING_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    all_strategy_chunks: Dict[str, List[ChunkRecord]] = {}
    manifest_entries: List[ChunkingManifestEntry] = []

    # --------------------------------------------------------------------------
    # 1. Strategy A: PAGE (page_v1)
    # --------------------------------------------------------------------------
    logger.info("Executing Strategy A: page_v1...")
    chunks_page = chunk_strategy_page(pages_by_doc)
    all_strategy_chunks["page_v1"] = chunks_page

    assert validate_strategy_coverage(pages_by_doc, chunks_page, "page_v1"), "Coverage validation failed for page_v1!"

    out_path_page = CHUNKS_DIR / "page_v1.jsonl"
    with open(out_path_page, "w", encoding="utf-8", newline="\n") as f:
        for c in chunks_page:
            f.write(c.model_dump_json() + "\n")

    manifest_page = generate_manifest_entry(
        strategy_id="page_v1",
        config={"type": "PAGE", "unit": "page"},
        chunks=chunks_page,
        input_sha=input_sha,
        output_rel_path="data/processed/sbp/chunks/page_v1.jsonl",
    )
    manifest_entries.append(manifest_page)
    logger.info(f"Strategy page_v1 complete: {len(chunks_page)} chunks.")

    # --------------------------------------------------------------------------
    # 2. Strategy B: FIXED WINDOW (fixed_300w_50o_v1)
    # --------------------------------------------------------------------------
    logger.info("Executing Strategy B: fixed_300w_50o_v1...")
    chunks_fixed = chunk_strategy_fixed_window(pages_by_doc, target_words=300, overlap_words=50)
    all_strategy_chunks["fixed_300w_50o_v1"] = chunks_fixed

    assert validate_strategy_coverage(pages_by_doc, chunks_fixed, "fixed_300w_50o_v1"), "Coverage validation failed for fixed_300w_50o_v1!"

    out_path_fixed = CHUNKS_DIR / "fixed_300w_50o_v1.jsonl"
    with open(out_path_fixed, "w", encoding="utf-8", newline="\n") as f:
        for c in chunks_fixed:
            f.write(c.model_dump_json() + "\n")

    manifest_fixed = generate_manifest_entry(
        strategy_id="fixed_300w_50o_v1",
        config={"type": "FIXED_WINDOW", "target_words": 300, "overlap_words": 50, "unit": "words"},
        chunks=chunks_fixed,
        input_sha=input_sha,
        output_rel_path="data/processed/sbp/chunks/fixed_300w_50o_v1.jsonl",
    )
    manifest_entries.append(manifest_fixed)
    logger.info(f"Strategy fixed_300w_50o_v1 complete: {len(chunks_fixed)} chunks.")

    # --------------------------------------------------------------------------
    # 3. Strategy C: PAGE-AWARE WINDOW (page_aware_300w_50o_v1)
    # --------------------------------------------------------------------------
    logger.info("Executing Strategy C: page_aware_300w_50o_v1...")
    chunks_aware = chunk_strategy_page_aware_window(pages_by_doc, target_words=300, overlap_words=50)
    all_strategy_chunks["page_aware_300w_50o_v1"] = chunks_aware

    assert validate_strategy_coverage(pages_by_doc, chunks_aware, "page_aware_300w_50o_v1"), "Coverage validation failed for page_aware_300w_50o_v1!"

    out_path_aware = CHUNKS_DIR / "page_aware_300w_50o_v1.jsonl"
    with open(out_path_aware, "w", encoding="utf-8", newline="\n") as f:
        for c in chunks_aware:
            f.write(c.model_dump_json() + "\n")

    manifest_aware = generate_manifest_entry(
        strategy_id="page_aware_300w_50o_v1",
        config={"type": "PAGE_AWARE_WINDOW", "target_words": 300, "overlap_words": 50, "unit": "words"},
        chunks=chunks_aware,
        input_sha=input_sha,
        output_rel_path="data/processed/sbp/chunks/page_aware_300w_50o_v1.jsonl",
    )
    manifest_entries.append(manifest_aware)
    logger.info(f"Strategy page_aware_300w_50o_v1 complete: {len(chunks_aware)} chunks.")

    # Write overall chunking manifest
    with open(CHUNKING_MANIFEST_PATH, "w", encoding="utf-8", newline="\n") as f:
        for entry in manifest_entries:
            f.write(entry.model_dump_json() + "\n")

    logger.info(f"Wrote chunking manifest to {CHUNKING_MANIFEST_PATH}")
    return all_strategy_chunks, manifest_entries


if __name__ == "__main__":
    run_chunking_pipeline()
