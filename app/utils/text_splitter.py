from typing import List, Tuple, Dict

def split_text_into_chunks_with_metadata(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150,
    source_name: str = "uploaded_file"
) -> Tuple[List[str], List[Dict]]:
    """
    Splits input text into overlapping chunks and generates metadata for each chunk.

    Args:
        text (str): Full document text.
        chunk_size (int): Number of words per chunk.
        overlap (int): Number of overlapping words between chunks.
        source_name (str): Name of the source file for traceability.

    Returns:
        Tuple[List[str], List[Dict]]: Text chunks and corresponding metadata.
    """
    if not text.strip():
        return [], []

    words = text.split()
    chunks = []
    metadata = []
    start = 0
    chunk_index = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        meta = {
            "source": source_name,
            "chunk_index": chunk_index,
            "char_range": f"{start}-{min(end, len(words))}",
            "word_count": len(chunk.split())
        }
        metadata.append(meta)

        start += max(chunk_size - overlap, 1)
        chunk_index += 1

    return chunks, metadata
