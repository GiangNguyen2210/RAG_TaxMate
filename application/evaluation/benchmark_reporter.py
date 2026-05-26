from collections import defaultdict
from typing import Dict, Any, List


class BenchmarkReporter:

    @staticmethod
    def print_case(item: Dict[str, Any], result: Dict[str, Any], evaluation: Dict[str, Any]) -> None:
        answer = result.get("answer", "")
        sources = result.get("sources", [])
        top_source = sources[0] if sources else {}

        print("=" * 100)
        print("ID:", item["id"])
        print("CATEGORY:", item.get("category"))
        print("QUESTION:", item["question"])

        print("\nANSWER:")
        print(answer)

        print("\nTOP SOURCE:")
        print({
            "document": top_source.get("ten_van_ban"),
            "dieu": top_source.get("dieu"),
            "khoan": top_source.get("khoan"),
            "diem": top_source.get("diem"),
            "score": top_source.get("score"),
            "source": top_source.get("retrieval_source"),
        })

        print("\nCHECK:")
        for key, value in evaluation.items():
            print(f"{key}: {value}")

    @staticmethod
    def print_summary(evaluations: List[Dict[str, Any]], items: List[Dict[str, Any]]) -> None:
        total = len(evaluations)

        metric_keys = [
            "document_correct",
            "dieu_correct",
            "khoan_correct",
            "keyword_match",
            "must_contain_match",
            "hallucination_safe",
            "citation_correct",
        ]

        print("\n========== SUMMARY ==========")
        print(f"Total: {total}")

        for key in metric_keys:
            score = sum(1 for e in evaluations if e.get(key, False))
            percent = (score / total * 100) if total else 0
            print(f"{key}: {score}/{total} ({percent:.1f}%)")

        print("\n========== CATEGORY SUMMARY ==========")

        by_category = defaultdict(list)
        for item, evaluation in zip(items, evaluations):
            by_category[item.get("category", "unknown")].append(evaluation)

        for category, rows in by_category.items():
            passed = sum(
                1 for e in rows
                if all(e.get(k, True) for k in metric_keys)
            )
            total_cat = len(rows)
            percent = (passed / total_cat * 100) if total_cat else 0
            print(f"{category}: {passed}/{total_cat} ({percent:.1f}%)")