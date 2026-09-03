"""
Batched embedding generation service.

Uses the model registry's embedding client to generate vector embeddings
with automatic batching (default batch size 32) to optimize throughput
and avoid overwhelming the local serving engine.
"""

import logging
from typing import List, Optional

from app.config import settings
from app.models.registry import model_registry

logger = logging.getLogger(__name__)

# Default batch size for embedding requests
DEFAULT_BATCH_SIZE = 32


class EmbeddingService:
    """
    Generates vector embeddings for text chunks using the local embedding model.

    Automatically batches requests to prevent memory pressure on the serving engine
    and to stay within per-request token limits.
    """

    def __init__(self, batch_size: int = DEFAULT_BATCH_SIZE):
        self.batch_size = batch_size

    def _get_client(self):
        """Get the embedding client from the model registry."""
        return model_registry.get_client(role="embedding")

    async def embed_texts(
        self,
        texts: List[str],
        model: Optional[str] = None,
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts with automatic batching.

        Args:
            texts: List of text strings to embed.
            model: Optional model override (defaults to configured embedding model).

        Returns:
            List of embedding vectors (one per input text), in the same order.
        """
        if not texts:
            return []

        client = self._get_client()
        target_model = model or settings.default_embedding_model

        all_embeddings: List[List[float]] = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size

        for batch_idx in range(total_batches):
            start = batch_idx * self.batch_size
            end = min(start + self.batch_size, len(texts))
            batch = texts[start:end]

            logger.debug(
                "Embedding batch %d/%d (%d texts)", batch_idx + 1, total_batches, len(batch)
            )

            try:
                batch_embeddings = await client.embeddings(batch, model=target_model)
                all_embeddings.extend(batch_embeddings)
            except Exception as exc:
                logger.error(
                    "Embedding batch %d/%d failed: %s", batch_idx + 1, total_batches, exc
                )
                raise

        if len(all_embeddings) != len(texts):
            logger.warning(
                "Embedding count mismatch: expected %d, got %d",
                len(texts), len(all_embeddings),
            )

        return all_embeddings

    async def embed_single(self, text: str, model: Optional[str] = None) -> List[float]:
        """Generate embedding for a single text string."""
        results = await self.embed_texts([text], model=model)
        if not results:
            raise RuntimeError("Embedding returned empty result")
        return results[0]


# Singleton embedding service
embedding_service = EmbeddingService()
