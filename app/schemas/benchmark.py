"""Pydantic schemas for the Phase 2A FinUrdu multilingual retrieval benchmark."""

import re
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class BenchmarkLanguage(str, Enum):
    """Supported query languages for the retrieval benchmark."""

    ENGLISH = "ENGLISH"
    URDU = "URDU"
    ROMAN_URDU = "ROMAN_URDU"


class BenchmarkScript(str, Enum):
    """Supported query script classifications."""

    LATIN = "LATIN"
    ARABIC = "ARABIC"


class BenchmarkAnswerability(str, Enum):
    """Ground-truth answerability classification against corpus evidence."""

    ANSWERABLE = "ANSWERABLE"
    UNANSWERABLE = "UNANSWERABLE"


class BenchmarkDifficulty(str, Enum):
    """Operational query difficulty rubric."""

    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class BenchmarkQueryType(str, Enum):
    """Defensible query intent taxonomy for financial & regulatory retrieval."""

    FACTUAL = "FACTUAL"
    DEFINITIONAL = "DEFINITIONAL"
    PROCEDURAL = "PROCEDURAL"
    ELIGIBILITY = "ELIGIBILITY"
    LIMIT_OR_THRESHOLD = "LIMIT_OR_THRESHOLD"
    REGULATORY_REQUIREMENT = "REGULATORY_REQUIREMENT"
    COMPARATIVE = "COMPARATIVE"
    DOCUMENT_NAVIGATION = "DOCUMENT_NAVIGATION"


class EvidenceSpan(BaseModel):
    """Schema representing a single verbatim evidence span anchored in a source document page."""

    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(..., description="Target SBP document identifier")
    page_number: int = Field(..., ge=1, description="1-based page index containing evidence")
    verbatim_text: str = Field(
        ..., min_length=1, description="Verbatim text span extracted from normalized page text"
    )

    @field_validator("document_id")
    @classmethod
    def validate_document_id(cls, v: str) -> str:
        """Validate deterministic document identifier format."""
        pattern = r"^[A-Z]{2}-[A-Z0-9]+-[A-Z0-9_]+-\d{4}-[A-Z0-9]+$"
        if not re.match(pattern, v):
            raise ValueError(f"document_id '{v}' does not match expected convention: PK-SBP-DOCTYPE-YEAR-SEQ")
        return v


class BenchmarkRecord(BaseModel):
    """Schema representing a single benchmark query unit record."""

    model_config = ConfigDict(extra="forbid")

    benchmark_id: str = Field(
        ..., description="Deterministic query record identifier e.g. TFB-0001-EN"
    )
    concept_id: str = Field(
        ..., description="Underlying information-need concept identifier e.g. CUSTOMER_ONBOARDING_001"
    )
    query_text: str = Field(..., min_length=1, description="Query text string")
    query_language: BenchmarkLanguage = Field(..., description="Query language classification")
    query_script: BenchmarkScript = Field(..., description="Query script classification")
    query_type: BenchmarkQueryType = Field(..., description="Functional query category")
    difficulty: BenchmarkDifficulty = Field(..., description="Operational difficulty level")
    expected_document_ids: List[str] = Field(
        default_factory=list, description="Target document IDs containing evidence"
    )
    relevant_pages: List[int] = Field(
        default_factory=list, description="1-based target page numbers containing evidence"
    )
    evidence_spans: List[EvidenceSpan] = Field(
        default_factory=list, description="Verbatim evidence spans with document/page provenance"
    )
    answerability: BenchmarkAnswerability = Field(
        ..., description="Whether query can be answered from corpus evidence"
    )
    notes: Optional[str] = Field(default=None, description="Annotation and research notes")

    @field_validator("benchmark_id")
    @classmethod
    def validate_benchmark_id(cls, v: str) -> str:
        pattern = r"^TFB-\d{4}-(EN|UR|RU)$"
        if not re.match(pattern, v):
            raise ValueError(f"benchmark_id '{v}' must match pattern TFB-0000-XX (where XX is EN, UR, or RU)")
        return v

    @field_validator("concept_id")
    @classmethod
    def validate_concept_id(cls, v: str) -> str:
        pattern = r"^[A-Z0-9_]+$"
        if not re.match(pattern, v):
            raise ValueError(f"concept_id '{v}' must contain uppercase alphanumeric characters and underscores")
        return v
