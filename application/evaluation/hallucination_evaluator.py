from typing import Dict, Any, List


class HallucinationEvaluator:

    @staticmethod
    def contains_any(text: str, phrases: List[str]) -> bool:
        text = (text or "").lower()
        return any(p.lower() in text for p in phrases)

    @staticmethod
    def contains_all(text: str, phrases: List[str]) -> bool:
        text = (text or "").lower()
        return all(p.lower() in text for p in phrases)

    @staticmethod
    def evaluate(item: Dict[str, Any], answer: str) -> Dict[str, Any]:
        must_contain = item.get("must_contain", [])
        must_not_contain = item.get("must_not_contain", [])

        return {
            "must_contain_match": (
                True if not must_contain
                else HallucinationEvaluator.contains_all(answer, must_contain)
            ),
            "hallucination_safe": not HallucinationEvaluator.contains_any(
                answer,
                must_not_contain,
            ),
        }