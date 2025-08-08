from typing import List, Tuple, Dict, Any
from app.app_config import settings
from app.models.schema import SourceChunk

from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQAWithSourcesChain, RefineDocumentsChain
from langchain_core.runnables import RunnableConfig
from langchain_core.output_parsers import StrOutputParser

from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from app.retrieval.embedding_engine import load_faiss_index


# === LLM Loader ===
def get_llm():
    if settings.provider == "groq":
        return ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL_NAME,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )
    elif settings.provider == "openai":
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL_NAME,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )
    else:
        raise ValueError(f"Unsupported provider: {settings.provider}")


# === Prompt Template ===
STANDARD_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["question", "context"],
    template="""
You are a helpful assistant. Use ONLY the following context to answer the question.
If you don't know the answer, say "I don't know".

Question: {question}

Context:
{context}

Answer with complete explanation:
""".strip()
)

REFINE_PROMPT = PromptTemplate(
    input_variables=["question", "existing_answer", "context"],
    template="""
You are refining an answer based on new context.

Existing Answer:
{existing_answer}

Additional Context:
{context}

Refine the answer if helpful. Otherwise, repeat the existing answer.
""".strip()
)


# === Primary QA for Retrieved Chunks (manual pipeline) ===
def get_answer(question: str, chunks: List[SourceChunk]) -> Tuple[str, str]:
    if not chunks:
        return "No relevant context found.", "No chunks provided."

    context = "\n\n".join(chunk.content for chunk in chunks)
    llm = get_llm()
    chain = STANDARD_PROMPT_TEMPLATE | llm | StrOutputParser()

    try:
        response = chain.invoke(
            {"question": question, "context": context},
            config=RunnableConfig(tags=["qa", settings.provider])
        )
        rationale = f"Generated using {settings.provider.upper()} with {len(chunks)} chunks."
        return response.strip(), rationale
    except Exception as e:
        return f"[Error] {str(e)}", "Chain execution failed."


# === RAG + MultiQuery Retriever + Source Trace ===
def get_answer_rag(question: str, index_name: str) -> Dict[str, Any]:
    try:
        # Load FAISS vector store with metadata
        vectorstore = load_faiss_index(index_name)
        retriever = MultiQueryRetriever.from_llm(
            retriever=vectorstore.as_retriever(search_type="similarity", k=6),
            llm=get_llm()
        )

        chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=get_llm(),
            retriever=retriever,
            chain_type="stuff",
            return_source_documents=True,
            verbose=settings.DEBUG
        )

        result = chain.invoke({"question": question})
        sources = []

        for doc in result.get("source_documents", []):
            source_info = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", None)
            sources.append(f"{source_info} (Page {page})" if page else source_info)

        return {
            "answer": result["answer"].strip(),
            "rationale": f"Multi-query RAG used with {len(sources)} retrieved chunks.",
            "sources": list(set(sources)) or ["Not available"]
        }

    except Exception as e:
        return {
            "answer": f"[RAG Error] {str(e)}",
            "rationale": "RAG execution failed.",
            "sources": []
        }


# === Refine-based RAG for longer/more nuanced answers ===
def get_answer_refine_rag(question: str, index_name: str) -> Dict[str, Any]:
    try:
        vectorstore = load_faiss_index(index_name)
        retriever = vectorstore.as_retriever(search_type="similarity", k=10)

        llm = get_llm()
        chain = RefineDocumentsChain.from_llm(
            llm=llm,
            question_prompt=STANDARD_PROMPT_TEMPLATE,
            refine_prompt=REFINE_PROMPT,
            document_variable_name="context",
            return_intermediate_steps=False
        )

        docs = retriever.get_relevant_documents(question)

        answer = chain.invoke({"question": question, "context": docs})
        sources = [
            f"{doc.metadata.get('source', 'Unknown')} (Page {doc.metadata.get('page')})"
            for doc in docs
        ]

        return {
            "answer": answer.strip(),
            "rationale": f"Refine-based RAG using {len(sources)} refined chunks.",
            "sources": list(set(sources)) or ["Not available"]
        }

    except Exception as e:
        return {
            "answer": f"[Refine Error] {str(e)}",
            "rationale": "Refine chain failed.",
            "sources": []
        }
