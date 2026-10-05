# Step 2 of RAG: convert text into vectors (lists of numbers) with Gemini.
import time
from google import genai
from google.genai import types
from .config import GEMINI_API_KEY, EMBED_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

# Free tier is limited (requests/min and tokens/min), so we send small
# batches and pause briefly between them.
BATCH_SIZE = 20
PAUSE_SECONDS = 1.5


def _embed(texts: list[str], task_type: str) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(task_type=task_type),
    )
    return [e.values for e in response.embeddings]


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embed many chunks (used when uploading a PDF)."""
    vectors = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        vectors.extend(_embed(batch, "RETRIEVAL_DOCUMENT"))
        time.sleep(PAUSE_SECONDS)  # be gentle with the free-tier rate limit
    return vectors


def embed_query(question: str) -> list[float]:
    """Embed one user question (used when searching)."""
    return _embed([question], "RETRIEVAL_QUERY")[0]
