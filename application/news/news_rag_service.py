import os
from typing import Any, Dict, List
from datetime import datetime

from application.news.news_retriever import NewsRetriever


class NewsRagService:
    def __init__(self) -> None:
        self.retriever = NewsRetriever()

        self.top_k = int(
            os.getenv("NEWS_RAG_TOP_K", "4")
        )

        self.dense_k = int(
            os.getenv("NEWS_RAG_DENSE_K", "20")
        )

        self.max_context_chars = int(
            os.getenv("NEWS_RAG_MAX_CONTEXT_CHARS", "9000")
        )

        self.max_source_chars = int(
            os.getenv("NEWS_RAG_MAX_SOURCE_CHARS", "2800")
        )

    def retrieve(
        self,
        question: str,
    ) -> List[Dict[str, Any]]:
        question = question.strip()

        if not question:
            return []

        results = self.retriever.search(
            query=question,
            top_k=self.top_k,
            dense_k=self.dense_k,
        )

        min_score = float(
            os.getenv("NEWS_RAG_MIN_FINAL_SCORE", "12")
        )

        return [
            item
            for item in results
            if float(item.get("final_score") or 0) >= min_score
        ]

    def build_context(
        self,
        results: List[Dict[str, Any]],
    ) -> str:
        """
        Chuyển kết quả retrieval thành context cho LLM.

        Mỗi nguồn giữ:
        - số thứ tự citation
        - tiêu đề
        - nguồn
        - ngày đăng
        - URL
        - chủ đề
        - văn bản pháp luật được nhắc đến
        - nội dung chunk
        """
        context_blocks: List[str] = []
        current_chars = 0

        for index, item in enumerate(results, start=1):
            metadata = item.get("metadata", {})
            text = (item.get("text") or "").strip()

            if not text:
                continue

            legal_refs = self.retriever.parse_legal_references(
                metadata
            )

            if len(text) > self.max_source_chars:
                text = text[:self.max_source_chars].rsplit(" ", 1)[0].strip()
                text += "\n[Đã rút gọn nội dung nguồn]"

            block = self._format_context_block(
                index=index,
                metadata=metadata,
                text=text,
                legal_refs=legal_refs,
            )

            if current_chars + len(block) > self.max_context_chars:
                break

            context_blocks.append(block)
            current_chars += len(block)

        return "\n\n".join(context_blocks)

    def build_prompt(
        self,
        question: str,
        context: str,
    ) -> str:
        """
        Prompt riêng cho News RAG.

        News chỉ dùng để cung cấp thông tin cập nhật.
        Không được xem tin tức như căn cứ pháp lý cuối cùng.
        """
        return f"""
Bạn là trợ lý cập nhật tin tức thuế của TaxMate, chuyên hỗ trợ hộ kinh doanh và cá nhân kinh doanh tại Việt Nam.

YÊU CẦU:
1. Chỉ trả lời dựa trên phần NGUỒN TIN được cung cấp.
2. Không tự suy đoán hoặc bổ sung dữ kiện không xuất hiện trong nguồn.
3. Nếu nguồn chỉ là dự thảo, lấy ý kiến hoặc đề xuất, phải nói rõ đây chưa phải quy định chính thức.
4. Nếu nội dung liên quan nghĩa vụ pháp lý, phải nói rõ người dùng nên đối chiếu văn bản pháp luật gốc.
5. Khi sử dụng thông tin từ nguồn nào, trích dẫn theo dạng [Nguồn 1], [Nguồn 2].
6. Không coi bài báo hoặc tin tức là căn cứ pháp lý cuối cùng.
7. Ưu tiên trả lời ngắn gọn, rõ ràng, thực tế cho hộ kinh doanh.
8. Nếu nguồn không đủ để trả lời, hãy nói rõ chưa có đủ thông tin.

CÂU HỎI:
{question}

NGUỒN TIN:
{context}

Hãy trả lời bằng tiếng Việt.
""".strip()

    def build_sources(
        self,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Tạo danh sách nguồn trả về cho API/frontend.
        """
        sources = []

        for index, item in enumerate(results, start=1):
            metadata = item.get("metadata", {})

            sources.append({
                "citation": f"Nguồn {index}",
                "title": metadata.get(
                    "article_title",
                    "",
                ),
                "source_name": metadata.get(
                    "source_name",
                    "",
                ),
                "url": metadata.get(
                    "url",
                    "",
                ),
                "published_at": metadata.get(
                    "published_at",
                    "",
                ),
                "topic": metadata.get(
                    "topic",
                    "",
                ),
                "legal_references": (
                    self.retriever
                    .parse_legal_references(
                        metadata
                    )
                ),
                "distance": item.get(
                    "distance"
                ),
                "final_score": item.get(
                    "final_score"
                ),
                "published_at": self._format_published_at(
                    metadata.get("published_at")
                ),
            })

        return sources

    def prepare(
        self,
        question: str,
    ) -> Dict[str, Any]:
        """
        Chạy retrieval và chuẩn bị dữ liệu cho bước gọi LLM.
        """
        results = self.retrieve(question)
        context = self.build_context(results)
        prompt = self.build_prompt(
            question=question,
            context=context,
        )
        sources = self.build_sources(results)

        return {
            "question": question,
            "results": results,
            "context": context,
            "prompt": prompt,
            "sources": sources,
        }

    @staticmethod
    def _format_context_block(
        index: int,
        metadata: Dict[str, Any],
        text: str,
        legal_refs: List[str],
    ) -> str:
        title = metadata.get(
            "article_title",
            "Không xác định",
        )
        source_name = metadata.get(
            "source_name",
            "Không xác định",
        )
        published_at = metadata.get(
            "published_at",
            "",
        )
        url = metadata.get("url", "")
        topic = metadata.get("topic", "")
        legal_refs_text = (
            "; ".join(legal_refs)
            if legal_refs
            else "Không có"
        )

        published_at = NewsRagService._format_published_at(
            metadata.get("published_at")
        )

        return (
            f"[Nguồn {index}]\n"
            f"Tiêu đề: {title}\n"
            f"Nguồn: {source_name}\n"
            f"Ngày đăng: {published_at}\n"
            f"Chủ đề: {topic}\n"
            f"Văn bản được nhắc đến: "
            f"{legal_refs_text}\n"
            f"URL: {url}\n"
            f"Nội dung:\n{text}\n"
        )
    
    @staticmethod
    def _format_published_at(value: Any) -> str:
        if not value:
            return "Chưa xác định"

        try:
            parsed = datetime.fromisoformat(str(value))
            return parsed.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            return str(value)