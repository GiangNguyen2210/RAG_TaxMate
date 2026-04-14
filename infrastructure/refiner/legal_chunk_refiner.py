import re
from typing import List, Dict, Any


class LegalChunkRefiner:
    """
    Refine legal article-level chunks into smaller retrieval-friendly chunks.

    Priority:
    1. Keep article if short enough
    2. Split by numbered clauses: 1., 2., 3.
    3. If clause still too large, split by letter points: a), b), c)
    4. If still too large, split by smart size boundary (not raw char cut)
    """

    def __init__(
        self,
        max_chars: int = 2200,
        overlap_chars: int = 200,
    ):
        self.max_chars = max_chars
        self.overlap_chars = overlap_chars

    def refine_chunks(self, article_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        refined = []

        for chunk in article_chunks:
            text = self._normalize_legal_text(chunk["text"].strip())
            metadata = chunk["metadata"]

            if len(text) <= self.max_chars:
                refined.append(self._build_refined_chunk(
                    text=text,
                    metadata=metadata,
                    chunk_index=1,
                    chunk_total=1,
                    sub_unit="article_full"
                ))
                continue

            clause_chunks = self._split_by_clause(text)

            # Nếu không tách được theo khoản thì cắt thông minh theo độ dài
            if len(clause_chunks) <= 1:
                windows = self._split_by_size_smart(text)
                for i, part in enumerate(windows, start=1):
                    refined.append(self._build_refined_chunk(
                        text=part,
                        metadata=metadata,
                        chunk_index=i,
                        chunk_total=len(windows),
                        sub_unit="article_window"
                    ))
                continue

            temp_parts = []

            for clause_idx, clause_text in enumerate(clause_chunks, start=1):
                clause_text = self._normalize_legal_text(clause_text.strip())
                if not clause_text:
                    continue

                # LUÔN thử tách theo point trước
                point_chunks = self._split_by_letter_points(clause_text)

                if len(point_chunks) > 1:
                    for point_idx, point_text in enumerate(point_chunks, start=1):
                        point_text = self._normalize_legal_text(point_text.strip())
                        if not point_text:
                            continue

                        if len(point_text) <= self.max_chars:
                            temp_parts.append({
                                "text": point_text,
                                "sub_unit": f"clause_{clause_idx}_point_{point_idx}"
                            })
                        else:
                            windows = self._split_by_size_smart(point_text)
                            for win_idx, win_text in enumerate(windows, start=1):
                                temp_parts.append({
                                    "text": win_text,
                                    "sub_unit": f"clause_{clause_idx}_point_{point_idx}_window_{win_idx}"
                                })

                    continue

                # Nếu không tách được point thì mới xét giữ nguyên clause
                if len(clause_text) <= self.max_chars:
                    temp_parts.append({
                        "text": clause_text,
                        "sub_unit": f"clause_{clause_idx}"
                    })
                else:
                    windows = self._split_by_size_smart(clause_text)
                    for win_idx, win_text in enumerate(windows, start=1):
                        temp_parts.append({
                            "text": win_text,
                            "sub_unit": f"clause_{clause_idx}_window_{win_idx}"
                        })

            for i, part in enumerate(temp_parts, start=1):
                refined.append(self._build_refined_chunk(
                    text=part["text"],
                    metadata=metadata,
                    chunk_index=i,
                    chunk_total=len(temp_parts),
                    sub_unit=part["sub_unit"]
                ))

        return refined

    def _normalize_legal_text(self, text: str) -> str:
        """
        Normalize OCR/legal text to make structural splitting easier.
        """

        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Chuẩn hóa khoảng trắng
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Ép xuống dòng trước khoản 1. 2. 3. nếu OCR dính vào giữa dòng
        text = re.sub(r'(?<!\n)(\s)(\d+\.\s+)', r'\n\2', text)

        # Ép xuống dòng trước a) b) c) nếu OCR dính giữa dòng
        text = re.sub(r'(?<!\n)(\s)([a-zđ]\)\s+)', r'\n\2', text, flags=re.IGNORECASE)

        # Ép xuống dòng trước a.1) a.2) nếu OCR dính
        text = re.sub(r'(?<!\n)(\s)([a-zđ]\.\d+\)\s+)', r'\n\2', text, flags=re.IGNORECASE)

        return text.strip()

    def _split_by_clause(self, article_text: str) -> List[str]:
        """
        Split article text by numbered clauses at line starts:
        1.
        2.
        3.
        """
        article_text = article_text.strip()

        first_newline = article_text.find("\n")
        if first_newline == -1:
            return [article_text]

        article_title = article_text[:first_newline].strip()
        body = article_text[first_newline + 1:].strip()

        matches = list(
            re.finditer(
                r"(?:(?<=\n)|^)\s*(\d+)\.\s+",
                body
            )
        )
        if not matches:
            return [article_text]

        chunks = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            clause_text = body[start:end].strip()
            combined = f"{article_title}\n\n{clause_text}".strip()
            chunks.append(combined)

        return chunks

    def _split_by_letter_points(self, text: str) -> List[str]:
        """
        Split by legal points:
        a)
        b)
        c)
        only when they appear at line start.
        """
        text = text.strip()

        first_newline = text.find("\n")
        if first_newline == -1:
            return [text]

        header = text[:first_newline].strip()
        body = text[first_newline + 1:].strip()

        matches = list(
            re.finditer(
                r"(?:(?<=\n)|^)\s*([a-zđ])\)\s+",
                body,
                flags=re.IGNORECASE
            )
        )
        if not matches:
            return [text]

        chunks = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            point_text = body[start:end].strip()
            combined = f"{header}\n\n{point_text}".strip()
            chunks.append(combined)

        return chunks

    def _split_by_size_smart(self, text: str) -> List[str]:
        """
        Split by size, but cut at safer boundaries:
        1. double newline
        2. newline
        3. punctuation + space
        4. last space
        """
        text = text.strip()
        if len(text) <= self.max_chars:
            return [text]

        parts = []
        start = 0
        n = len(text)

        while start < n:
            if n - start <= self.max_chars:
                parts.append(text[start:].strip())
                break

            hard_end = start + self.max_chars
            search_start = max(start + int(self.max_chars * 0.6), start)

            window = text[search_start:hard_end]

            cut = None

            # ưu tiên cắt ở ranh giới đẹp gần cuối window
            candidates = [
                "\n\n",
                "\n",
                ". ",
                "; ",
                ": ",
                ", ",
                " "
            ]

            for sep in candidates:
                idx = window.rfind(sep)
                if idx != -1:
                    cut = search_start + idx + len(sep)
                    break

            if cut is None or cut <= start:
                cut = hard_end

            part = text[start:cut].strip()
            if part:
                parts.append(part)

            # overlap nhưng phải bắt đầu ở ranh giới từ
            new_start = max(cut - self.overlap_chars, 0)
            while new_start > 0 and new_start < n and not text[new_start].isspace():
                new_start -= 1

            if new_start <= start:
                new_start = cut

            start = new_start

        return parts

    def _build_refined_chunk(
        self,
        text: str,
        metadata: Dict[str, Any],
        chunk_index: int,
        chunk_total: int,
        sub_unit: str,
    ) -> Dict[str, Any]:
        new_metadata = dict(metadata)
        new_metadata["chunk_index"] = chunk_index
        new_metadata["chunk_total"] = chunk_total
        new_metadata["sub_unit"] = sub_unit

        return {
            "text": text.strip(),
            "metadata": new_metadata
        }