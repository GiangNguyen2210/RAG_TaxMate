import os
from typing import List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class ColabEmbedder:
    def __init__(self, base_url: Optional[str] = None, timeout: int = 120):
        self.base_url = (base_url or os.getenv("COLAB_EMBEDDING_URL", "")).rstrip("/")
        if not self.base_url:
            raise ValueError("Missing COLAB_EMBEDDING_URL in environment or base_url.")

        self.timeout = timeout

    def embed_text(self, text: str) -> List[float]:
        text = (text or "").strip()
        if not text:
            return []

        response = requests.post(
            f"{self.base_url}/embed",
            json={"texts": [text]},
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        embeddings = data.get("embeddings", [])
        return embeddings[0] if embeddings else []

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        clean_texts = [t.strip() for t in texts if t and t.strip()]
        if not clean_texts:
            return []

        response = requests.post(
            f"{self.base_url}/embed",
            json={"texts": clean_texts},
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("embeddings", [])