class NewsClassifier:
    KEYWORDS = {
        "hộ kinh doanh": 3.0,
        "cá nhân kinh doanh": 3.0,
        "kinh doanh cá thể": 2.5,
        "thuế": 1.5,
        "thuế gtgt": 2.5,
        "thuế tncn": 2.5,
        "hóa đơn điện tử": 3.0,
        "máy tính tiền": 3.0,
        "doanh thu": 2.0,
        "kê khai": 2.0,
        "nộp thuế": 2.0,
        "thương mại điện tử": 2.0,
        "sàn thương mại điện tử": 2.5,
        "mã số thuế": 2.0,
        "định danh cá nhân": 2.5,
        "chậm nộp": 2.0,
        "xử phạt": 2.0,
        "lệ phí môn bài": 2.0,
        "thuế khoán": 2.5,
        "bỏ thuế khoán": 3.0,
    }

    def score(self, title: str | None, summary: str | None) -> float:
        text = f"{title or ''} {summary or ''}".lower()

        score = 0.0

        for keyword, weight in self.KEYWORDS.items():
            if keyword in text:
                score += weight

        return score

    def detect_topic(self, title: str | None, summary: str | None) -> str:
        text = f"{title or ''} {summary or ''}".lower()

        if "hóa đơn điện tử" in text or "máy tính tiền" in text:
            return "e_invoice"

        if "hộ kinh doanh" in text or "cá nhân kinh doanh" in text or "thuế khoán" in text:
            return "household_business_tax"

        if "thuế gtgt" in text or "thuế tncn" in text:
            return "tax_calculation"

        if "chậm nộp" in text or "xử phạt" in text:
            return "penalty"

        if "thương mại điện tử" in text or "sàn thương mại điện tử" in text:
            return "ecommerce_tax"

        if "mã số thuế" in text or "định danh cá nhân" in text:
            return "tax_identification"

        return "general_tax_news"