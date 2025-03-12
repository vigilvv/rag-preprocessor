"""
Provides embedding using the Gemini model
"""

from google.generativeai.client import configure
from google.generativeai.embedding import (
    EmbeddingTaskType,
)
from google.generativeai.embedding import (
    embed_content as _embed_content,
)


class GeminiEmbedding:
    def __init__(self, api_key: str) -> None:
        """
        Initialize Gemini with API credentials.
        This client uses google.generativeai

        Args:
            api_key (str): Google API key for authentication
        """
        configure(api_key=api_key)

    def embed_content(
        self,
        embedding_model: str,
        contents: str,
        task_type: EmbeddingTaskType,
        title: str | None = None,
    ) -> list[float]:
        """
        Generate text embeddings using Gemini.

        Args:
            model (str): The embedding model to use (e.g., "text-embedding-004").
            contents (str): The text to be embedded.

        Returns:
            list[float]: The generated embedding vector.
        """
        response = _embed_content(
            model=embedding_model, content=contents, task_type=task_type, title=title
        )
        try:
            embedding = response["embedding"]
        except (KeyError, IndexError) as e:
            msg = "Failed to extract embedding from response."
            raise ValueError(msg) from e
        return embedding
