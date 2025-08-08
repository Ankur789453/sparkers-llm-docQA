from pydantic import BaseModel, Field
from typing import List, Optional


# === Metadata Schema ===
class ChunkMetadata(BaseModel):
    source: Optional[str] = Field(None, description="File name or origin of the chunk")
    page: Optional[int] = Field(None, description="Page number in the original document")
    chunk_index: Optional[int] = Field(None, description="Index of the chunk")
    word_count: Optional[int] = Field(None, description="Number of words in the chunk")


# === Retrieved Document Chunk ===
class SourceChunk(BaseModel):
    content: str = Field(..., description="Exact chunk text used in answering")
    metadata: Optional[ChunkMetadata] = Field(
        default=None,
        description="Metadata such as file source, page number, or chunk index"
    )


# === Detailed Answer Response ===
class AnswerResponse(BaseModel):
    question: str
    answer: str
    rationale: Optional[str] = Field(
        default=None,
        description="LLM's reasoning for the answer based on retrieved context"
    )
    provider: Optional[str] = Field(
        default="groq",
        description="LLM provider used (e.g., groq, openai)"
    )
    model_name: Optional[str] = Field(
        default=None,
        description="Specific LLM model used for this response (e.g., llama3-70b-8192)"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        description="Optional: confidence score or log probability from LLM, if available"
    )
    sources: List[SourceChunk] = Field(
        default_factory=list,
        description="Chunks of document content used to generate the answer"
    )


# === Upload Response ===
class UploadResponse(BaseModel):
    file_name: str
    chunk_count: int
    message: str
    file_id: str
