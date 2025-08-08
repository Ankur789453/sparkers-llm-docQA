import os
import requests
import fitz  # PyMuPDF
from app.utils.text_splitter import split_text_into_chunks_with_metadata

def download_and_parse_pdf(url: str, chunk_size: int = 500, chunk_overlap: int = 50, source_name: str = "remote.pdf"):
    """
    Downloads a PDF from the given URL, extracts text, and splits into chunks with metadata.
    Returns chunks and metadata separately.
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to download PDF, status code: {response.status_code}")

    temp_pdf_path = "temp.pdf"
    try:
        with open(temp_pdf_path, "wb") as f:
            f.write(response.content)

        doc = fitz.open(temp_pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()

        if not full_text.strip():
            raise ValueError("No text extracted from PDF")

        # ✅ Use metadata-aware splitting
        chunks, metadata = split_text_into_chunks_with_metadata(
            full_text,
            chunk_size=chunk_size,
            overlap=chunk_overlap,
            source_name=source_name
        )

        return chunks, metadata

    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
