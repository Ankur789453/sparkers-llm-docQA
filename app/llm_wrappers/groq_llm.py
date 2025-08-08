from openai import OpenAI
from app.app_config import settings
from typing import List, Dict, Union
import time
import logging

logger = logging.getLogger(__name__)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=settings.GROQ_API_KEY,
)

DEFAULT_MODEL = "llama3-70b-8192"
DEFAULT_SYSTEM_PROMPT = (
    "You are an intelligent document assistant. "
    "Answer questions based strictly on the provided document context. "
    "If the answer is not found in the context, say 'I don't know.'"
)
DEFAULT_TEMPERATURE = 0.2


def retry_call(func, max_retries=3, delay=1.5):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i < max_retries - 1:
                logger.warning(f"[Retry {i+1}] LLM error: {e}")
                time.sleep(delay)
            else:
                raise


def generate_answer(
    prompt: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = settings.MAX_TOKENS
) -> str:
    def call():
        start = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        duration = time.time() - start
        logger.info(
            f"[LLM Success] Model={model} Tokens={response.usage.total_tokens} Time={duration:.2f}s"
        )
        return response.choices[0].message.content.strip()

    try:
        return retry_call(call)
    except Exception as e:
        logger.error(f"[LLM Error] {e}")
        return f"[LLM Error] {str(e)}"
