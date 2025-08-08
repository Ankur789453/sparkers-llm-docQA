from typing import List
from openai import OpenAI
from app.app_config import settings  # ✅ this pulls OPENAI_API_KEY from .env
from app.utils.text_splitter import split_text_into_chunks_with_metadata
from app.retrieval.embedding_engine import (
    create_faiss_index,
    save_faiss_index,
    load_faiss_index,
    get_top_k_chunks,
)
from app.models.schema import SourceChunk

# === Initialize OpenAI Client ===
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# === GPT-3.5 Answer Generator ===
def gpt35_answer(question: str, context: str) -> str:
    prompt = f"""
You are an insurance policy expert.
Use the provided context to give a clear, complete, and user-friendly answer to the question.

Context:
\"\"\"
{context}
\"\"\"

Question: {question}

Please give a detailed but concise answer without unnecessary repetition.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

# === Document Indexer ===
def index_document(text: str, index_name: str = "default", save_index: bool = False) -> None:
    chunks, metadata = split_text_into_chunks_with_metadata(text, chunk_size=1000, overlap=150, source_name="filename.docx")
    index = create_faiss_index(chunks, metadata=metadata)
    if save_index:
        save_faiss_index(index, index_name)

# === Main QA Engine ===
def answer_questions(questions: List[str], index_name: str = "default"):
    index = load_faiss_index(index_name)
    answers = []
    rationales = []
    sources_all = []

    for question in questions:
        # Step 1: Retrieve top-k relevant chunks
        context_chunks = get_top_k_chunks(question, index, top_k=5)

        # Step 2: Build context string from retrieved chunks
        context = " ".join([
            chunk.content if isinstance(chunk, SourceChunk) else str(chunk)
            for chunk in context_chunks
        ])

        # Step 3: Generate answer with GPT-3.5
        gpt_answer = gpt35_answer(question, context)

        answers.append(gpt_answer)
        rationales.append(context)  # optional
        sources_all.append(context_chunks)

    return answers, rationales, sources_all
