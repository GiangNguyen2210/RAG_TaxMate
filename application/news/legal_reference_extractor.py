import re


class LegalReferenceExtractor:
    PATTERNS = [
        r"Luật\s+số\s+\d+\/\d{4}\/[A-ZĐ\-]+",
        r"Nghị định\s+số\s+\d+\/\d{4}\/NĐ-CP",
        r"Thông tư\s+số\s+\d+\/\d{4}\/TT-BTC",
        r"Công văn\s+số\s+\d+\/[A-Z0-9\-]+",
        r"Quyết định\s+số\s+\d+\/[A-Z0-9\-]+",
        r"\d+\/\d{4}\/NĐ-CP",
        r"\d+\/\d{4}\/TT-BTC",
        r"\d+\/\d{4}\/QH\d+",
    ]

    def extract(self, title: str | None, summary: str | None) -> list[str]:
        text = f"{title or ''} {summary or ''}"

        results: list[str] = []

        for pattern in self.PATTERNS:
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            results.extend(matches)

        cleaned = []

        for item in results:
            normalized = item.strip()
            if normalized and normalized not in cleaned:
                cleaned.append(normalized)

        return cleaned