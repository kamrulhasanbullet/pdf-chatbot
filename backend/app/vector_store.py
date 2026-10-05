# Step 3 of RAG: store vectors in ChromaDB and search them.
import uuid
import chromadb
from .config import CHROMA_PATH, TOP_K

# PersistentClient saves data to disk, so it survives restarts.
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# One collection holds ALL documents. "cosine" = how similarity is measured.
collection = chroma_client.get_or_create_collection(
    name="pdf_docs",
    metadata={"hnsw:space": "cosine"},
)


def add_chunks(filename: str, chunks: list[dict], vectors: list[list[float]]) -> None:
    """Save chunks + their vectors, tagged with the source filename."""
    collection.add(
        ids=[str(uuid.uuid4()) for _ in chunks],
        documents=[c["text"] for c in chunks],
        embeddings=vectors,
        metadatas=[{"source": filename, "page": c["page"]} for c in chunks],
    )


def search(query_vector: list[float], k: int = TOP_K) -> list[dict]:
    """Find the k most similar chunks to the question."""
    if collection.count() == 0:
        return []
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(k, collection.count()),
    )
    hits = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        hits.append({"text": doc, "source": meta["source"], "page": meta["page"]})
    return hits


def list_documents() -> list[str]:
    """Return the unique filenames currently stored."""
    data = collection.get(include=["metadatas"])
    return sorted({m["source"] for m in data["metadatas"]})


def delete_document(filename: str) -> None:
    """Remove all chunks that belong to one file."""
    collection.delete(where={"source": filename})
