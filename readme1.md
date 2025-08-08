# 📄🧠 HackRx DocQA - LLM-powered Document Q&A API

An intelligent document question-answering backend using FastAPI + LangChain + Groq + FAISS, designed for HackRx 6.0. It allows users to upload insurance/legal/policy documents (PDF), ask domain-specific questions, and get structured, context-rich answers with rationale and source tracking.

---

## 🚀 Features

- 🧠 **LLM-powered**: Uses Groq-hosted models (e.g. LLaMA3 or Mixtral) for fast, accurate answers.
- 🔍 **Semantic Search**: FAISS-based retrieval over chunked document embeddings.
- 📜 **Source Tracking**: Answers are based on actual chunks from the document.
- 🔗 **LangChain Refine Chain**: Enhances answers with context aggregation.
- 🧾 **Structured JSON Responses**: Answer + rationale + source metadata.
- 🛡️ **Secure Access**: Token-based Bearer authentication.

---

## 🏁 Quickstart

### 🔧 1. Clone the Repo

```bash
git clone https://github.com/<your-username>/hackrx-docqa.git
cd hackrx-docqa
```

### 📦 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 🔐 3. Create a .env File
```env
OPENAI_API_KEY=your-openai-api-key
GROQ_API_KEY=your-groq-api-key
API_AUTH_TOKEN=your-secret-token
TEMPERATURE=0.1
MAX_TOKENS=1024
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
DEBUG=True
```

###▶️ 4. Run the Server
```bash
uvicorn main:app --reload
```
The API will be live at: http://localhost:8000

---

## 📬 API Documentation

### 🔹 /api/v1/hackrx/run (POST)
This endpoint accepts a document URL and list of questions, and returns extracted answers from the document using an LLM with retrieval-augmented generation (RAG).

###✅ Request Format
Headers (Optional if Authorization is moved to JSON body):

```pgsql
Content-Type: application/json
Authorization: Bearer <your-token>
```

#### JSON Body
```json
{
  "documents": "https://example.com/policy.pdf",
  "questions": [
    "What is the waiting period for pre-existing diseases?",
    "Does this policy cover maternity expenses?"
  ]
}
```
If using inline auth:

```json
{
  "authorization": "Bearer your-token-here",
  "documents": "https://example.com/policy.pdf",
  "questions": ["..."]
}
```

### 🔁 Response Format
```json
{
  "answers": [
    "The waiting period for pre-existing diseases is 36 months...",
    "Yes, maternity expenses are covered after 24 months of continuous coverage..."
  ]
}
```
---

## 🧠 Tech Stack
FastAPI – Web framework for API

LangChain – Prompt chaining and LLM tools

Groq – High-speed inference with Mixtral / LLaMA3

FAISS – Vector similarity search for document chunks

PyMuPDF / PyPDF2 – Document parsing

HuggingFace Embeddings – Sentence transformers

Pydantic – Request/response validation

---

## 🔒 Security
All endpoints requiring document access are protected by a Bearer token.

You can set your token in .env and validate it in requests via Authorization header.

## 🧪 Testing
Use Postman or curl to test the endpoint:

```bash
curl -X POST http://localhost:8000/api/v1/hackrx/run \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{"documents":"https://example.com/doc.pdf","questions":["What is the grace period?"]}'
```

## 📦 Deployment
To run in production:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

You can deploy on:

Render

Railway

[AWS EC2 / Lambda]

[Google Cloud Run]

[Azure App Service]

## 🤝 Contributing
Pull requests are welcome! For major changes, open an issue first to discuss what you want to add.

## 🏆 Built With ❤️ for HackRx 6.0
By Sparkers — powered by OpenAI, Groq, LangChain, and FAISS.

📜 License
This project is licensed under the MIT License. See the LICENSE file for more details.

```yaml
---

Let me know if you want me to generate this as a file (e.g. `README.md`) or include a `badge`, `demo GIF`, or link to a frontend.
```
 
