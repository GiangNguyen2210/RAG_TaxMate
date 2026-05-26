from typing import Dict, Any, List


class CitationEvaluator:
    @staticmethod
    def contains_all(text: str, phrases: List[str]) -> bool:
        text = (text or "").lower()
        return all(p.lower() in text for p in phrases)

    @staticmethod
    def evaluate(
        benchmark_item: Dict[str, Any],
        answer: str,
    ) -> Dict[str, Any]:
        expected_citation = benchmark_item.get("expected_citation", [])

        if not expected_citation:
            return {
                "citation_required": False,
                "citation_correct": True,
            }

        return {
            "citation_required": True,
            "citation_correct": CitationEvaluator.contains_all(
                answer,
                expected_citation,
            ),
        }