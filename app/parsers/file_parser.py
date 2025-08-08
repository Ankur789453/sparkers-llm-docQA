import os
from typing import List, Tuple
from PyPDF2 import PdfReader
from unstructured.partition.auto import partition
from docx import Document
from email import policy
from email.parser import BytesParser

from app.utils.text_splitter import split_text_into_chunks_with_metadata


def parse_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        extracted = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if not text.strip():
                print(f"[PDF] Warning: Page {i+1} has no text.")
            extracted.append(text)
        return "\n\n".join(extracted).strip()
    except Exception as e:
        print(f"[PDF ERROR] {file_path}: {e}")
        return ""


def parse_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
        return "\n".join(lines)
    except Exception as e:
        print(f"[DOCX ERROR] {file_path}: {e}")
        return ""


def parse_txt(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"[TXT ERROR] {file_path}: {e}")
        return ""


def parse_eml(file_path: str) -> str:
    try:
        with open(file_path, "rb") as f:
            msg = BytesParser(policy=policy.default).parse(f)

        parts = []
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    parts.append(part.get_content())
        else:
            parts.append(msg.get_content())

        return "\n".join(parts).strip()
    except Exception as e:
        print(f"[EML ERROR] {file_path}: {e}")
        return ""


def parse_with_unstructured(file_path: str) -> str:
    try:
        elements = partition(filename=file_path)
        return "\n".join(str(el) for el in elements if str(el).strip())
    except Exception as e:
        print(f"[UNSTRUCTURED ERROR] {file_path}: {e}")
        return ""


def parse_document(file_path: str) -> Tuple[List[str], List[dict]]:
    """
    Main entry point for parsing any supported document.

    Returns:
        Tuple[List[str], List[dict]]: Clean text chunks and metadata (chunk index, range, source).
    """
    ext = os.path.splitext(file_path)[-1].lower()
    print(f"[PARSER] File: {file_path} (ext: {ext})")

    text = ""

    if ext == ".pdf":
        text = parse_pdf(file_path)
    elif ext == ".docx":
        text = parse_docx(file_path)
    elif ext == ".txt":
        text = parse_txt(file_path)
    elif ext == ".eml":
        text = parse_eml(file_path)
    else:
        print(f"[PARSER] Unknown extension '{ext}', using fallback.")
        text = parse_with_unstructured(file_path)

    if not text.strip():
        print("[PARSER] Primary extraction failed. Trying fallback...")
        text = parse_with_unstructured(file_path)

    if not text.strip():
        raise ValueError(f"[PARSER ERROR] No extractable text from: {file_path}")

    print(f"[PARSER] Text extraction succeeded: {len(text)} characters.")

    # Use advanced splitter with metadata
    file_name = os.path.basename(file_path)
    chunks, metadata = split_text_into_chunks_with_metadata(
        text, chunk_size=500, overlap=50, source_name=file_name
    )

    return chunks, metadata
