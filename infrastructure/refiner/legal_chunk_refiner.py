
import hashlib
import re
from typing import List, Dict, Any, Optional, Tuple


class LegalChunkRefiner:
    """
    Refine article-level legal chunks into hierarchical retrieval chunks.

    TaxMate v2.1:
    - Store BOTH full article chunk and smaller clause/point chunks.
    - Add chunk_id for stable dedupe/debug/citation.
    - Add level:
        1 = toàn bộ điều
        2 = khoản
        3 = điểm
    - Add lightweight context enrichment to each chunk.
    - Avoid markdown styling because it can add retrieval noise for tax/legal text.
    - Avoid dropping short legal chunks because short clauses may be legally important.

    Fixes:
    - Do NOT treat the article number in "Điều X." as "Khoản X".
    - Format clause chunks as "Khoản X. ..." instead of raw "X. ...".
    - Format point chunks as "Điểm a) ..." instead of raw "a) ...".
    """

    def __init__(
        self,
        max_chars: int = 2200,
        overlap_chars: int = 200,
        keep_full_article: bool = True,
        always_split_clauses: bool = True,
        split_points: bool = True,
        enrich_context: bool = True,
        deduplicate: bool = True,
    ):
        self.max_chars = max_chars
        self.overlap_chars = overlap_chars
        self.keep_full_article = keep_full_article
        self.always_split_clauses = always_split_clauses
        self.split_points = split_points
        self.enrich_context = enrich_context
        self.deduplicate = deduplicate

    def refine_chunks(self, article_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        refined: List[Dict[str, Any]] = []
        seen_hashes = set()

        for article_chunk in article_chunks:
            article_text = self._normalize_legal_text(article_chunk["text"].strip())
            article_metadata = article_chunk["metadata"]
            article_parts: List[Dict[str, Any]] = []

            if self.keep_full_article:
                if len(article_text) <= self.max_chars:
                    article_parts.append({
                        "text": article_text,
                        "don_vi_con": "toàn_bộ_điều",
                        "khoan": None,
                        "diem": None,
                        "level": 1,
                        "la_chunk_toan_dieu": True,
                    })
                else:
                    windows = self._split_by_size_smart(article_text)
                    for win_idx, win_text in enumerate(windows, start=1):
                        article_parts.append({
                            "text": win_text,
                            "don_vi_con": f"toàn_bộ_điều_cửa_sổ_{win_idx}",
                            "khoan": None,
                            "diem": None,
                            "level": 1,
                            "la_chunk_toan_dieu": True,
                        })

            if self.always_split_clauses:
                clause_chunks = self._split_by_clause(article_text)
            else:
                clause_chunks = self._split_by_clause(article_text) if len(article_text) > self.max_chars else []

            if clause_chunks:
                for clause_num, clause_text in clause_chunks:
                    clause_text = self._normalize_legal_text(clause_text.strip())
                    if not clause_text:
                        continue

                    point_chunks = self._split_by_letter_points(clause_text) if self.split_points else [(None, clause_text)]
                    has_points = len(point_chunks) > 1 or any(point_label for point_label, _ in point_chunks)

                    if has_points:
                        for point_label, point_text in point_chunks:
                            point_text = self._normalize_legal_text(point_text.strip())
                            if not point_text:
                                continue

                            if len(point_text) <= self.max_chars:
                                article_parts.append({
                                    "text": point_text,
                                    "don_vi_con": (
                                        f"khoản_{clause_num}_điểm_{point_label}"
                                        if point_label else f"khoản_{clause_num}_mở_đầu"
                                    ),
                                    "khoan": clause_num,
                                    "diem": point_label or None,
                                    "level": 3 if point_label else 2,
                                    "la_chunk_toan_dieu": False,
                                })
                            else:
                                windows = self._split_by_size_smart(point_text)
                                for win_idx, win_text in enumerate(windows, start=1):
                                    article_parts.append({
                                        "text": win_text,
                                        "don_vi_con": (
                                            f"khoản_{clause_num}_điểm_{point_label}_cửa_sổ_{win_idx}"
                                            if point_label else f"khoản_{clause_num}_mở_đầu_cửa_sổ_{win_idx}"
                                        ),
                                        "khoan": clause_num,
                                        "diem": point_label or None,
                                        "level": 3 if point_label else 2,
                                        "la_chunk_toan_dieu": False,
                                    })
                        continue

                    if len(clause_text) <= self.max_chars:
                        article_parts.append({
                            "text": clause_text,
                            "don_vi_con": f"khoản_{clause_num}",
                            "khoan": clause_num,
                            "diem": None,
                            "level": 2,
                            "la_chunk_toan_dieu": False,
                        })
                    else:
                        windows = self._split_by_size_smart(clause_text)
                        for win_idx, win_text in enumerate(windows, start=1):
                            article_parts.append({
                                "text": win_text,
                                "don_vi_con": f"khoản_{clause_num}_cửa_sổ_{win_idx}",
                                "khoan": clause_num,
                                "diem": None,
                                "level": 2,
                                "la_chunk_toan_dieu": False,
                            })

            if not article_parts:
                if len(article_text) <= self.max_chars:
                    article_parts.append({
                        "text": article_text,
                        "don_vi_con": "toàn_bộ_điều",
                        "khoan": None,
                        "diem": None,
                        "level": 1,
                        "la_chunk_toan_dieu": True,
                    })
                else:
                    windows = self._split_by_size_smart(article_text)
                    for win_idx, win_text in enumerate(windows, start=1):
                        article_parts.append({
                            "text": win_text,
                            "don_vi_con": f"cửa_sổ_điều_{win_idx}",
                            "khoan": None,
                            "diem": None,
                            "level": 1,
                            "la_chunk_toan_dieu": True,
                        })

            for i, part in enumerate(article_parts, start=1):
                built = self._build_refined_chunk(
                    text=part["text"],
                    metadata=article_metadata,
                    chi_so_chunk=i,
                    tong_so_chunk=len(article_parts),
                    don_vi_con=part["don_vi_con"],
                    khoan=part["khoan"],
                    diem=part["diem"],
                    level=part["level"],
                    la_chunk_toan_dieu=part["la_chunk_toan_dieu"],
                )

                if self.deduplicate:
                    content_hash = self._content_hash(built["text"])
                    if content_hash in seen_hashes:
                        continue
                    seen_hashes.add(content_hash)

                refined.append(built)

        return refined

    def _normalize_legal_text(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"\bĐ\s*i\s*ề\s*u\b", "Điều", text, flags=re.IGNORECASE)
        text = re.sub(r"Điều\s*\n\s*(\d+)\.", r"Điều \1.", text, flags=re.IGNORECASE)
        text = re.sub(r"(\w)\s*-\s*\n\s*(\w)", r"\1-\2", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        text = re.sub(r"(?<!\n)(\s)([a-zđ]\)\s+)", r"\n\2", text, flags=re.IGNORECASE)
        text = re.sub(r"(?<!\n)(\s)([a-zđ]\.\d+\)\s+)", r"\n\2", text, flags=re.IGNORECASE)
        return text.strip()

    def _split_by_clause(self, article_text: str) -> List[Tuple[int, str]]:
        article_text = article_text.strip()
        article_title, body = self._extract_article_title_and_body(article_text)

        if not body:
            return []

        matches = list(re.finditer(r"(?:(?<=\n)|^)\s*(\d+)\.\s+", body))
        if not matches:
            return []

        chunks: List[Tuple[int, str]] = []
        preface = body[:matches[0].start()].strip()

        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)

            clause_num = int(match.group(1))
            raw_clause_text = body[start:end].strip()

            clause_body = re.sub(r"^\s*\d+\.\s+", "", raw_clause_text, count=1).strip()

            if i == 0 and preface:
                clause_body = f"{preface}\n{clause_body}".strip()

            formatted_clause = f"Khoản {clause_num}. {clause_body}".strip()
            combined = f"{article_title}\n\n{formatted_clause}".strip()
            chunks.append((clause_num, combined))

        return chunks

    def _split_by_letter_points(self, text: str) -> List[Tuple[Optional[str], str]]:
        text = text.strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        if len(lines) < 2:
            return [(None, text)]

        article_title = lines[0]
        rest = "\n".join(lines[1:]).strip()

        m_clause = re.match(r"^(Khoản\s+\d+\.\s*)(.*)$", rest, flags=re.IGNORECASE | re.DOTALL)
        if not m_clause:
            return [(None, text)]

        clause_header = m_clause.group(1).strip()
        clause_body = m_clause.group(2).strip()

        matches = list(re.finditer(r"(?:(?<=\n)|^)\s*([a-zđ])\)\s+", clause_body, flags=re.IGNORECASE))
        if not matches:
            return [(None, text)]

        chunks: List[Tuple[Optional[str], str]] = []

        intro = clause_body[:matches[0].start()].strip()
        if intro:
            intro_text = f"{article_title}\n\n{clause_header} {intro}".strip()
            chunks.append((None, intro_text))

        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(clause_body)
            point_label = match.group(1).lower()

            raw_point_text = clause_body[start:end].strip()
            point_body = re.sub(r"^\s*[a-zđ]\)\s+", "", raw_point_text, count=1, flags=re.IGNORECASE).strip()

            formatted_point = f"Điểm {point_label}) {point_body}".strip()
            combined = f"{article_title}\n\n{clause_header}\n{formatted_point}".strip()
            chunks.append((point_label, combined))

        return chunks

    def _extract_article_title_and_body(self, article_text: str) -> Tuple[str, str]:
        text = article_text.strip()
        lines = text.splitlines()

        if not lines:
            return "", ""

        first_line = lines[0].strip()

        # Extract article title from a line like:
        # "Điều 16. Xử lý ... 1. Các trường hợp ..."
        m = re.match(r"^(Điều\s+\d+\.\s+.*?)(?=\s+\d+\.\s+|$)", first_line, flags=re.IGNORECASE)
        if m:
            article_title = m.group(1).strip()
            remaining_first_line = first_line[m.end():].strip()
            rest_lines = lines[1:]
            body_parts = []
            if remaining_first_line:
                body_parts.append(remaining_first_line)
            body_parts.extend(rest_lines)
            return article_title, "\n".join(body_parts).strip()

        if len(lines) >= 2:
            return first_line, "\n".join(lines[1:]).strip()

        return text, ""

    def _split_by_size_smart(self, text: str) -> List[str]:
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
            candidates = ["\n\n", "\n", ". ", "; ", ": ", ", ", " "]

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
        level: int,
        la_chunk_toan_dieu: bool,
    ) -> Dict[str, Any]:
        new_metadata = dict(metadata)
        new_metadata["chi_so_chunk"] = chi_so_chunk
        new_metadata["tong_so_chunk"] = tong_so_chunk
        new_metadata["don_vi_con"] = don_vi_con
        new_metadata["la_chunk_toan_dieu"] = bool(la_chunk_toan_dieu)
        new_metadata["level"] = int(level)
        new_metadata["khoan"] = int(khoan) if khoan is not None else ""
        new_metadata["diem"] = str(diem) if diem is not None else ""

        chunk_id = self._make_chunk_id(new_metadata)
        new_metadata["chunk_id"] = chunk_id

        final_text = self._enrich_chunk_text(text.strip(), new_metadata) if self.enrich_context else text.strip()

        return {"text": final_text, "metadata": new_metadata}

    def _make_chunk_id(self, metadata: Dict[str, Any]) -> str:
        ma_van_ban = str(metadata.get("ma_van_ban") or metadata.get("ten_van_ban") or "van_ban")
        ma_van_ban = self._safe_slug(ma_van_ban)

        dieu = metadata.get("dieu", "")
        khoan = metadata.get("khoan", "")
        diem = metadata.get("diem", "")
        don_vi_con = self._safe_slug(str(metadata.get("don_vi_con", "")))
        chi_so_chunk = metadata.get("chi_so_chunk", "")

        parts = [ma_van_ban]

        if dieu not in (None, ""):
            parts.append(f"dieu{dieu}")
        if khoan not in (None, ""):
            parts.append(f"khoan{khoan}")
        if diem not in (None, ""):
            parts.append(f"diem{diem}")
        if don_vi_con:
            parts.append(don_vi_con)
        if chi_so_chunk not in (None, ""):
            parts.append(f"chunk{chi_so_chunk}")

        return "_".join(parts)

    def _enrich_chunk_text(self, text: str, metadata: Dict[str, Any]) -> str:
        context_lines = []

        ten_van_ban = metadata.get("ten_van_ban")
        tieu_de_dieu = metadata.get("tieu_de_dieu")
        dieu = metadata.get("dieu")
        khoan = metadata.get("khoan")
        diem = metadata.get("diem")
        don_vi_con = metadata.get("don_vi_con")

        if ten_van_ban:
            context_lines.append(f"Văn bản: {ten_van_ban}")

        if tieu_de_dieu:
            context_lines.append(f"{tieu_de_dieu}")
        elif dieu not in (None, ""):
            context_lines.append(f"Điều {dieu}")

        if khoan not in (None, ""):
            context_lines.append(f"Khoản {khoan}")

        if diem not in (None, ""):
            context_lines.append(f"Điểm {diem}")

        if don_vi_con:
            context_lines.append(f"Đơn vị nội dung: {don_vi_con}")

        context = "\n".join(context_lines).strip()
        if not context:
            return text

        if text.startswith(context):
            return text

        return f"{context}\n\n{text}"

    @staticmethod
    def _safe_slug(value: str) -> str:
        value = value.strip().lower()
        value = re.sub(r"[^\w]+", "_", value, flags=re.UNICODE)
        value = re.sub(r"_+", "_", value)
        return value.strip("_")

    @staticmethod
    def _content_hash(text: str) -> str:
        normalized = re.sub(r"\s+", " ", text.strip().lower())
        return hashlib.md5(normalized.encode("utf-8")).hexdigest()
