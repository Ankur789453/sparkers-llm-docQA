from typing import List, Tuple
from app.retrieval.embedding_engine import (
    load_faiss_index,
    get_top_k_chunks,
)
from app.models.schema import SourceChunk
from app.llm_wrappers.openai_groq import get_llm_response


def refine_prompt(question: str, context: str) -> str:
    """
    Refine-style prompt designed for accurate and specific insurance-related answers.
    """
    return f"""
You are an expert insurance policy analyst.

Use the following CONTEXT from a health insurance policy to answer the QUESTION.

Instructions:
- Base your answer strictly on the provided context.
- Do not include generic disclaimers.
- If the answer is uncertain, say so clearly.
- Use bullet points if multiple points are found.
- Be concise, clear, and informative.

CONTEXT:
\"\"\"
{context}
\"\"\"

QUESTION: {question}

ANSWER:
""".strip()


def answer_questions(
    questions: List[str],
    index_name: str = "default"
) -> Tuple[List[str], List[str], List[List[SourceChunk]]]:
    """
    Answer each question using top retrieved chunks and Groq's refine-style prompt.

    Returns:
        answers: List of answers for each question (string format).
        rationales: Raw context used for generating each answer.
        sources_all: List of SourceChunks used for answering each question.
    """
    index = load_faiss_index(index_name)
    answers = []
    rationales = []
    sources_all = []

    for question in questions:
        # Retrieve top chunks relevant to the question
        context_chunks = get_top_k_chunks(question, index, top_k=5)

        # Join top K chunks into a single string context
        context = " ".join([
            chunk if isinstance(chunk, str) else chunk.content
            for chunk in context_chunks
        ])

        # Construct refine-style prompt
        prompt = refine_prompt(question, context)

        # Generate answer using Groq's LLaMA3
        try:
            refined_answer = get_llm_response(
                prompt=prompt,
                provider="groq",
                model="llama3-70b-8192",
                temperature=0.1,
                max_tokens=1024
            )
        except Exception as e:
            refined_answer = f"[Error generating answer: {str(e)}]"

        answers.append(refined_answer)
        rationales.append(context)
        sources_all.append(context_chunks)

    return answers, rationales, sources_all
