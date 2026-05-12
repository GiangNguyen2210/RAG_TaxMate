# -*- coding: utf-8 -*-
"""
reranker.py — Colab API reranker for TaxMate Legal RAG.

Expected endpoint:
POST {COLAB_RERANKER_URL}/rerank
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class Reranker:
    """
    Remote Colab reranker.

    It avoids importing RetrievedChunk to prevent circular import.
    It only expects each chunk object to have:
    - id
    - text
    - metadata
    - score
    - retrieval_source
    """

    def __init__(self, base_url: Optional[str] = None, timeout: int = 180):
        self.base_url = (base_url or os.getenv("COLAB_RERANKER_URL", "")).rstrip("/")

        # Fallback if embedder and reranker are hosted on the same Colab URL.
        if not self.base_url:
            self.base_url = os.getenv("COLAB_EMBEDDING_URL", "").rstrip("/")

        if not self.base_url:
            raise ValueError("Missing COLAB_RERANKER_URL or COLAB_EMBEDDING_URL in environment.")

        self.timeout = timeout

    def rerank(self, query: str, chunks: List[Any], top_k: int) -> List[Any]:
        query = (query or "").strip()

        if not query or not chunks:
            return []

        top_k = min(top_k, len(chunks))

        payload = {
            "query": query,
            "top_k": top_k,
            "chunks": [
                {
                    "id": str(getattr(chunk, "id", "") or ""),
                    "text": self._chunk_text_for_rerank(chunk),
                    "metadata": getattr(chunk, "metadata", {}) or {},
                }
                for chunk in chunks
            ],
        }

        response = requests.post(
            f"{self.base_url}/rerank",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        if not results:
            return []

        chunk_by_id: Dict[str, Any] = {
            str(getattr(chunk, "id", "")): chunk
            for chunk in chunks
        }

        chunk_by_chunk_id: Dict[str, Any] = {}
        for chunk in chunks:
            metadata = getattr(chunk, "metadata", {}) or {}
            chunk_id = metadata.get("chunk_id")
            if chunk_id:
                chunk_by_chunk_id[str(chunk_id)] = chunk

        output: List[Any] = []

        for item in results:
            item_id = str(item.get("id", "") or "")
            item_metadata = item.get("metadata", {}) or {}
            item_chunk_id = str(item_metadata.get("chunk_id", "") or "")

            chunk = None

            if item_id and item_id in chunk_by_id:
                chunk = chunk_by_id[item_id]
            elif item_chunk_id and item_chunk_id in chunk_by_chunk_id:
                chunk = chunk_by_chunk_id[item_chunk_id]

            if chunk is None:
                continue

            chunk.score = float(item.get("score", 0.0))

            if "reranker" not in chunk.retrieval_source:
                chunk.retrieval_source = f"{chunk.retrieval_source}+reranker"

            output.append(chunk)

        return output[:top_k]

    @staticmethod
    def _chunk_text_for_rerank(chunk: Any) -> str:
        metadata = getattr(chunk, "metadata", {}) or {}

        context_parts = []

        ten_van_ban = metadata.get("ten_van_ban")
        tieu_de_dieu = metadata.get("tieu_de_dieu")
        dieu = metadata.get("dieu")
        khoan = metadata.get("khoan")
        diem = metadata.get("diem")
        don_vi_con = metadata.get("don_vi_con")

        if ten_van_ban:
            context_parts.append(f"Văn bản: {ten_van_ban}")

        if tieu_de_dieu:
            context_parts.append(str(tieu_de_dieu))
        elif dieu not in (None, ""):
            context_parts.append(f"Điều {dieu}")

        if khoan not in (None, ""):
            context_parts.append(f"Khoản {khoan}")

        if diem not in (None, ""):
            context_parts.append(f"Điểm {diem}")

        if don_vi_con:
            context_parts.append(f"Đơn vị nội dung: {don_vi_con}")

        context = "\n".join(context_parts).strip()
        text = (getattr(chunk, "text", "") or "").strip()

        if context:
            return f"{context}\n\n{text}"

        return text
