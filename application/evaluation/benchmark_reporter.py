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

        failure_counter = defaultdict(int)

        print("\n========== SUMMARY ==========")
        print(f"Total: {total}")

        for key in metric_keys:
            score = sum(1 for e in evaluations if e.get(key, False))
            percent = (score / total * 100) if total else 0
            print(f"{key}: {score}/{total} ({percent:.1f}%)")

        print("\n========== FAILED CASES ==========")

        for item, evaluation in zip(items, evaluations):
            for key in metric_keys:
                if evaluation.get(key) is False:
                    failure_counter[key] += 1
            
            failed_metrics = [
                k
                for k in metric_keys
                if evaluation.get(k) is False
            ]

            if failed_metrics:
                print("\n----------------------------------------")
                print("ID:", item["id"])
                print("CATEGORY:", item.get("category"))
                print("QUESTION:", item["question"])
                print("FAILED:", ", ".join(failed_metrics))
                if "document_correct" in failed_metrics:
                    print(
                        "Expected Doc:",
                        item.get("expected_document")
                    )

                if "dieu_correct" in failed_metrics:
                    print(
                        "Expected Điều:",
                        item.get("expected_dieu")
                    )

                if "khoan_correct" in failed_metrics:
                    print(
                        "Expected Khoản:",
                        item.get("expected_khoan")
                    )

        print("\n========== CATEGORY SUMMARY ==========")

        category_failures = defaultdict(int)

        for item, evaluation in zip(items, evaluations):

            if not all(
                evaluation.get(k, True)
                for k in metric_keys
            ):
                category_failures[
                    item.get("category", "unknown")
                ] += 1

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

        perfect_cases = sum(
            1
            for e in evaluations
            if all(e.get(k, True) for k in metric_keys)
        )

        print(
            f"\nPerfect Cases: "
            f"{perfect_cases}/{total} "
            f"({perfect_cases/total*100:.1f}%)"
        )

        print("\n========== FAILURE BREAKDOWN ==========")

        for metric, count in sorted(
            failure_counter.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"{metric}: {count}")

        print("\n========== CATEGORY FAILURES ==========")

        for cat, count in sorted(
            category_failures.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(cat, count)