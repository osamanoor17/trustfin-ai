"""Pydantic schemas for processed page corpus and corpus manifests."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExtractionStatus(str, Enum):
    """Page-level extraction status taxonomy."""

    EXTRACTED = "EXTRACTED"
    EMPTY_TEXT = "EMPTY_TEXT"
    LOW_TEXT = "LOW_TEXT"
    REQUIRES_OCR_REVIEW = "REQUIRES_OCR_REVIEW"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"


class ProcessedPage(BaseModel):
    """Schema representing a single page extracted from a raw PDF document."""

    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(..., description="Unique document identifier")
    source_file_name: str = Field(..., description="Basename of the source PDF file")
    source_sha256: str = Field(..., description="SHA-256 hash of the raw source PDF")
    page_number: int = Field(..., ge=1, description="1-based page index")
    raw_text: str = Field(..., description="Unmodified extracted text content from PyMuPDF")
    normalized_text: str = Field(..., description="Conservatively normalized text content")
    character_count: int = Field(..., ge=0, description="Character count of normalized text")
    word_count: int = Field(..., ge=0, description="Word count of normalized text")
    contains_table_like_content: bool = Field(
        default=False, description="Whether page shows observable tabular structures"
    )
    extraction_status: ExtractionStatus = Field(
        default=ExtractionStatus.EXTRACTED, description="Extraction quality classification"
    )

    @field_validator("source_sha256")
    @classmethod
    def validate_sha256(cls, v: str) -> str:
        if len(v) != 64 or not all(c in "0123456789abcdefABCDEF" for c in v):
            raise ValueError("source_sha256 must be a 64-character hexadecimal digest")
        return v.lower()


class ProcessedDocumentManifestEntry(BaseModel):
    """Schema representing document-level processing entry in the processed manifest."""

    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(..., description="Unique document identifier")
    source_file_name: str = Field(..., description="Basename of the source PDF file")
    source_sha256: str = Field(..., description="SHA-256 hash of the raw source PDF")
    parser_name: str = Field(default="TrustFin SBP PyMuPDF Parser", description="Parser engine name")
    parser_version: str = Field(default="1.0.0", description="Parser release version")
    processed_at: str = Field(..., description="ISO 8601 UTC execution timestamp")
    total_pages: int = Field(..., ge=0, description="Total pages in the source document")
    pages_extracted: int = Field(..., ge=0, description="Number of successfully extracted pages")
    empty_pages: int = Field(..., ge=0, description="Count of empty text pages")
    low_text_pages: int = Field(..., ge=0, description="Count of low-text pages")
    pages_requiring_ocr_review: int = Field(..., ge=0, description="Count of pages requiring OCR review")
    pages_with_table_like_content: int = Field(..., ge=0, description="Count of pages containing tables")
    total_extracted_characters: int = Field(..., ge=0, description="Sum of characters extracted across all pages")
    output_file: str = Field(..., description="Relative repository path to JSONL page storage")
    processing_status: str = Field(default="PROCESSED_SUCCESSFULLY", description="Overall document processing status")
