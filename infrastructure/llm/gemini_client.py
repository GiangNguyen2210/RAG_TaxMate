import os
from typing import Optional
from google import genai
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    def __init__(self, model: Optional[str] = None):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment.")

        self.model = model or os.getenv("GEMINI_LLM_MODEL", "gemini-2.5-flash")
        self.client = genai.Client(api_key=self.api_key)

    def generate_answer(self, question: str, context: str) -> str:
        prompt = f"""
You are a helpful RAG assistant.
Answer ONLY based on the provided context.
If the context is insufficient, clearly say you don't have enough information.

Question:
{question}

Context:
{context}

Answer:
""".strip()

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return (response.text or "").strip()