# import os
# import uuid
# from typing import List, Dict, Any, Optional
# import chromadb
# from chromadb.config import Settings
# from dotenv import load_dotenv

# load_dotenv()


# class ChromaStore:
#     def __init__(
#         self,
#         collection_name: Optional[str] = None,
#         persist_directory: Optional[str] = None,
#     ):
#         self.collection_name = collection_name or os.getenv("CHROMA_COLLECTION", "rag_docs")
#         self.persist_directory = persist_directory or os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

#         self.client = chromadb.PersistentClient(
#             path=self.persist_directory,
#             settings=Settings(anonymized_telemetry=False)
#         )

#         self.collection = self.client.get_or_create_collection(name=self.collection_name)

#     def add_documents(
#         self,
#         documents: List[Dict[str, Any]],
#         embeddings: List[List[float]],
#         ids: Optional[List[str]] = None,
#     ) -> None:
#         if not documents:
#             return

#         ids = ids or [str(uuid.uuid4()) for _ in documents]
#         texts = [doc["text"] for doc in documents]
#         metadatas = [doc.get("metadata", {}) for doc in documents]

#         self.collection.add(
#             ids=ids,
#             documents=texts,
#             metadatas=metadatas,
#             embeddings=embeddings,
#         )

#     def similarity_search_by_vector(self, query_embedding: List[float], k: int = 4) -> List[Dict[str, Any]]:
#         results = self.collection.query(
#             query_embeddings=[query_embedding],
#             n_results=k,
#         )

#         docs = results.get("documents", [[]])[0]
#         metas = results.get("metadatas", [[]])[0]
#         distances = results.get("distances", [[]])[0]
#         ids = results.get("ids", [[]])[0]

#         output = []
#         for doc_id, doc_text, meta, distance in zip(ids, docs, metas, distances):
#             output.append(
#                 {
#                     "id": doc_id,
#                     "text": doc_text,
#                     "metadata": meta,
#                     "distance": distance,
#                 }
#             )

#         return output

#     def count(self) -> int:
#         return self.collection.count()

from typing import Any, Dict, List, Optional
import os
import chromadb
import uuid

class ChromaStore:
    def __init__(
        self,
        path: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        self.path = path or os.getenv("CHROMA_DB_PATH", "./chroma_db")
        self.collection_name = collection_name or os.getenv("CHROMA_COLLECTION_NAME", "rag_docs")

        self.client = chromadb.PersistentClient(path=self.path)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def similarity_search_by_vector(
        self,
        query_embedding: List[float],
        k: int = 10,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where,
            where_document=where_document,
            include=["documents", "metadatas", "distances"],
        )
        return self._map_query_result(result)

    def get_by_metadata(
        self,
        where: Dict[str, Any],
        limit: int = 10,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        result = self.collection.get(
            where=where,
            limit=limit,
            offset=offset,
            include=["documents", "metadatas"],
        )
        return self._map_get_result(result)

    def get_by_document_filter(
        self,
        where_document: Dict[str, Any],
        limit: int = 10,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        result = self.collection.get(
            where_document=where_document,
            limit=limit,
            offset=offset,
            include=["documents", "metadatas"],
        )
        return self._map_get_result(result)

    def get_all_documents(
        self,
        batch_size: int = 500,
    ) -> List[Dict[str, Any]]:
        all_docs: List[Dict[str, Any]] = []
        offset = 0

        while True:
            result = self.collection.get(
                limit=batch_size,
                offset=offset,
                include=["documents", "metadatas"],
            )

            ids = result.get("ids", [])
            if not ids:
                break

            mapped = self._map_get_result(result)
            all_docs.extend(mapped)

            if len(ids) < batch_size:
                break

            offset += batch_size

        return all_docs

    def _map_query_result(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        dists = result.get("distances", [[]])[0]
        ids = result.get("ids", [[]])[0]

        output = []
        for i in range(len(docs)):
            output.append({
                "id": ids[i] if i < len(ids) else None,
                "text": docs[i],
                "metadata": metas[i] if i < len(metas) else {},
                "distance": dists[i] if i < len(dists) else None,
                "retrieval_source": "dense",
            })
        return output

    def _map_get_result(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        docs = result.get("documents", [])
        metas = result.get("metadatas", [])
        ids = result.get("ids", [])

        output = []
        for i in range(len(docs)):
            output.append({
                "id": ids[i] if i < len(ids) else None,
                "text": docs[i],
                "metadata": metas[i] if i < len(metas) else {},
                "distance": None,
                "retrieval_source": "filter",
            })
        return output
    
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