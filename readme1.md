# 📄 HackRx 6.0 — LLM-powered Query-Retrieval System



A modern FastAPI backend that allows users to:

- Upload documents (PDF/DOCX)
- Ask complex domain-specific questions (e.g., Insurance/Legal)
- Get accurate answers powered by **semantic search**, **FAISS**, and **LLMs** like GPT & Mixtral

---

## 🚀 Features

✅ Upload & parse documents (PDF/DOCX)\
✅ Semantic chunk-based retrieval via FAISS\
✅ Clause-aware QA with rationale and sources\
✅ Switch between OpenAI and Groq (Mixtral) backends\
✅ Public `/hackrx/run` endpoint for HackRx integration

---

## 🛠️ Project Structure

```
Hackrx_6.0-main/
│
├── .env                      # API keys and configuration
├── payload.json              # Sample payload for testing
├── requirements.txt          # Project dependencies
├── test_request.py           # Script to test HackRx endpoint
│
├── app/
│   ├── main.py               # FastAPI app with endpoints
│   ├── app_config.py         # Environment variables (pydantic)
│
│   ├── parsers/
│   │   └── file_parser.py    # Local DOCX/PDF parsing
│
│   ├── retrieval/
│   │   ├── search_engine.py  # Semantic search logic
│   │   └── embedding_engine.py  # FAISS vector indexing
│
│   ├── llm_wrappers/
│   │   ├── qa_engine.py      # Uses Groq/OpenAI for answering
│   │   └── llm_engine.py     # Model handler (extensible)
│
│   ├── models/
│   │   └── schema.py         # Request/response models
│
│   └── utils/
│       ├── text_splitter.py      # Chunking logic
│       └── download_and_parse.py # Remote PDF downloader
```

---

## 🔧 Setup & Installation

```bash
# 1. Create virtualenv (optional)
conda create -n hackrx python=3.10 -y
conda activate hackrx

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API keys to `.env`
```

### .env Example:

```env
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk-...
GROQ_MODEL_NAME=llama3-70b-8192
OPENAI_MODEL_NAME=gpt-3.5-turbo
TEMPERATURE=0.1
MAX_TOKENS=1024
CHUNK_SIZE=500
CHUNK_OVERLAP=50
API_AUTH_TOKEN=Bearer your_api_token_here
```

---

## ⚙️ Run the Backend

```bash
uvicorn app.main:app --reload
```

---

## 📤 Upload Endpoint

```
POST /upload
```

> Uploads a document and indexes it using FAISS.

### Response:

```json
{
  "message": "✅ File uploaded and indexed successfully",
  "file_id": "abc-123-uuid",
  "file_name": "policy.pdf",
  "chunk_count": 21
}
```

---

## ❓ Ask Endpoint

```
POST /ask
```

> Ask a single question based on previously uploaded document.

**Form Data:**

- `question`: Your query
- `file_id`: ID returned during upload
- `provider`: `groq` or `openai` (default: `groq`)

---

## 🔥 HackRx Public API

```
POST /hackrx/run
```

> Directly hit the LLM-powered query system with a PDF URL + multiple questions.

### Payload:

```json
{
  "documents": "https://example.com/policy.pdf",
  "questions": [
    "What is the waiting period for cataract?",
    "Are maternity expenses covered?"
  ]
}
```

### Response:

```json
{
  "answers": [
    "24 months",
    "Yes, up to ₹25,000 with conditions"
  ]
}
```

---

## 📦 Included Files

- `payload.json` → For testing `/hackrx/run`
- `test_request.py` → Script to simulate external HackRx call
- `README.md` → You're reading it 📝
- `Procfile` → For deployment (Heroku compatible)

---

## 🧠 Powered By

- **FAISS** for vector similarity
- **SentenceTransformers** for embeddings
- **Groq (Mixtral)** & **OpenAI (GPT-3.5)** for answering
- **FastAPI** for blazing-fast backend

---

## 🏁 Future Upgrades

-

---

## 💙 Made for HackRx 6.0 by Ankur Jangra (Billu)

> "Query Smart, Retrieve Smarter."

---

## 🌐 License

MIT License. Use freely with attribution.

---

> Need help or want to contribute? Open a PR or raise an issue 🙌

