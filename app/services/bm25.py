"""Pure Python Okapi BM25 implementation for Phase 2B lexical retrieval baseline."""

import math
import re
from typing import Dict, List, Tuple
from app.schemas.chunk import ChunkRecord


def tokenize_text(text: str) -> List[str]:
    r"""Explicit lexical baseline tokenizer.

    - Unicode-aware lowercasing of Latin characters.
    - Whitespace & punctuation tokenization via regex r'[^\W_]+'.
    - Preserves Urdu script character sequences intact.
    - No stemming, lemmatization, stop-word removal, translation, or LLM normalization.
    """
    if not text:
        return []
    return re.findall(r"[^\W_]+", text.lower())


class BM25Okapi:
    """Okapi BM25 ranking algorithm implementation.

    Scoring Equation:
        Score(d, Q) = sum_{q in Q} IDF(q) * (f(q, d) * (k1 + 1)) / (f(q, d) + k1 * (1 - b + b * (|d| / avgdl)))

    Smoothed Non-Negative IDF Equation:
        IDF(q) = ln((N - n(q) + 0.5) / (n(q) + 0.5) + 1)

    where:
        N = total number of chunks in collection
        n(q) = number of chunks containing token q
        f(q, d) = term frequency of q in chunk d
        |d| = document (chunk) length in tokens
        avgdl = average document length across collection
        k1 = 1.5 (fixed parameter)
        b = 0.75 (fixed parameter)

    Duplicate Query Term Semantics:
        Repeated query terms contribute additively. If a query contains duplicate
        tokens (e.g., ['cat', 'cat']), each occurrence accumulates its term score
        independently during iteration over query tokens.
    """

    def __init__(self, chunks: List[ChunkRecord], k1: float = 1.5, b: float = 0.75):
        """Initialize BM25 index over a list of ChunkRecord items."""
        self.k1 = k1
        self.b = b
        self.chunks = chunks
        self.corpus_size = len(chunks)

        self.doc_tokens: List[List[str]] = []
        self.doc_len: List[int] = []
        self.doc_freqs: List[Dict[str, int]] = []
        self.df: Dict[str, int] = {}
        total_len = 0

        for chunk in chunks:
            tokens = tokenize_text(chunk.text)
            self.doc_tokens.append(tokens)
            d_len = len(tokens)
            self.doc_len.append(d_len)
            total_len += d_len

            freqs: Dict[str, int] = {}
            for token in tokens:
                freqs[token] = freqs.get(token, 0) + 1
            self.doc_freqs.append(freqs)

            for token in freqs.keys():
                self.df[token] = self.df.get(token, 0) + 1

        self.avgdl = (total_len / self.corpus_size) if self.corpus_size > 0 else 0.0

        # Precompute IDF values
        self.idf: Dict[str, float] = {}
        for token, freq in self.df.items():
            # Smoothed non-negative Okapi IDF formula
            self.idf[token] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1.0)

    def score_query(self, query_tokens: List[str]) -> List[float]:
        """Compute BM25 score for a query across all indexed chunks."""
        scores = [0.0] * self.corpus_size
        if self.corpus_size == 0 or not query_tokens:
            return scores

        for token in query_tokens:
            if token not in self.idf:
                continue
            idf_val = self.idf[token]
            for idx in range(self.corpus_size):
                f = self.doc_freqs[idx].get(token, 0)
                if f == 0:
                    continue
                d_len = self.doc_len[idx]
                denom = f + self.k1 * (1.0 - self.b + self.b * (d_len / self.avgdl))
                num = f * (self.k1 + 1.0)
                scores[idx] += idf_val * (num / denom)

        return scores

    def search(
        self, query_text: str, top_k: int = 10
    ) -> List[Tuple[ChunkRecord, float]]:
        """Retrieve top-k chunks for a query with deterministic tie-breaking.

        Tie-breaking rule:
            Primary sort: BM25 score descending (-score)
            Secondary sort: chunk_id ascending (chunk.chunk_id)
        """
        query_tokens = tokenize_text(query_text)
        scores = self.score_query(query_tokens)

        # Index paired with chunk and score
        results = []
        for idx, score in enumerate(scores):
            results.append((self.chunks[idx], round(score, 6)))

        # Deterministic sort: score descending, then chunk_id ascending
        results.sort(key=lambda item: (-item[1], item[0].chunk_id))

        return results[:top_k]
