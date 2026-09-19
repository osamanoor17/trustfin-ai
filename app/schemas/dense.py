"""Pydantic schemas for Phase 2C Multilingual Dense Retrieval Baseline experiments."""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.benchmark import BenchmarkLanguage


class DenseModelConfig(BaseModel):
    """Configuration metadata for a dense embedding model candidate."""

    model_config = ConfigDict(extra="forbid")

    model_id: str = Field(..., description="Hugging Face model repository identifier")
    model_revision: str = Field(..., description="Exact Hugging Face commit SHA revision")
    embedding_dimension: int = Field(..., ge=1, description="Output embedding vector dimension")
    max_sequence_length: int = Field(..., ge=1, description="Maximum token sequence length supported")
    normalized: bool = Field(default=True, description="Whether embedding vectors are L2-normalized")
    similarity_function: str = Field(default="cosine_dot_product", description="Vector similarity metric")
    query_prefix: str = Field(default="", description="Mandatory prefix for query text")
    passage_prefix: str = Field(default="", description="Mandatory prefix for chunk/passage text")
    role_description: str = Field(..., description="Methodological role of model in baseline experiment")


class TruncationStatRecord(BaseModel):
    """Truncation statistics for a model across a chunk strategy."""

    model_config = ConfigDict(extra="forbid")

    model_id: str = Field(..., description="Hugging Face model repository identifier")
    chunk_strategy: str = Field(..., description="Chunking strategy evaluated")
    max_sequence_length: int = Field(..., ge=1, description="Model token limit")
    total_chunks: int = Field(..., ge=1, description="Total indexed chunks in strategy")
    truncated_chunk_count: int = Field(..., ge=0, description="Count of chunks exceeding model token limit")
    truncated_chunk_pct: float = Field(..., ge=0.0, le=100.0, description="Percentage of chunks truncated")


class QueryTruncationStatRecord(BaseModel):
    """Truncation statistics for a model across all benchmark queries."""

    model_config = ConfigDict(extra="forbid")

    model_id: str = Field(..., description="Hugging Face model repository identifier")
    max_sequence_length: int = Field(..., ge=1, description="Model token limit")
    total_queries: int = Field(..., ge=1, description="Total benchmark queries evaluated")
    truncated_query_count: int = Field(..., ge=0, description="Count of queries exceeding model token limit")
    truncated_query_pct: float = Field(..., ge=0.0, le=100.0, description="Percentage of queries truncated")


class DenseRetrievalResultItem(BaseModel):
    """Schema representing a single ranked retrieved chunk item in dense retrieval."""

    model_config = ConfigDict(extra="forbid")

    benchmark_id: str = Field(..., description="Deterministic query record identifier")
    concept_id: str = Field(..., description="Information-need concept identifier")
    query_language: BenchmarkLanguage = Field(..., description="Language classification of query")
    model_id: str = Field(..., description="Hugging Face model identifier")
    chunk_strategy: str = Field(..., description="Chunking strategy name e.g. page_v1")
    rank: int = Field(..., ge=1, description="1-based rank position in top-k results")
    chunk_id: str = Field(..., description="Deterministic identifier of retrieved chunk")
    score: float = Field(..., description="Dense similarity score (cosine / dot product of normalized vectors)")
    document_id: str = Field(..., description="Target document identifier of retrieved chunk")
    source_pages: List[int] = Field(..., description="1-based source pages spanned by retrieved chunk")
    page_start: int = Field(..., ge=1, description="Starting page index")
    page_end: int = Field(..., ge=1, description="Ending page index")
    is_relevant: bool = Field(
        ..., description="Whether chunk matches gold document_id AND intersects gold pages (regardless of score sign)"
    )


class SingleQueryDenseRecord(BaseModel):
    """Top-k dense retrieval results for a single query record."""

    model_config = ConfigDict(extra="forbid")

    benchmark_id: str = Field(..., description="Deterministic query record identifier")
    concept_id: str = Field(..., description="Information-need concept identifier")
    query_language: BenchmarkLanguage = Field(..., description="Language classification")
    query_text: str = Field(..., description="Raw query string text")
    formatted_query_text: str = Field(..., description="Formatted query text with model prefix")
    model_id: str = Field(..., description="Model identifier")
    chunk_strategy: str = Field(..., description="Chunking strategy evaluated")
    answerability: str = Field(..., description="ANSWERABLE or UNANSWERABLE")
    expected_document_ids: List[str] = Field(default_factory=list, description="Gold target document IDs")
    relevant_pages: List[int] = Field(default_factory=list, description="Gold target 1-based page numbers")
    top_results: List[DenseRetrievalResultItem] = Field(..., description="Top-k retrieved chunk items")
    first_relevant_rank: Optional[int] = Field(
        default=None, description="1-based rank of first relevant chunk (None if not found in top-k)"
    )


class DenseMetricBreakdown(BaseModel):
    """Hit@K and MRR@10 dense retrieval metrics for a query set."""

    model_config = ConfigDict(extra="forbid")

    query_count: int = Field(..., ge=0, description="Total queries in subset")
    hit_at_1: float = Field(..., ge=0.0, le=1.0, description="Hit@1 rate")
    hit_at_3: float = Field(..., ge=0.0, le=1.0, description="Hit@3 rate")
    hit_at_5: float = Field(..., ge=0.0, le=1.0, description="Hit@5 rate")
    hit_at_10: float = Field(..., ge=0.0, le=1.0, description="Hit@10 rate")
    mrr_at_10: float = Field(..., ge=0.0, le=1.0, description="Mean Reciprocal Rank @ 10")


class DenseStrategyEvaluationSummary(BaseModel):
    """Evaluation summary metrics for a dense model across a chunking strategy."""

    model_config = ConfigDict(extra="forbid")

    model_id: str = Field(..., description="Hugging Face model identifier")
    chunk_strategy: str = Field(..., description="Chunking strategy name")
    total_indexed_chunks: int = Field(..., ge=1, description="Number of chunks indexed")
    truncation_stats: TruncationStatRecord = Field(..., description="Truncation statistics")
    overall_answerable: DenseMetricBreakdown = Field(..., description="Metrics across 30 answerable queries")
    english: DenseMetricBreakdown = Field(..., description="Metrics across 10 English queries")
    urdu: DenseMetricBreakdown = Field(..., description="Metrics across 10 Urdu queries")
    roman_urdu: DenseMetricBreakdown = Field(..., description="Metrics across 10 Roman Urdu queries")
    unanswerable_query_count: int = Field(default=6, description="Count of unanswerable queries")
