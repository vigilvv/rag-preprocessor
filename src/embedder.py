"""
Creates embedding and stores it to json along with metadata and raw chunks
"""

from config import EmbeddingConfig
from typing import List
import structlog
import asyncio

from embedding import EmbeddingTaskType, GeminiEmbedding
import google.api_core.exceptions

from utils import load_json, save_json

from settings import settings
logger = structlog.get_logger(__name__)


input_config = load_json(settings.input_path / "config.json")
embedding_config = EmbeddingConfig.load(input_config["embedding_config"])


CRAWLED_DEPTH = 2
CHUNKING_STRATEGY = "simple"
CHUNKED_SAVE_FILE = f"data/chunked_data/flare-network_{CHUNKING_STRATEGY}_d{CRAWLED_DEPTH}.json"
EMBEDDING_SAVE_FILE = f"data/embedding_data/flare-network_{CHUNKING_STRATEGY}_d{CRAWLED_DEPTH}.json"


async def get_embedding(text: str, url: str) -> List[float]:
    """Get embedding vector from Gemini."""
    # try:
    #     response = await openai_client.embeddings.create(
    #         model="text-embedding-3-small",
    #         input=text
    #     )
    #     return response.data[0].embedding
    # except Exception as e:
    #     print(f"Error getting embedding: {e}")
    #     return [0] * 1536  # Return zero vector on error
    embedding_client = GeminiEmbedding(settings.gemini_api_key)

    try:
        embedding = embedding_client.embed_content(
            embedding_model=embedding_config.embedding_model,
            task_type=EmbeddingTaskType.RETRIEVAL_DOCUMENT,
            contents=text,
            # title=url,
        )

        return embedding
    except google.api_core.exceptions.InvalidArgument as e:
        # Check if it's the known "Request payload size exceeds the limit" error
        # If so, downgrade it to a warning
        if "400 Request payload size exceeds the limit" in str(e):
            logger.warning(
                "Skipping document due to size limit.",
                filename=url,
            )

        # Log the full traceback for other InvalidArgument errors
        logger.exception(
            "Error encoding document (InvalidArgument).",
            filename=url,
        )

    except Exception:
        # Log the full traceback for any other errors
        logger.exception(
            "Error encoding document (general).",
            filename=url,
        )

        return embedding


# Write your own post chunk processor to match your needs
def postprocess_chunks(all_chunks):
    """
    Remove chunks when "chunk": ""
    Remove chunks when "page_title" starts with "Access denied"
    """
    processed_chunks = []

    for index, chunk in enumerate(all_chunks):
        if (chunk["chunk"] == ""):
            print("Chunk has no text")
            print(f"Removing chunk {index}")
            continue
        elif (chunk["page_title"].startswith("Access denied")):
            print("Access denied page")
            print(f"Removing chunk {index}")
            continue
        else:
            processed_chunks.append(chunk)

    return processed_chunks


async def embedder_main():
    all_chunks = load_json(settings.input_path / CHUNKED_SAVE_FILE)

    postprocessed_chunks = postprocess_chunks(all_chunks)

    all_chunk_embeddings = []

    for index, chunk in enumerate(postprocessed_chunks):
        print(f"Processing {index}/{len(postprocessed_chunks)}")

        try:
            embedding = await get_embedding(chunk["chunk"], chunk["page_url"])
            chunk["embedding"] = embedding
            all_chunk_embeddings.append(chunk)
            print(chunk)

            # After processing every 5 chunks, wait for 10 seconds
            if (index + 1) % 10 == 0:
                print(f"Processed {index} chunks, waiting for 60 seconds...")
                # Delay for 60 seconds after every 5 chunks
                await asyncio.sleep(60)
        except Exception:
            raise Exception(f"Error processing chunk {chunk['page_url']}")

    save_json(all_chunk_embeddings, settings.input_path / EMBEDDING_SAVE_FILE)


if __name__ == "__main__":
    asyncio.run(embedder_main())
