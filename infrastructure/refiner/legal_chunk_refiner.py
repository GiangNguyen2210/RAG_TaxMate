import re
from typing import List, Dict, Any, Optional, Tuple


class LegalChunkRefiner:
    """
    Refine article-level legal chunks into smaller retrieval-friendly chunks.

    Metadata output dùng tiếng Việt:
    - khoan
    - diem
    - chi_so_chunk
    - tong_so_chunk
    - don_vi_con

    Strategy:
    1. Keep article if short enough.
    2. Split by numbered clauses: 1., 2., 3.
    3. If clause is too large, split by letter points: a), b), c).
    4. If still too large, split by smart size boundary.
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
                    chi_so_chunk=1,
                    tong_so_chunk=1,
                    don_vi_con="toàn_bộ_điều",
                    khoan=None,
                    diem=None,
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
                        chi_so_chunk=i,
                        tong_so_chunk=len(windows),
                        don_vi_con="cửa_sổ_điều",
                        khoan=None,
                        diem=None,
                    ))
                continue

            temp_parts = []

            for clause_num, clause_text in clause_chunks:
                clause_text = self._normalize_legal_text(clause_text.strip())
                if not clause_text:
                    continue

                # Luôn thử tách theo điểm trước
                point_chunks = self._split_by_letter_points(clause_text)

                if len(point_chunks) > 1:
                    for point_label, point_text in point_chunks:
                        point_text = self._normalize_legal_text(point_text.strip())
                        if not point_text:
                            continue

                        if len(point_text) <= self.max_chars:
                            temp_parts.append({
                                "text": point_text,
                                "don_vi_con": f"khoản_{clause_num}_điểm_{point_label}" if point_label else f"khoản_{clause_num}",
                                "khoan": clause_num,
                                "diem": point_label or None,
                            })
                        else:
                            windows = self._split_by_size_smart(point_text)
                            for win_idx, win_text in enumerate(windows, start=1):
                                temp_parts.append({
                                    "text": win_text,
                                    "don_vi_con": f"khoản_{clause_num}_điểm_{point_label}_cửa_sổ_{win_idx}" if point_label else f"khoản_{clause_num}_cửa_sổ_{win_idx}",
                                    "khoan": clause_num,
                                    "diem": point_label or None,
                                })
                    continue

                # Nếu không có điểm thì giữ nguyên khoản nếu đủ ngắn
                if len(clause_text) <= self.max_chars:
                    temp_parts.append({
                        "text": clause_text,
                        "don_vi_con": f"khoản_{clause_num}",
                        "khoan": clause_num,
                        "diem": None,
                    })
                else:
                    windows = self._split_by_size_smart(clause_text)
                    for win_idx, win_text in enumerate(windows, start=1):
                        temp_parts.append({
                            "text": win_text,
                            "don_vi_con": f"khoản_{clause_num}_cửa_sổ_{win_idx}",
                            "khoan": clause_num,
                            "diem": None,
                        })

            for i, part in enumerate(temp_parts, start=1):
                refined.append(self._build_refined_chunk(
                    text=part["text"],
                    metadata=metadata,
                    chi_so_chunk=i,
                    tong_so_chunk=len(temp_parts),
                    don_vi_con=part["don_vi_con"],
                    khoan=part["khoan"],
                    diem=part["diem"],
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

        # Sửa một vài lỗi OCR phổ biến
        text = re.sub(r"\bĐ\s*i\s*ề\s*u\b", "Điều", text, flags=re.IGNORECASE)

        # Ép xuống dòng trước khoản 1. 2. 3. nếu OCR dính vào giữa dòng
        text = re.sub(r'(?<!\n)(\s)(\d+\.\s+)', r'\n\2', text)

        # Ép xuống dòng trước a) b) c) nếu OCR dính giữa dòng
        text = re.sub(r'(?<!\n)(\s)([a-zđ]\)\s+)', r'\n\2', text, flags=re.IGNORECASE)

        # Ép xuống dòng trước a.1) a.2) nếu OCR dính
        text = re.sub(r'(?<!\n)(\s)([a-zđ]\.\d+\)\s+)', r'\n\2', text, flags=re.IGNORECASE)

        return text.strip()

    def _split_by_clause(self, article_text: str) -> List[Tuple[int, str]]:
        """
        Split article text by numbered clauses at line starts:
        1.
        2.
        3.
        """
        article_text = article_text.strip()

        first_newline = article_text.find("\n")
        if first_newline == -1:
            return []

        article_title = article_text[:first_newline].strip()
        body = article_text[first_newline + 1:].strip()

        matches = list(
            re.finditer(
                r"(?:(?<=\n)|^)\s*(\d+)\.\s+",
                body
            )
        )
        if not matches:
            return []

        chunks: List[Tuple[int, str]] = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            clause_num = int(match.group(1))
            clause_text = body[start:end].strip()
            combined = f"{article_title}\n\n{clause_text}".strip()
            chunks.append((clause_num, combined))

        return chunks

    def _split_by_letter_points(self, text: str) -> List[Tuple[Optional[str], str]]:
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
            return [(None, text)]

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
            return [(None, text)]

        chunks: List[Tuple[Optional[str], str]] = []

        # Phần trước điểm a), nếu có
        if body[:matches[0].start()].strip():
            chunks.append((None, f"{header}\n\n{body[:matches[0].start()].strip()}"))

        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            point_label = match.group(1).lower()
            point_text = body[start:end].strip()
            combined = f"{header}\n\n{point_text}".strip()
            chunks.append((point_label, combined))

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
        chi_so_chunk: int,
        tong_so_chunk: int,
        don_vi_con: str,
        khoan: Optional[int],
        diem: Optional[str],
    ) -> Dict[str, Any]:
        new_metadata = dict(metadata)
        new_metadata["chi_so_chunk"] = chi_so_chunk
        new_metadata["tong_so_chunk"] = tong_so_chunk
        new_metadata["don_vi_con"] = don_vi_con

        if khoan is not None:
            new_metadata["khoan"] = int(khoan)
        else:
            new_metadata["khoan"] = ""

        if diem is not None:
            new_metadata["diem"] = str(diem)
        else:
            new_metadata["diem"] = ""

        return {
            "text": text.strip(),
            "metadata": new_metadata
        }
