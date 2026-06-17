import os
import json
from typing import Any, Dict, List

from infrastructure.embeddings.collab_embedder import ColabEmbedder
from infrastructure.vectorstores.chroma_store import ChromaStore


class NewsRetriever:
    TOPIC_KEYWORDS = {
        "e_invoice": [
            "hóa đơn điện tử",
            "máy tính tiền",
            "khởi tạo từ máy tính tiền",
            "sinh trắc học",
            "etax mobile",
        ],
        "household_business_tax": [
            "hộ kinh doanh",
            "cá nhân kinh doanh",
            "thuế khoán",
            "bỏ thuế khoán",
            "kê khai",
            "nộp thuế điện tử",
            "doanh thu",
        ],
        "ecommerce_tax": [
            "thương mại điện tử",
            "sàn thương mại điện tử",
            "gian lận thuế",
            "trục lợi thuế",
            "hoàn thuế",
            "dòng tiền",
        ],
    }

    def __init__(self) -> None:
        self.embedder = ColabEmbedder()
        self.store = ChromaStore(
            collection_name=os.getenv("CHROMA_NEWS_COLLECTION", "taxmate_news")
        )

    def search(
        self,
        query: str,
        top_k: int = 4,
        dense_k: int = 12,
    ) -> List[Dict[str, Any]]:
        query_embedding = self.embedder.embed_texts([query])[0]

        results = self.store.similarity_search_by_vector(
            query_embedding=query_embedding,
            k=dense_k,
        )

        reranked = []

        for item in results:
            score = self._score_item(query, item)

            item["news_score"] = score
            item["final_score"] = score - float(item.get("distance") or 0)

            reranked.append(item)

        reranked.sort(key=lambda x: x["final_score"], reverse=True)

        deduplicated = []
        seen_articles = set()

        for item in reranked:
            metadata = item.get("metadata", {})

            article_key = (
                metadata.get("url")
                or metadata.get("article_title")
                or metadata.get("content_hash")
            )

            if not article_key:
                continue

            if article_key in seen_articles:
                continue

            seen_articles.add(article_key)
            deduplicated.append(item)

            if len(deduplicated) >= top_k:
                break

        return deduplicated

    def _score_item(self, query: str, item: Dict[str, Any]) -> float:
        query_lower = query.lower()
        text = (item.get("text") or "").lower()
        metadata = item.get("metadata", {})

        title = (metadata.get("article_title") or "").lower()
        topic = metadata.get("topic") or ""

        score = 0.0

        # 1. Exact query terms in title/text
        query_terms = self._extract_query_terms(query_lower)

        for term in query_terms:
            if term in title:
                score += 4.0
            elif term in text:
                score += 2.0

        # 2. Topic keyword boost
        for keyword in self.TOPIC_KEYWORDS.get(topic, []):
            keyword_lower = keyword.lower()

            if keyword_lower in query_lower:
                score += 2.5

            if keyword_lower in title:
                score += 2.0
            elif keyword_lower in text:
                score += 1.0

        # 3. Topic intent boost
        detected_topic = self._detect_query_topic(query_lower)

        if detected_topic and detected_topic == topic:
            score += 3.0

        # 4. Relevance score from crawler
        try:
            score += float(metadata.get("relevance_score", 0)) * 0.15
        except Exception:
            pass

        return score

    def _extract_query_terms(self, query: str) -> List[str]:
        candidates = [
            "hộ kinh doanh",
            "cá nhân kinh doanh",
            "hóa đơn điện tử",
            "máy tính tiền",
            "khởi tạo từ máy tính tiền",
            "sinh trắc học",
            "thương mại điện tử",
            "sàn thương mại điện tử",
            "gian lận thuế",
            "trục lợi thuế",
            "thuế khoán",
            "bỏ thuế khoán",
            "kê khai",
            "nộp thuế điện tử",
        ]

        return [term for term in candidates if term in query]

    def _detect_query_topic(self, query: str) -> str | None:
        if (
            "hóa đơn điện tử" in query
            or "máy tính tiền" in query
            or "sinh trắc học" in query
        ):
            return "e_invoice"

        if (
            "hộ kinh doanh" in query
            or "cá nhân kinh doanh" in query
            or "thuế khoán" in query
            or "bỏ thuế khoán" in query
        ):
            return "household_business_tax"

        if (
            "thương mại điện tử" in query
            or "sàn thương mại điện tử" in query
            or "gian lận thuế" in query
            or "trục lợi thuế" in query
        ):
            return "ecommerce_tax"

        return None

    @staticmethod
    def parse_legal_references(metadata: Dict[str, Any]) -> List[str]:
        raw = metadata.get("legal_references", "[]")

        try:
            return json.loads(raw)
        except Exception:
            return []