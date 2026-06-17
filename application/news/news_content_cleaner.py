import re
import unicodedata

class NewsContentCleaner:
    REMOVE_AFTER_MARKERS = [
        "Thuế Việt Nam - Trang thông tin điện tử của Cục Thuế",
        "Cơ quan chủ quản: Bộ Tài chính",
        "Ghi rõ nguồn",
        "Bạn đã nhấn vào một liên kết",
        "gdt.gov.vn không chịu trách nhiệm",
        "Chức năng này đang được xây dựng",
    ]

    REMOVE_EXACT_LINES = {
        "Ứng dụng hỗ trợ người nộp thuế",
        (
            "NGÀNH THUẾ COI TRỌNG, XÂY DỰNG VÀ GÌN GIỮ CÁC GIÁ TRỊ "
            "“MINH BẠCH – CHUYÊN NGHIỆP – LIÊM CHÍNH – ĐỔI MỚI\""
        ),
    }

    RELATED_NEWS_HINTS = [
        "Cục Thuế gửi THƯ NGỎ",
        "Không tiếp tay cho các hành vi gian lận thuế",
        "Tăng cường phối hợp đào tạo liên ngành",
        "Mua bán hóa đơn giá trị gia tăng trái phép",
        "Bộ trưởng Ngô Văn Tuấn tiếp",

        "Báo chí và ngành Thuế Việt Nam:",
        "Bế giảng lớp bồi dưỡng",
        "Khẩn trương giải quyết vướng mắc",
        "Khai giảng lớp bồi dưỡng",
        "Tình hình thực hiện nhiệm vụ trọng tâm",
        "Sổ tay thuế cho hộ, cá nhân kinh doanh",
        "Kiểm soát doanh thu đa kênh",
        "Bản tin Thuế tuần",
    ]

    def clean(
        self,
        title: str | None,
        content: str | None,
    ) -> str | None:
        if not content:
            return None

        text = unicodedata.normalize("NFC", content)
        text = text.replace("\u200b", "")
        text = text.replace("\ufeff", "")
        text = text.replace("\xa0", " ")
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        text = self._remove_after_fixed_markers(text)
        text = self._remove_related_news_block(title, text)
        text = self._remove_noise_lines(text)
        text = self._remove_duplicate_title(title, text)
        text = self._fix_joined_words(text)
        text = self._normalize_whitespace(text)

        return text if len(text) >= 200 else None

    def _remove_after_fixed_markers(self, text: str) -> str:
        positions = []

        for marker in self.REMOVE_AFTER_MARKERS:
            index = text.find(marker)

            if index != -1:
                positions.append(index)

        if positions:
            text = text[:min(positions)]

        return text.strip()

    def _remove_related_news_block(
        self,
        title: str | None,
        text: str,
    ) -> str:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if not lines:
            return text

        search_start = max(3, int(len(lines) * 0.25))

        for index in range(search_start, len(lines)):
            line = lines[index]

            if any(
                hint.lower() in line.lower()
                for hint in self.RELATED_NEWS_HINTS
            ):
                return "\n".join(lines[:index]).strip()

            if (
                title
                and line.strip() == title.strip()
                and index > search_start
            ):
                return "\n".join(lines[:index]).strip()

        return "\n".join(lines)

    def _remove_noise_lines(self, text: str) -> str:
        cleaned_lines = []

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            if line in self.REMOVE_EXACT_LINES:
                continue

            if line.startswith("Địa chỉ:"):
                continue

            if line.startswith("Điện thoại:"):
                continue

            if line.startswith("Fax:"):
                continue

            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def _remove_duplicate_title(
        self,
        title: str | None,
        text: str,
    ) -> str:
        if not title:
            return text

        lines = text.splitlines()
        result = []
        title_seen = False

        for line in lines:
            if line.strip() == title.strip():
                if title_seen:
                    continue

                title_seen = True

            result.append(line)

        return "\n".join(result)

    def _fix_joined_words(self, text: str) -> str:
        urls: list[str] = []

        def protect_url(match: re.Match) -> str:
            index = len(urls)
            urls.append(match.group(0))
            return f"URLPLACEHOLDER{index}"

        # Bảo vệ URL trước khi sửa text
        text = re.sub(
            r"https?://[^\s]+",
            protect_url,
            text,
        )

        exact_replacements = {
            "hóađơn": "hóa đơn",
            "mua bángiả": "mua bán giả",
            "cánhân": "cá nhân",
            "việctập trung": "việc tập trung",
            "mở rộngcác": "mở rộng các",
            "quản lývà": "quản lý và",
            "người nộpthuế": "người nộp thuế",
            "trướcthời hạn": "trước thời hạn",
            "truy thu,xử phạt": "truy thu, xử phạt",
            "hơn.Đặc biệt": "hơn. Đặc biệt",
            "thương mại điệntử": "thương mại điện tử",
            "khuế khoán": "thuế khoán",
            "hgân hàng": "ngân hàng",
            "lính vực": "lĩnh vực",
            "thương maị": "thương mại",
            "tuy nhiện": "tuy nhiên",
        }

        for old, new in exact_replacements.items():
            text = text.replace(old, new)

        regex_replacements = {
            r"hóa[\u200b\ufeff\xa0]*đơn": "hóa đơn",
            r"cá[\u200b\ufeff\xa0]*nhân": "cá nhân",
            r"thương mại[\u200b\ufeff\xa0]*điện tử": "thương mại điện tử",
            r"(?m)^hó Cục trưởng\b": "Phó Cục trưởng",
            r"(?m)^ục trưởng\b": "Cục trưởng",
            r"Phó C\s*\n\s*ục trưởng": "Phó Cục trưởng",
        }

        for pattern, replacement in regex_replacements.items():
            text = re.sub(
                pattern,
                replacement,
                text,
                flags=re.IGNORECASE,
            )

        # Khôi phục URL thật trước khi return
        for index, url in enumerate(urls):
            text = text.replace(
                f"URLPLACEHOLDER{index}",
                url,
            )

        return text

    def _normalize_whitespace(self, text: str) -> str:
        lines = []

        for line in text.splitlines():
            line = re.sub(r"[ \t]+", " ", line).strip()

            if line:
                lines.append(line)

        return "\n".join(lines).strip()