"""
Reads result.json and chunks data based on the selected chunking strategy
"""

from utils import load_json, save_json

from settings import settings
CRAWLED_DEPTH = 2
DATASET = f"data/crawled_data/flare-network_depth{CRAWLED_DEPTH}.json"
CHUNKING_STRATEGY = "simple"
CHUNKED_SAVE_FILE = f"data/chunked_data/flare-network_{CHUNKING_STRATEGY}_d{CRAWLED_DEPTH}.json"

# CHUNKING_STRATEGY
# "simple" -> code blocks > para breaks > sentence breaks

# Todo: Eliminate duplicate urls and "Access denied" pages


def simple_chunking(text: str, chunk_size: int = 5000):
    """Split text into chunks, respecting code blocks and paragraphs."""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        # Calculate end position
        end = start + chunk_size

        # If we're at the end of the text, just take what's left
        if end >= text_length:
            chunks.append(text[start:].strip())
            break

        # Try to find a code block boundary first (```)
        chunk = text[start:end]
        code_block = chunk.rfind('```')
        if code_block != -1 and code_block > chunk_size * 0.3:
            end = start + code_block

        # If no code block, try to break at a paragraph
        elif '\n\n' in chunk:
            # Find the last paragraph break
            last_break = chunk.rfind('\n\n')
            if last_break > chunk_size * 0.3:  # Only break if we're past 30% of chunk_size
                end = start + last_break

        # If no paragraph break, try to break at a sentence
        elif '. ' in chunk:
            # Find the last sentence break
            last_period = chunk.rfind('. ')
            if last_period > chunk_size * 0.3:  # Only break if we're past 30% of chunk_size
                end = start + last_period + 1

        # Extract chunk and clean it up
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start position for next chunk
        start = max(start + 1, end)

    return chunks


def chunker_main():
    raw_data = load_json(settings.input_path / DATASET)

    all_chunks = []

    for file in raw_data:
        file_chunks = simple_chunking(file["file"])

        for index, chunk in enumerate(file_chunks):
            all_chunks.append({
                "page_url": file["url"],
                "page_title": file["page_title"],
                "page_description": file["page_description"],
                "chunk_number": index,
                "chunk": chunk
            })

    save_json(all_chunks, settings.input_path / CHUNKED_SAVE_FILE)


if __name__ == "__main__":
    chunker_main()
