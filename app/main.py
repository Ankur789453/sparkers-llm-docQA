from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from pathlib import Path
import os
import uuid
import logging

from app.app_config import settings
from app.parsers.file_parser import parse_document
from app.retrieval.embedding_engine import index_document
from app.retrieval.search_engine import answer_questions
from app.models.schema import AnswerResponse, UploadResponse
from app.utils.download_and_parse import download_and_parse_pdf

# === Logging Setup ===
logger = logging.getLogger("docqa")
logger.setLevel(settings.LOG_LEVEL)
logging.basicConfig(level=settings.LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")

# === FastAPI App ===
app = FastAPI(title="📄🧠 DocQA - LLM-powered Document QA API")

# === CORS Policy ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Ensure Upload Dir Exists ===
UPLOAD_DIR: Path = settings.UPLOAD_DIR
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# === Health Check ===
@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Backend is live 🔥"}

# === Upload Endpoint ===
@app.post("/upload", response_model=UploadResponse, tags=["Document"])
async def upload_file(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        file_path = UPLOAD_DIR / filename

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Parse and index
        text_chunks, metadata = parse_document(str(file_path))  # modified parse_document to return both
        index_document(text_chunks, index_name=file_id, metadata=metadata, save_index=True)

        return UploadResponse(
            message="✅ File uploaded and indexed successfully",
            file_id=file_id,
            file_name=file.filename,
            chunk_count=len(text_chunks),
        )

    except Exception as e:
        logger.exception("[UPLOAD ERROR] Failed to upload/index document")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to upload and index file")

# === Ask Endpoint ===
@app.post("/ask", response_model=AnswerResponse, tags=["Q&A"])
async def ask_question(
    question: str = Form(...),
    file_id: str = Form(...),
    provider: str = Form("groq")
):
    try:
        answers, rationales, sources = answer_questions([question], index_name=file_id)
        return AnswerResponse(
            question=question,
            answer=answers[0],
            sources=sources[0],
            rationale=rationales[0],
            provider=provider.upper()
        )
    except Exception as e:
        logger.exception(f"[ASK ERROR] Failed to answer question: {question}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to answer question")


# === HackRx Schemas ===
class HackRxRequest(BaseModel):
    documents: str
    questions: List[str]

class HackRxResponse(BaseModel):
    answers: List[str]

# === HackRx API ===
@app.post("/api/v1/hackrx/run", response_model=HackRxResponse, tags=["HackRx"])
async def hackrx_run(
    payload: HackRxRequest,
    authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")

    token = authorization.removeprefix("Bearer ").strip()
    if token != settings.API_AUTH_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    try:
        index_name = str(uuid.uuid4())

        # Download, parse, and index
        text_chunks, metadata = download_and_parse_pdf(payload.documents)
        index_document(text_chunks, index_name=index_name, metadata=metadata, save_index=True)

        # Answer questions
        answers, _, _ = answer_questions(payload.questions, index_name=index_name)
        return HackRxResponse(answers=answers)

    except Exception as e:
        logger.exception("[HACKRX ERROR] Error processing document/questions")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error processing document and questions")
