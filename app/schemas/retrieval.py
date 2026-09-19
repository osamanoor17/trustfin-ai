"""Pydantic schemas for Phase 2B BM25 retrieval baseline experiments."""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.benchmark import BenchmarkLanguage


class RetrievalResultItem(BaseModel):
    """Schema representing a single ranked retrieved chunk item."""

    model_config = ConfigDict(extra="forbid")

    benchmark_id: str = Field(..., description="Deterministic query record identifier")
    concept_id: str = Field(..., description="Information-need concept identifier")
    query_language: BenchmarkLanguage = Field(..., description="Language classification of query")
    chunk_strategy: str = Field(..., description="Chunking strategy name e.g. page_v1")
    rank: int = Field(..., ge=1, description="1-based rank position in top-k results")
    chunk_id: str = Field(..., description="Deterministic identifier of retrieved chunk")
    score: float = Field(..., ge=0.0, description="BM25 Okapi relevance score")
    document_id: str = Field(..., description="Target document identifier of retrieved chunk")
    source_pages: List[int] = Field(..., description="1-based source pages spanned by retrieved chunk")
    page_start: int = Field(..., ge=1, description="Starting page index")
    page_end: int = Field(..., ge=1, description="Ending page index")
    is_relevant: bool = Field(
        ..., description="Whether chunk matches gold document_id, intersects gold pages, AND has score > 0.0"
    )


class SingleQueryRetrievalRecord(BaseModel):
    """Schema representing top-k retrieval results for a single query record."""

    model_config = ConfigDict(extra="forbid")

    benchmark_id: str = Field(..., description="Deterministic query record identifier")
    concept_id: str = Field(..., description="Information-need concept identifier")
    query_language: BenchmarkLanguage = Field(..., description="Language classification")
    query_text: str = Field(..., description="Query string text")
    chunk_strategy: str = Field(..., description="Chunking strategy evaluated")
    answerability: str = Field(..., description="ANSWERABLE or UNANSWERABLE")
    expected_document_ids: List[str] = Field(default_factory=list, description="Gold target document IDs")
    relevant_pages: List[int] = Field(default_factory=list, description="Gold target 1-based page numbers")
    top_results: List[RetrievalResultItem] = Field(..., description="Top-k retrieved chunk items")
    first_relevant_rank: Optional[int] = Field(
        default=None, description="1-based rank of first relevant chunk with score > 0.0 (None if not found in top-k)"
    )
    has_zero_overlap: bool = Field(
        ..., description="Whether all retrieved chunks for this query have score == 0.0"
    )


class MetricBreakdown(BaseModel):
    """Hit@K and MRR@10 retrieval metrics for a query set."""

    model_config = ConfigDict(extra="forbid")

    query_count: int = Field(..., ge=0, description="Total queries in subset")
    zero_overlap_count: int = Field(..., ge=0, description="Queries with zero lexical overlap (score == 0.0)")
    zero_overlap_pct: float = Field(..., ge=0.0, le=100.0, description="Percentage of queries with zero overlap")
    hit_at_1: float = Field(..., ge=0.0, le=1.0, description="Hit@1 rate")
    hit_at_3: float = Field(..., ge=0.0, le=1.0, description="Hit@3 rate")
    hit_at_5: float = Field(..., ge=0.0, le=1.0, description="Hit@5 rate")
    hit_at_10: float = Field(..., ge=0.0, le=1.0, description="Hit@10 rate")
    mrr_at_10: float = Field(..., ge=0.0, le=1.0, description="Mean Reciprocal Rank @ 10")


class StrategyEvaluationSummary(BaseModel):
    """Evaluation summary metrics for a single chunking strategy."""

    model_config = ConfigDict(extra="forbid")

    chunk_strategy: str = Field(..., description="Chunking strategy name")
    total_indexed_chunks: int = Field(..., ge=1, description="Number of chunks indexed")
    overall_answerable: MetricBreakdown = Field(..., description="Metrics across all 30 answerable queries")
    english: MetricBreakdown = Field(..., description="Metrics across 10 English answerable queries")
    urdu: MetricBreakdown = Field(..., description="Metrics across 10 Urdu answerable queries")
    roman_urdu: MetricBreakdown = Field(..., description="Metrics across 10 Roman Urdu answerable queries")
    unanswerable_query_count: int = Field(default=6, description="Count of unanswerable queries evaluated separately")


class ConceptRankComparison(BaseModel):
    """Concept-aligned first relevant rank comparison across language variants."""

    model_config = ConfigDict(extra="forbid")

    concept_id: str = Field(..., description="Information-need concept identifier")
    english_rank: Optional[int] = Field(default=None, description="First relevant rank for English query")
    urdu_rank: Optional[int] = Field(default=None, description="First relevant rank for Urdu query")
    roman_urdu_rank: Optional[int] = Field(default=None, description="First relevant rank for Roman Urdu query")
