import re
from typing import Any


class NewsChunker:
    def __init__(
        self,
        max_chars: int = 1800,
        overlap_paragraphs: int = 1,
    ) -> None:
        self.max_chars = max_chars
        self.overlap_paragraphs = overlap_paragraphs

    def chunk_article(self, article: dict[str, Any]) -> list[dict[str, Any]]:
        title = article.get("title") or ""
        content = article.get("content") or ""

        if not content.strip():
            return []

        paragraphs = self._split_paragraphs(content)

        # Nếu dòng đầu là title thì bỏ ra khỏi paragraphs,
        # vì ta sẽ gắn title riêng vào mỗi chunk.
        if paragraphs and paragraphs[0].strip() == title.strip():
            paragraphs = paragraphs[1:]

        chunks_paragraphs = self._build_chunks(paragraphs)

        chunks = []

        for index, paragraph_group in enumerate(chunks_paragraphs):
            chunk_text = self._format_chunk_text(
                title=title,
                paragraphs=paragraph_group,
            )

            chunk = {
                "chunk_id": f"{article.get('content_hash')}_{index}",
                "article_title": title,
                "source_name": article.get("source_name"),
                "url": article.get("url"),
                "published_at": article.get("published_at"),
                "crawled_at": article.get("crawled_at"),
                "article_crawled_at": article.get("article_crawled_at"),
                "topic": article.get("topic"),
                "relevance_score": article.get("relevance_score"),
                "legal_references": article.get("legal_references", []),
                "content_hash": article.get("content_hash"),
                "chunk_index": index,
                "chunk_text": chunk_text,
            }

            chunks.append(chunk)

        return chunks

    def _split_paragraphs(self, content: str) -> list[str]:
        lines = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")

        paragraphs = []

        for line in lines:
            line = re.sub(r"\s+", " ", line).strip()

            if not line:
                continue

            paragraphs.append(line)

        return paragraphs

    def _build_chunks(self, paragraphs: list[str]) -> list[list[str]]:
        chunks: list[list[str]] = []
        current: list[str] = []

        for paragraph in paragraphs:
            candidate = current + [paragraph]
            candidate_text = "\n".join(candidate)

            if len(candidate_text) <= self.max_chars:
                current = candidate
                continue

            if current:
                chunks.append(current)

            # Overlap theo paragraph, không cắt giữa chữ.
            overlap = current[-self.overlap_paragraphs :] if current else []
            current = overlap + [paragraph]

        if current:
            chunks.append(current)

        return chunks

    def _format_chunk_text(self, title: str, paragraphs: list[str]) -> str:
        body = "\n".join(paragraphs).strip()

        if not title:
            return body

        return f"{title}\n{body}".strip()