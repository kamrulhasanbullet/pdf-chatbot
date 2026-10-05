# Step 1 of RAG: turn a PDF into small text chunks.
from io import BytesIO
from pypdf import PdfReader
from .config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_pages(file_bytes: bytes) -> list[tuple[int, str]]:
    """Return a list of (page_number, page_text) from a PDF."""
    reader = PdfReader(BytesIO(file_bytes))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:  # skip empty pages (e.g. scanned images)
            pages.append((i, text))
    return pages


def split_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks using a sliding window."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += size - overlap  # move forward, but keep some overlap
    return chunks


def pdf_to_chunks(file_bytes: bytes) -> list[dict]:
    """Full pipeline: PDF bytes -> list of {text, page} chunks."""
    result = []
    for page_num, page_text in extract_pages(file_bytes):
        for chunk in split_text(page_text):
            result.append({"text": chunk, "page": page_num})
    return result