# FastAPI app: exposes upload / ask / list / delete endpoints.
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .pdf_utils import pdf_to_chunks
from .embeddings import embed_documents
from .vector_store import add_chunks, list_documents, delete_document
from .rag import answer_question

app = FastAPI(title="Multi-Doc PDF Chatbot")

# Allow the Next.js dev server to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are allowed.")

    data = await file.read()
    if len(data) > 15 * 1024 * 1024:  # 15 MB limit keeps free-tier usage safe
        raise HTTPException(400, "File too large (max 15 MB).")

    chunks = pdf_to_chunks(data)
    if not chunks:
        raise HTTPException(400, "No readable text found (is it a scanned PDF?).")

    try:
        vectors = embed_documents([c["text"] for c in chunks])
    except Exception as e:
        raise HTTPException(502, f"Embedding failed (rate limit?): {e}")

    # Re-uploading the same file replaces the old version
    delete_document(file.filename)
    add_chunks(file.filename, chunks, vectors)
    return {"filename": file.filename, "chunks": len(chunks)}


@app.post("/ask")
async def ask(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(400, "Question is empty.")
    try:
        return answer_question(req.question)
    except Exception as e:
        raise HTTPException(502, f"Gemini request failed: {e}")


@app.get("/documents")
async def documents():
    return {"documents": list_documents()}


@app.delete("/documents/{filename}")
async def remove_document(filename: str):
    delete_document(filename)
    return {"deleted": filename}
