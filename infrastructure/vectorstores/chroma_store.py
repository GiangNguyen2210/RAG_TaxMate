import os
import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()


class ChromaStore:
    def __init__(
        self,
        collection_name: Optional[str] = None,
        persist_directory: Optional[str] = None,
    ):
        self.collection_name = collection_name or os.getenv("CHROMA_COLLECTION", "rag_docs")
        self.persist_directory = persist_directory or os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]],
        ids: Optional[List[str]] = None,
    ) -> None:
        if not documents:
            return

        ids = ids or [str(uuid.uuid4()) for _ in documents]
        texts = [doc["text"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]

        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def similarity_search_by_vector(self, query_embedding: List[float], k: int = 4) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        output = []
        for doc_id, doc_text, meta, distance in zip(ids, docs, metas, distances):
            output.append(
                {
                    "id": doc_id,
                    "text": doc_text,
                    "metadata": meta,
                    "distance": distance,
                }
            )

        return output

    def count(self) -> int:
        return self.collection.count()