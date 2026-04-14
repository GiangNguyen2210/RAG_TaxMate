import os
import time
from typing import List, Optional
from google import genai
from dotenv import load_dotenv

load_dotenv()


class GeminiEmbedder:
    def __init__(self, model: Optional[str] = None):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment.")

        self.model = model or os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
        self.client = genai.Client(api_key=self.api_key)

    def embed_text(self, text: str) -> List[float]:
        text = (text or "").strip()
        if not text:
            return []

        response = self.client.models.embed_content(
            model=self.model,
            contents=text,
        )
        return list(response.embeddings[0].values)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        batch_size = 10
        sleep_seconds = 3

        clean_texts = [t.strip() for t in texts if t and t.strip()]
        all_embeddings: List[List[float]] = []

        for i in range(0, len(clean_texts), batch_size):
            batch = clean_texts[i:i + batch_size]

            response = self.client.models.embed_content(
                model=self.model,
                contents=batch,
            )

            embeddings = [list(e.values) for e in response.embeddings]
            all_embeddings.extend(embeddings)

            # nghỉ giữa các batch để tránh 429
            if i + batch_size < len(clean_texts):
                time.sleep(sleep_seconds)

        return all_embeddings