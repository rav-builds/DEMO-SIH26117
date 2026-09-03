"""
Qdrant vector store wrapper for the RAG pipeline.

Provides collection management, vector upsert, similarity search,
and source-level deletion. Uses the qdrant-client library.
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.config import settings

logger = logging.getLogger(__name__)


class QdrantStore:
    """
    Wrapper around the Qdrant vector database for document chunk storage
    and semantic similarity search.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection_name: Optional[str] = None,
        vector_size: Optional[int] = None,
    ):
        self.url = url or settings.qdrant_url
        self.api_key = api_key or settings.qdrant_api_key
        self.collection_name = collection_name or settings.qdrant_collection_name
        self.vector_size = vector_size or settings.embedding_dimension

        self._client: Optional[QdrantClient] = None

    def _get_client(self) -> QdrantClient:
        """Lazily initialize the Qdrant client."""
        if self._client is None:
            kwargs: Dict[str, Any] = {"url": self.url, "timeout": 30}
            if self.api_key:
                kwargs["api_key"] = self.api_key
            self._client = QdrantClient(**kwargs)
        return self._client

    def ensure_collection(self) -> None:
        """Create the collection if it doesn't already exist."""
        client = self._get_client()

        collections = client.get_collections().collections
        existing_names = {c.name for c in collections}

        if self.collection_name not in existing_names:
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=self.vector_size,
                    distance=qmodels.Distance.COSINE,
                ),
            )
            logger.info(
                "Created Qdrant collection '%s' (dim=%d, cosine)",
                self.collection_name,
                self.vector_size,
            )
        else:
            logger.debug("Qdrant collection '%s' already exists.", self.collection_name)

    def upsert(
        self,
        chunks: List[Dict[str, Any]],
        vectors: List[List[float]],
    ) -> int:
        """
        Upsert document chunks with their embedding vectors.

        Args:
            chunks: List of dicts, each with at least 'text' and optionally
                    'source', 'page', 'chunk_index', etc.
            vectors: Corresponding embedding vectors.

        Returns:
            Number of points upserted.
        """
        if len(chunks) != len(vectors):
            raise ValueError(
                f"Chunk/vector count mismatch: {len(chunks)} chunks vs {len(vectors)} vectors"
            )

        if not chunks:
            return 0

        client = self._get_client()

        points = []
        for chunk, vector in zip(chunks, vectors):
            point_id = str(uuid4())
            payload = {
                "text": chunk.get("text", ""),
                "source": chunk.get("source", "unknown"),
                "page": chunk.get("page"),
                "chunk_index": chunk.get("chunk_index"),
                **{k: v for k, v in chunk.items() if k not in ("text", "source", "page", "chunk_index")},
            }
            points.append(qmodels.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload,
            ))

        client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        logger.info("Upserted %d points into '%s'", len(points), self.collection_name)
        return len(points)

    def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
        source_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search.

        Args:
            query_vector: The query embedding vector.
            limit: Maximum number of results.
            score_threshold: Minimum similarity score (0.0 - 1.0).
            source_filter: Optional filter to restrict results to a specific source.

        Returns:
            List of dicts with 'text', 'score', 'source', and other metadata.
        """
        client = self._get_client()

        query_filter = None
        if source_filter:
            query_filter = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="source",
                        match=qmodels.MatchValue(value=source_filter),
                    )
                ]
            )

        results = client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )

        return [
            {
                "id": str(hit.id),
                "score": hit.score,
                "text": hit.payload.get("text", "") if hit.payload else "",
                "source": hit.payload.get("source", "") if hit.payload else "",
                "page": hit.payload.get("page") if hit.payload else None,
                "chunk_index": hit.payload.get("chunk_index") if hit.payload else None,
            }
            for hit in results
        ]

    def delete_by_source(self, source: str) -> None:
        """Delete all points associated with a specific source document."""
        client = self._get_client()

        client.delete(
            collection_name=self.collection_name,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="source",
                            match=qmodels.MatchValue(value=source),
                        )
                    ]
                )
            ),
        )
        logger.info("Deleted points for source '%s' from '%s'", source, self.collection_name)

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection statistics."""
        client = self._get_client()
        info = client.get_collection(self.collection_name)
        return {
            "name": self.collection_name,
            "points_count": info.points_count,
            "vectors_count": info.vectors_count,
            "status": info.status.value if info.status else "unknown",
        }

    def close(self) -> None:
        """Close the Qdrant client connection."""
        if self._client is not None:
            self._client.close()
            self._client = None


# Singleton vector store instance
vector_store = QdrantStore()
