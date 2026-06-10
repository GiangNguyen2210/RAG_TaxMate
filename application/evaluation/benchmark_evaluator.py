from typing import Dict, Any

from application.evaluation.citation_evaluator import CitationEvaluator
from application.evaluation.hallucination_evaluator import HallucinationEvaluator

DOCUMENT_ALIASES = {
    "Luật quản lý thuế 108/2025/QH15": [
        "108-2025-QH15",
        "Luật quản lý thuế 108/2025/QH15",
    ],

    "Luật Thuế giá trị gia tăng 48/2024/QH15": [
        "48-2024-QH15",
        "Luật Thuế giá trị gia tăng 48/2024/QH15",
    ],

    "Luật Thuế thu nhập cá nhân 109/2025/QH15": [
        "109-2025-QH15",
        "Luật Thuế thu nhập cá nhân 109/2025/QH15",
    ],

    "Nghị quyết 198/2025/QH15": [
        "198-2025-QH15",
        "Nghị quyết 198/2025/QH15",
    ],

    "68-2026-ND-CP": [
        "68-2026-ND-CP",
    ],

    "70-2025-ND-CP": [
        "70-2025-ND-CP",
    ],

    "Thông tư 18/2023/TT-BTC": [
        "18-2023-TT-BTC",
        "Thông tư 18/2023/TT-BTC",
    ],

    "Thông tư 32/2025/TT-BTC": [
        "32-2025-TT-BTC",
        "Thông tư 32/2025/TT-BTC",
    ],
}

class BenchmarkEvaluator:

    @staticmethod
    def contains_any(text: str, keywords: list[str]) -> bool:
        text = (text or "").lower()
        return any(k.lower() in text for k in keywords)

    @staticmethod
    def evaluate(
        benchmark_item: Dict[str, Any],
        result: Dict[str, Any],
    ) -> Dict[str, Any]:

        answer = result.get("answer", "")
        sources = result.get("sources", [])
        top_source = sources[0] if sources else {}

        expected_doc = benchmark_item.get("expected_document")
        expected_dieu = benchmark_item.get("expected_dieu")
        expected_khoan = benchmark_item.get("expected_khoan")
        expected_keywords = benchmark_item.get("expected_keywords", [])

        acceptable_dieu = benchmark_item.get("acceptable_dieu", [])
        acceptable_khoan = benchmark_item.get("acceptable_khoan", [])

        top_doc = top_source.get("ten_van_ban")
        top_dieu = top_source.get("dieu")
        top_khoan = top_source.get("khoan")

        is_doc_correct = BenchmarkEvaluator.document_match(
            expected_doc,
            top_doc,
        )

        if acceptable_dieu:
            is_dieu_correct = top_dieu in acceptable_dieu
        else:
            is_dieu_correct = expected_dieu is None or top_dieu == expected_dieu

        if acceptable_khoan:
            is_khoan_correct = str(top_khoan) in [str(x) for x in acceptable_khoan]
        else:
            is_khoan_correct = expected_khoan is None or str(top_khoan) == str(expected_khoan)

        is_keyword_correct = BenchmarkEvaluator.contains_any(
            answer,
            expected_keywords,
        )

        hallucination_eval = HallucinationEvaluator.evaluate(
            item=benchmark_item,
            answer=answer,
        )

        citation_eval = CitationEvaluator.evaluate(
            benchmark_item=benchmark_item,
            answer=answer,
        )

        return {
            "document_correct": is_doc_correct,
            "dieu_correct": is_dieu_correct,
            "khoan_correct": is_khoan_correct,
            "keyword_match": is_keyword_correct,
            "must_contain_match": hallucination_eval["must_contain_match"],
            "hallucination_safe": hallucination_eval["hallucination_safe"],
            "citation_required": citation_eval["citation_required"],
            "citation_correct": citation_eval["citation_correct"],
        }
    
    @staticmethod
    def document_match(
        expected_doc: str | None,
        actual_doc: str | None,
    ) -> bool:

        if expected_doc is None:
            return True

        aliases = DOCUMENT_ALIASES.get(
            expected_doc,
            [expected_doc]
        )

        return actual_doc in aliases