import re
from typing import List, Dict, Any, Optional


class LegalDocumentParser:
    def parse_articles(
        self,
        page_docs: List[Dict[str, Any]],
        document_name: str,
        document_id: str,
        document_type: str = "legal_document",
        authority_level: str = "primary",
        stop_at_appendix: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Parse phần nội dung chính của văn bản pháp luật theo Điều.

        Hỗ trợ:
        - Luật có Chương
        - Nghị định không có Chương
        - Có thể dừng trước phần Phụ lục / Biểu mẫu

        Input:
            [
              {"text": "...", "metadata": {"page": 1, "source": "..."}},
              ...
            ]

        Output:
            [
              {
                "text": "...",
                "metadata": {
                  "document_name": "...",
                  "document_id": "...",
                  "document_type": "...",
                  "chapter": "... | None",
                  "article": 1,
                  "article_title": "Điều 1. ...",
                  "page_start": 1,
                  "authority_level": "primary",
                  "section_type": "main_text"
                }
              }
            ]
        """
        full_text, article_page_map = self._merge_pages_with_article_mapping(page_docs)

        if stop_at_appendix:
            full_text = self._truncate_before_appendix(full_text)

        chapters = self._extract_chapter_positions(full_text)
        articles = self._split_articles(full_text)

        chunk_docs = []
        for article in articles:
            chapter_name = self._find_chapter_for_article(article["start_idx"], chapters)

            chunk_docs.append({
                "text": article["text"],
                "metadata": {
                    "document_name": str(document_name),
                    "document_id": str(document_id),
                    "document_type": str(document_type),
                    "chapter": str(chapter_name) if chapter_name is not None else "",
                    "article": int(article["article_number"]),
                    "article_title": str(article["article_title"]),
                    "page_start": int(article_page_map.get(article["article_number"], -1)),
                    "authority_level": str(authority_level),
                    "section_type": "main_text",
                }
            })

        return chunk_docs

    def parse_appendices(
        self,
        page_docs: List[Dict[str, Any]],
        document_name: str,
        document_id: str,
        document_type: str = "legal_document_appendix",
        authority_level: str = "primary",
    ) -> List[Dict[str, Any]]:
        """
        Parse phần phụ lục / biểu mẫu / danh sách biểu mẫu.

        Đây là parser đơn giản theo block bắt đầu bằng:
        - Phụ lục
        - Danh sách các biểu mẫu
        - Mẫu số

        Dùng cho các trang cuối của nghị định có form/table.
        """
        full_text, _ = self._merge_pages_with_article_mapping(page_docs)

        appendix_start = self._find_appendix_start(full_text)
        if appendix_start is None:
            return []

        appendix_text = full_text[appendix_start:].strip()
        appendix_blocks = self._split_appendix_blocks(appendix_text)

        results = []
        for idx, block in enumerate(appendix_blocks, start=1):
            title = self._extract_appendix_title(block)

            results.append({
                "text": block,
                "metadata": {
                    "document_name": document_name,
                    "document_id": document_id,
                    "document_type": document_type,
                    "appendix_index": idx,
                    "appendix_title": title,
                    "authority_level": authority_level,
                    "section_type": "appendix",
                }
            })

        return results

    def _merge_pages_with_article_mapping(self, page_docs):
        full_parts = []
        article_page_map = {}

        for doc in page_docs:
            text = self._clean_text(doc.get("text", ""))
            page = doc.get("metadata", {}).get("page")

            found_articles = re.findall(r"Điều\s+(\d+)\.", text)
            for num in found_articles:
                num_int = int(num)
                if num_int not in article_page_map:
                    article_page_map[num_int] = page

            full_parts.append(text)

        full_text = "\n\n".join(part for part in full_parts if part.strip())
        return full_text, article_page_map

    def _clean_text(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"\s+([,.;:])", r"\1", text)
        return text.strip()

    def _extract_chapter_positions(self, full_text: str):
        """
        Chương là optional.
        Nếu có thì map vào article.
        Nếu không có thì chapter = None.
        """
        patterns = [
            r"(Chương\s+[IVXLC]+\s*\n+[A-ZÀ-Ỹ0-9 ,\-/()]+)",
            r"(Chương\s+[IVXLC]+\s+[A-ZÀ-Ỹ0-9 ,\-/()]+)",
        ]

        chapters = []
        for pattern in patterns:
            for match in re.finditer(pattern, full_text):
                raw = match.group(1).strip()
                normalized = re.sub(r"\s*\n+\s*", " - ", raw)
                chapters.append({
                    "name": normalized,
                    "start_idx": match.start()
                })

        # deduplicate theo start_idx
        seen = set()
        unique_chapters = []
        for c in sorted(chapters, key=lambda x: x["start_idx"]):
            if c["start_idx"] not in seen:
                seen.add(c["start_idx"])
                unique_chapters.append(c)

        return unique_chapters

    def _split_articles(self, full_text: str):
        """
        Tách theo Điều.

        Pattern này đủ linh hoạt cho:
        - Điều 1. Phạm vi điều chỉnh
        - Điều 1. Sửa đổi, bổ sung...
        """
        pattern = r"(Đi.{0,2}u\s+(\d+)\.\s*([^\n]+))"
        matches = list(re.finditer(pattern, full_text))

        articles = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)

            full_article_text = full_text[start:end].strip()
            article_number = int(match.group(2))
            article_title = f"Điều {article_number}. {match.group(3).strip()}"

            articles.append({
                "article_number": article_number,
                "article_title": article_title,
                "text": full_article_text,
                "start_idx": start
            })

        return articles

    def _find_chapter_for_article(self, article_start_idx, chapters) -> Optional[str]:
        current_chapter = None
        for chapter in chapters:
            if chapter["start_idx"] <= article_start_idx:
                current_chapter = chapter["name"]
            else:
                break
        return current_chapter

    def _find_appendix_start(self, full_text: str) -> Optional[int]:
        """
        Tìm điểm bắt đầu phụ lục / mẫu biểu.
        """
        appendix_patterns = [
            r"\nPhụ lục\b",
            r"\nDANH SÁCH CÁC BIỂU MẪU\b",
            r"\nDanh sách các biểu mẫu\b",
            r"\nMẫu số\s+\d+",
        ]

        positions = []
        for pattern in appendix_patterns:
            m = re.search(pattern, full_text, flags=re.IGNORECASE)
            if m:
                positions.append(m.start())

        return min(positions) if positions else None

    def _truncate_before_appendix(self, full_text: str) -> str:
        appendix_start = self._find_appendix_start(full_text)
        if appendix_start is None:
            return full_text
        return full_text[:appendix_start].strip()

    def _split_appendix_blocks(self, appendix_text: str) -> List[str]:
        """
        Tách phụ lục thành các block theo:
        - Phụ lục
        - Mẫu số ...
        - Danh sách các biểu mẫu ...
        """
        pattern = r"(?=(Phụ lục\b|Mẫu số[: ]|DANH SÁCH CÁC BIỂU MẪU\b|Danh sách các biểu mẫu\b))"
        parts = re.split(pattern, appendix_text, flags=re.IGNORECASE)

        blocks = []
        current = ""

        for part in parts:
            part = part.strip()
            if not part:
                continue

            if re.match(r"^(Phụ lục\b|Mẫu số[: ]|DANH SÁCH CÁC BIỂU MẪU\b|Danh sách các biểu mẫu\b)", part, flags=re.IGNORECASE):
                if current:
                    blocks.append(current.strip())
                current = part
            else:
                current += "\n" + part

        if current.strip():
            blocks.append(current.strip())

        return blocks

    def _extract_appendix_title(self, block_text: str) -> str:
        lines = [line.strip() for line in block_text.splitlines() if line.strip()]
        if not lines:
            return "Appendix"
        return lines[0][:200]