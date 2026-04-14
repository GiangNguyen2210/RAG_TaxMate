import os
from typing import Dict, Any, List
from dotenv import load_dotenv

from infrastructure.embeddings.gemini_embedder import GeminiEmbedder
from infrastructure.embeddings.collab_embedder import ColabEmbedder
from infrastructure.vectorstores.chroma_store import ChromaStore
from infrastructure.llm.gemini_client import GeminiClient

load_dotenv()


class RAGPipeline:
    def __init__(self):
        self.embedder = ColabEmbedder()
        self.vectorstore = ChromaStore()
        self.llm = GeminiClient()

        self.top_k = int(os.getenv("RAG_TOP_K", "4"))
        self.max_context_chars = int(os.getenv("RAG_MAX_CONTEXT_CHARS", "12000"))

    def _build_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        context_parts = []
        total_chars = 0

        for item in retrieved_docs:
            source = item.get("metadata", {}).get("source", "unknown")
            page = item.get("metadata", {}).get("page", "?")
            text = item.get("text", "").strip()

            block = f"[Source: {source} | Page: {page}]\n{text}\n"
            if total_chars + len(block) > self.max_context_chars:
                break

            context_parts.append(block)
            total_chars += len(block)

        return "\n---\n".join(context_parts)

    def ask(self, question: str) -> Dict[str, Any]:
        question = (question or "").strip()
        if not question:
            raise ValueError("Question must not be empty.")

        query_embedding = self.embedder.embed_text(question)
        if not query_embedding:
            raise ValueError("Failed to generate query embedding.")

        retrieved_docs = self.vectorstore.similarity_search_by_vector(
            query_embedding=query_embedding,
            k=self.top_k,
        )

        context = self._build_context(retrieved_docs)
        answer = self.llm.generate_answer(question=question, context=context)

        return {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "source": d.get("metadata", {}).get("source"),
                    "page": d.get("metadata", {}).get("page"),
                    "chunk_index": d.get("metadata", {}).get("chunk_index"),
                    "distance": d.get("distance"),
                }
                for d in retrieved_docs
            ],
        }