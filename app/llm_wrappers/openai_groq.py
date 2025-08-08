# app/llm_wrappers/openai_groq.py
import os
from app.app_config import settings
from openai import OpenAI
from groq import Groq

OPENAI_API_KEY = settings.OPENAI_API_KEY
GROQ_API_KEY = settings.GROQ_API_KEY

# Clients
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def get_llm_response(prompt: str, provider: str = "groq", model: str = None, temperature: float = 0.1, max_tokens: int = 512) -> str:
    """
    Get a text completion from Groq or OpenAI based on the provider.
    """
    provider = provider.lower()

    if provider == "groq":
        if not groq_client:
            raise ValueError("GROQ_API_KEY not found in environment.")
        model = model or settings.GROQ_MODEL_NAME
        print(f"Using GROQ model: {model}")  # ← ADD THIS LINE
        try:
            response = groq_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error generating answer: {str(e)}]"

    elif provider == "openai":
        if not openai_client:
            raise ValueError("OPENAI_API_KEY not found in environment.")
        model = model or "gpt-3.5-turbo"
        response = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()

    else:
        raise ValueError(f"Unknown provider: {provider}")
