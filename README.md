# HackRx Query-Retrieval System

This is a FastAPI-based backend to handle PDF document ingestion, semantic search, clause matching, and JSON response generation using GPT-4.

## How to Run

1. `pip install -r requirements.txt`
2. Replace `"your-openai-key"` with your OpenAI API key in `retrieval.py`
3. Run the server:
```bash
uvicorn app.main:app --reload
```

## Endpoint

POST `/api/v1/hackrx/run`

### Body:

```json
{
  "documents": "<PDF_URL>",
  "questions": [
    "What is the grace period for premium payment?",
    ...
  ]
}
```