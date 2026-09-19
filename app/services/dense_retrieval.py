"""Multilingual Dense Embedding & Retrieval Service for Phase 2C baseline experiments."""

import math
from typing import Dict, List, Optional, Tuple
from app.schemas.chunk import ChunkRecord
from app.schemas.dense import DenseModelConfig, QueryTruncationStatRecord, TruncationStatRecord

# FROZEN MODEL CONFIGURATIONS (Pre-experiment model freeze)
FROZEN_DENSE_MODELS: Dict[str, DenseModelConfig] = {
    "multilingual-e5-base": DenseModelConfig(
        model_id="intfloat/multilingual-e5-base",
        model_revision="d7dbd2363595f4e19f7f45c8f85f8c65f97332f1",
        embedding_dimension=768,
        max_sequence_length=512,
        normalized=True,
        similarity_function="cosine_dot_product",
        query_prefix="query: ",
        passage_prefix="passage: ",
        role_description="retrieval-specialized multilingual baseline",
    ),
    "bge-m3": DenseModelConfig(
        model_id="BAAI/bge-m3",
        model_revision="5617a9f61b028005a4858fdac845db4034724a87",
        embedding_dimension=1024,
        max_sequence_length=8192,
        normalized=True,
        similarity_function="cosine_dot_product",
        query_prefix="",
        passage_prefix="",
        role_description="multilingual dense retrieval / multi-granularity baseline (dense embeddings only)",
    ),
    "paraphrase-multilingual-mpnet-base-v2": DenseModelConfig(
        model_id="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        model_revision="79f238270bbb1999f3659424750eed546059d18f",
        embedding_dimension=768,
        max_sequence_length=128,
        normalized=True,
        similarity_function="cosine_dot_product",
        query_prefix="",
        passage_prefix="",
        role_description="general multilingual semantic embedding baseline",
    ),
}


def l2_normalize_vector(vec: List[float]) -> List[float]:
    """Compute L2-normalized vector."""
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        return [0.0] * len(vec)
    return [x / norm for x in vec]


def l2_normalize_matrix(matrix: List[List[float]]) -> List[List[float]]:
    """Compute L2-normalized 2D matrix."""
    return [l2_normalize_vector(row) for row in matrix]


def compute_dot_product(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute dot product of two vectors."""
    return sum(a * b for a, b in zip(vec_a, vec_b))


def compute_cosine_similarities(
    query_vec: List[float], doc_vecs: List[List[float]]
) -> List[float]:
    """Compute full-precision cosine similarities (dot product of L2-normalized vectors)."""
    norm_q = l2_normalize_vector(query_vec)
    sims = []
    for doc_v in doc_vecs:
        norm_d = l2_normalize_vector(doc_v)
        sims.append(compute_dot_product(norm_q, norm_d))
    return sims


def measure_chunk_truncation(
    chunks: List[ChunkRecord],
    config: DenseModelConfig,
    tokenizer_fn: Optional[callable] = None,
) -> TruncationStatRecord:
    """Measure the number and percentage of chunks that exceed model max sequence length.

    If tokenizer_fn is provided (during real execution), exact token length is measured
    including special tokens and model-specific passage prefixes.
    Otherwise, a word-based fallback is used.
    """
    total = len(chunks)
    if total == 0:
        return TruncationStatRecord(
            model_id=config.model_id,
            chunk_strategy=chunks[0].strategy if chunks else "unknown",
            max_sequence_length=config.max_sequence_length,
            total_chunks=0,
            truncated_chunk_count=0,
            truncated_chunk_pct=0.0,
        )

    truncated_count = 0
    strategy_name = chunks[0].strategy

    for chunk in chunks:
        formatted_text = config.passage_prefix + chunk.text
        if tokenizer_fn is not None:
            token_count = len(tokenizer_fn(formatted_text))
        else:
            token_count = int(len(formatted_text.split()) * 1.3)

        if token_count > config.max_sequence_length:
            truncated_count += 1

    pct = round((truncated_count / total) * 100.0, 2)
    return TruncationStatRecord(
        model_id=config.model_id,
        chunk_strategy=strategy_name,
        max_sequence_length=config.max_sequence_length,
        total_chunks=total,
        truncated_chunk_count=truncated_count,
        truncated_chunk_pct=pct,
    )


def measure_query_truncation(
    query_texts: List[str],
    config: DenseModelConfig,
    tokenizer_fn: Optional[callable] = None,
) -> QueryTruncationStatRecord:
    """Measure the number and percentage of benchmark queries that exceed model max sequence length."""
    total = len(query_texts)
    if total == 0:
        return QueryTruncationStatRecord(
            model_id=config.model_id,
            max_sequence_length=config.max_sequence_length,
            total_queries=0,
            truncated_query_count=0,
            truncated_query_pct=0.0,
        )

    truncated_count = 0
    for q_text in query_texts:
        formatted_query = config.query_prefix + q_text
        if tokenizer_fn is not None:
            token_count = len(tokenizer_fn(formatted_query))
        else:
            token_count = int(len(formatted_query.split()) * 1.3)

        if token_count > config.max_sequence_length:
            truncated_count += 1

    pct = round((truncated_count / total) * 100.0, 2)
    return QueryTruncationStatRecord(
        model_id=config.model_id,
        max_sequence_length=config.max_sequence_length,
        total_queries=total,
        truncated_query_count=truncated_count,
        truncated_query_pct=pct,
    )


class SyntheticDenseRetrievalEngine:
    """Deterministic dense retrieval engine operating over synthetic vector matrices (for offline tests)."""

    def __init__(
        self,
        chunks: List[ChunkRecord],
        doc_embeddings: List[List[float]],
        config: DenseModelConfig,
    ):
        if len(chunks) != len(doc_embeddings):
            raise ValueError("Number of chunks must match number of document embeddings.")
        self.chunks = chunks
        self.config = config
        self.doc_embeddings = l2_normalize_matrix(doc_embeddings)

    def search(
        self, query_vec: List[float], top_k: int = 10
    ) -> List[Tuple[ChunkRecord, float]]:
        """Rank chunks by FULL-PRECISION cosine similarity with deterministic tie-breaking.

        Ranking Sequence:
            1. Compute unrounded full-precision similarity score for each document.
            2. Primary sort: Full-precision score descending (-score).
            3. Secondary sort: chunk_id ascending (chunk.chunk_id).
            4. Post-ranking float serialization: round score to 6 decimal places for display/artifact storage.
        """
        norm_q = l2_normalize_vector(query_vec)
        raw_results = []

        for idx, doc_vec in enumerate(self.doc_embeddings):
            # FULL PRECISION similarity score for sorting
            full_score = compute_dot_product(norm_q, doc_vec)
            raw_results.append((self.chunks[idx], full_score))

        # Sort using unrounded full-precision score
        raw_results.sort(key=lambda item: (-item[1], item[0].chunk_id))

        # Format output with 6-decimal rounded score AFTER ranking has completed
        final_results = []
        for chunk, full_score in raw_results[:top_k]:
            final_results.append((chunk, round(full_score, 6)))

        return final_results
