# Loads settings from the .env file so we never hardcode secrets.
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-2.5-flash")
EMBED_MODEL = os.getenv("EMBED_MODEL", "gemini-embedding-001")

# Where ChromaDB stores its files on disk (survives server restarts)
CHROMA_PATH = "./chroma_db"

# Chunking settings (measured in characters)
CHUNK_SIZE = 1000      # size of each text piece
CHUNK_OVERLAP = 200    # overlap so sentences cut at the edge aren't lost

# How many chunks to retrieve for each question
TOP_K = 5

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing. Add it to backend/.env")