import os
import faiss
import pickle
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from app.models.schema import SourceChunk, ChunkMetadata

# === FAISS Index Directory ===
INDEX_ROOT = "vector_indexes"
os.makedirs(INDEX_ROOT, exist_ok=True)

# === Embedding Model ===
embedding_model = SentenceTransformer("BAAI/bge-base-en-v1.5")  # ✅ Solid for production

# === Embedding Helper ===
def embed_chunks(chunks: List[str]) -> np.ndarray:
    return embedding_model.encode(chunks, show_progress_bar=False).astype(np.float32)

# === Core Indexing Logic ===
def create_faiss_index(chunks: List[str], metadata: List[Dict]) -> faiss.Index:
    embeddings = embed_chunks(chunks)
    dim = embeddings.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    # Attach chunk content and metadata to index
    index.chunk_texts = chunks
    index.chunk_metadata = metadata
    return index

# === Save Index to Disk ===
def save_faiss_index(index: faiss.Index, index_name: str):
    faiss.write_index(index, os.path.join(INDEX_ROOT, f"{index_name}.index"))
    with open(os.path.join(INDEX_ROOT, f"{index_name}_meta.pkl"), "wb") as f:
        pickle.dump({
            "texts": index.chunk_texts,
            "meta": index.chunk_metadata
        }, f)

# === Load Index from Disk ===
def load_faiss_index(index_name: str) -> faiss.Index:
    index_path = os.path.join(INDEX_ROOT, f"{index_name}.index")
    meta_path = os.path.join(INDEX_ROOT, f"{index_name}_meta.pkl")

    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise FileNotFoundError(f"FAISS index or metadata not found for: {index_name}")

    index = faiss.read_index(index_path)
    with open(meta_path, "rb") as f:
        meta = pickle.load(f)

    index.chunk_texts = meta["texts"]
    index.chunk_metadata = meta["meta"]
    return index

# === Retrieve Top-k Chunks ===
def get_top_k_chunks(query: str, index: faiss.Index, top_k: int = 5) -> List[SourceChunk]:
    query_vec = embed_chunks([query])
    distances, indices = index.search(query_vec, top_k)

    results = []
    for i in indices[0]:
        if 0 <= i < len(index.chunk_texts):
            chunk_meta = ChunkMetadata(
                chunk_index=i,
                source=getattr(index, "source_name", None),
                page=getattr(index, "chunk_pages", {}).get(i),
                word_count=len(index.chunk_texts[i].split())
            )
            results.append(SourceChunk(
                content=index.chunk_texts[i],
                metadata=chunk_meta.dict()  # ✅ Dict for pydantic validation
            ))

    return results

# === Index Entry Point ===
def index_document(chunks: List[str], index_name: str, metadata: List[Dict], save_index: bool = True):
    index = create_faiss_index(chunks, metadata)
    if save_index:
        save_faiss_index(index, index_name)
    return index
