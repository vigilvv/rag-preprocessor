from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EmbeddingConfig:
    """Configuration for the embedding model."""

    embedding_model: str
    collection_name: str
    vector_size: int

    @staticmethod
    def load(retriever_config: dict[str, Any]) -> "EmbeddingConfig":
        return EmbeddingConfig(
            embedding_model=retriever_config["embedding_model"],
            collection_name=retriever_config["collection_name"],
            vector_size=retriever_config["vector_size"]
        )
