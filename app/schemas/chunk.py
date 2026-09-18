"""Pydantic schemas for document chunk records and chunking manifests."""

from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChunkRecord(BaseModel):
    """Schema representing a single text chunk with strict page provenance."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str = Field(..., description="Deterministic chunk identifier: {document_id}::{strategy}::{chunk_index:06d}")
    strategy: str = Field(..., description="Chunking strategy identifier")
    document_id: str = Field(..., description="Unique document identifier")
    chunk_index: int = Field(..., ge=0, description="0-based chunk index within document and strategy")
    text: str = Field(..., min_length=1, description="Chunk text content")
    word_count: int = Field(..., ge=1, description="Word count of chunk text (whitespace tokens)")
    character_count: int = Field(..., ge=1, description="Character count of chunk text")
    page_start: int = Field(..., ge=1, description="First 1-based source page number")
    page_end: int = Field(..., ge=1, description="Last 1-based source page number")
    source_pages: List[int] = Field(..., description="Sorted, unique list of 1-based source page numbers")
    source_sha256: str = Field(..., description="SHA-256 hash of the raw source PDF")
    source_file_name: str = Field(..., description="Basename of the source PDF file")
    contains_table_like_content: bool = Field(
        default=False, description="True if any contributing page contains table-like content"
    )
    is_low_text: bool = Field(
        default=False, description="True if chunk originated from a LOW_TEXT page or sparse content"
    )

    @field_validator("source_sha256")
    @classmethod
    def validate_sha256(cls, v: str) -> str:
        if len(v) != 64 or not all(c in "0123456789abcdefABCDEF" for c in v):
            raise ValueError("source_sha256 must be a 64-character hexadecimal digest")
        return v.lower()

    @field_validator("page_end")
    @classmethod
    def validate_page_bounds(cls, v: int, info) -> int:
        page_start = info.data.get("page_start")
        if page_start is not None and v < page_start:
            raise ValueError(f"page_end ({v}) must be greater than or equal to page_start ({page_start})")
        return v

    @field_validator("source_pages")
    @classmethod
    def validate_source_pages(cls, v: List[int], info) -> List[int]:
        if not v:
            raise ValueError("source_pages must contain at least one page number")
        if v != sorted(list(set(v))):
            raise ValueError("source_pages must be sorted in ascending order with unique values")
        page_start = info.data.get("page_start")
        page_end = info.data.get("page_end")
        if page_start is not None and min(v) != page_start:
            raise ValueError(f"min(source_pages) ({min(v)}) must equal page_start ({page_start})")
        if page_end is not None and max(v) != page_end:
            raise ValueError(f"max(source_pages) ({max(v)}) must equal page_end ({page_end})")
        return v


class ChunkingManifestEntry(BaseModel):
    """Schema representing strategy execution summary in chunking manifest."""

    model_config = ConfigDict(extra="forbid")

    strategy: str = Field(..., description="Chunking strategy identifier")
    configuration: Dict[str, Any] = Field(..., description="Strategy configuration parameters")
    source_page_corpus_sha256: str = Field(..., description="SHA-256 digest of input sbp_pages.jsonl")
    chunker_name: str = Field(default="TrustFin SBP Document Chunker", description="Chunker engine name")
    chunker_version: str = Field(default="1.0.0", description="Chunker engine version")
    processed_at: str = Field(..., description="ISO 8601 UTC execution timestamp")
    total_documents: int = Field(..., ge=0, description="Total documents chunked")
    total_chunks: int = Field(..., ge=0, description="Total chunks generated")
    total_words: int = Field(..., ge=0, description="Sum of words across all generated chunks")
    min_chunk_words: int = Field(..., ge=0, description="Minimum chunk word count")
    max_chunk_words: int = Field(..., ge=0, description="Maximum chunk word count")
    mean_chunk_words: float = Field(..., ge=0.0, description="Mean chunk word count")
    median_chunk_words: float = Field(..., ge=0.0, description="Median chunk word count")
    chunks_crossing_pages: int = Field(..., ge=0, description="Count of chunks spanning multiple source pages")
    chunks_with_table_like_content: int = Field(..., ge=0, description="Count of chunks containing table-like content")
    output_file: str = Field(..., description="Relative repository path to generated JSONL chunk file")
    processing_status: str = Field(default="CHUNKED_SUCCESSFULLY", description="Execution status")
