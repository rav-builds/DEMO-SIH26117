"""
Hybrid retriever combining Vector Similarity Search + BM25 for the RAG pipeline.

Uses Reciprocal Rank Fusion (RRF) to merge vector and BM25 scores into
a single ranked result list, improving retrieval quality over either method alone.
"""

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from rank_bm25 import BM25Okapi

from app.rag.embeddings import embedding_service
from app.rag.vector_store import vector_store

logger = logging.getLogger(__name__)

# RRF constant (standard value from the original paper)
_RRF_K = 60


class RetrievedChunk(BaseModel):
    """A single retrieved chunk with combined score and metadata."""

    text: str = Field(..., description="Chunk text content")
    score: float = Field(..., description="Combined retrieval score")
    source: str = Field(default="", description="Source document identifier")
    page: Optional[int] = Field(default=None, description="Page number if available")
    chunk_index: Optional[int] = Field(default=None, description="Chunk index within source")
    vector_score: Optional[float] = Field(default=None, description="Vector similarity score")
    bm25_score: Optional[float] = Field(default=None, description="BM25 relevance score")


def _tokenize(text: str) -> List[str]:
    """Simple whitespace tokenizer for BM25."""
    return text.lower().split()


def _reciprocal_rank_fusion(
    ranked_lists: List[List[str]],
    k: int = _RRF_K,
) -> Dict[str, float]:
    """
    Compute Reciprocal Rank Fusion scores across multiple ranked lists.

    Args:
        ranked_lists: List of ranked document ID lists (highest rank first).
        k: RRF constant (default 60).

    Returns:
        Dict mapping document ID to fused score.
    """
    fused_scores: Dict[str, float] = {}
    for ranked_list in ranked_lists:
        for rank, doc_id in enumerate(ranked_list, start=1):
            if doc_id not in fused_scores:
                fused_scores[doc_id] = 0.0
            fused_scores[doc_id] += 1.0 / (k + rank)
    return fused_scores


class HybridRetriever:
    """
    Combines vector similarity search (Qdrant) with BM25 keyword matching
    using Reciprocal Rank Fusion (RRF) for improved retrieval quality.

    Retrieval strategy:
    1. Generate query embedding → Qdrant vector search (top_k * 2 candidates)
    2. BM25 re-rank the candidate texts against the query
    3. RRF merge of vector and BM25 rankings
    4. Return final top_k results
    """

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: Optional[float] = None,
        source_filter: Optional[str] = None,
    ) -> List[RetrievedChunk]:
        """
        Perform hybrid retrieval (Vector + BM25) with RRF fusion.

        Args:
            query: The natural language search query.
            top_k: Number of final results to return.
            score_threshold: Minimum vector similarity score.
            source_filter: Optional source document filter.

        Returns:
            List of RetrievedChunk objects, ranked by fused score.
        """
        if not query.strip():
            return []

        # Step 1: Generate query embedding
        try:
            query_vector = await embedding_service.embed_single(query)
        except Exception as exc:
            logger.error("Query embedding failed: %s", exc)
            raise

        # Step 2: Vector search (fetch more candidates for BM25 re-ranking)
        candidate_count = max(top_k * 3, 20)
        vector_results = vector_store.search(
            query_vector=query_vector,
            limit=candidate_count,
            score_threshold=score_threshold,
            source_filter=source_filter,
        )

        if not vector_results:
            logger.debug("No vector results for query: %s", query[:100])
            return []

        # Build lookup by ID
        results_by_id: Dict[str, Dict[str, Any]] = {}
        for r in vector_results:
            results_by_id[r["id"]] = r

        # Step 3: BM25 scoring on candidate texts
        candidate_texts = [r["text"] for r in vector_results]
        candidate_ids = [r["id"] for r in vector_results]

        tokenized_corpus = [_tokenize(text) for text in candidate_texts]
        tokenized_query = _tokenize(query)

        bm25 = BM25Okapi(tokenized_corpus)
        bm25_scores = bm25.get_scores(tokenized_query)

        # Create BM25 ranked list (highest score first)
        bm25_ranked = sorted(
            zip(candidate_ids, bm25_scores),
            key=lambda x: x[1],
            reverse=True,
        )
        bm25_ranked_ids = [doc_id for doc_id, _ in bm25_ranked]

        # Create vector ranked list (already sorted by score from Qdrant)
        vector_ranked_ids = candidate_ids

        # Step 4: Reciprocal Rank Fusion
        fused_scores = _reciprocal_rank_fusion([vector_ranked_ids, bm25_ranked_ids])

        # Build BM25 score lookup
        bm25_score_lookup = {doc_id: score for doc_id, score in zip(candidate_ids, bm25_scores)}

        # Sort by fused score and take top_k
        sorted_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)
        top_ids = sorted_ids[:top_k]

        # Build final results
        chunks: List[RetrievedChunk] = []
        for doc_id in top_ids:
            r = results_by_id.get(doc_id)
            if r is None:
                continue
            chunks.append(RetrievedChunk(
                text=r["text"],
                score=round(fused_scores[doc_id], 6),
                source=r.get("source", ""),
                page=r.get("page"),
                chunk_index=r.get("chunk_index"),
                vector_score=r.get("score"),
                bm25_score=round(bm25_score_lookup.get(doc_id, 0.0), 6),
            ))

        logger.info(
            "Hybrid retrieval: query='%s' → %d candidates → %d final results",
            query[:80], len(vector_results), len(chunks),
        )

        return chunks


# Singleton hybrid retriever
hybrid_retriever = HybridRetriever()
