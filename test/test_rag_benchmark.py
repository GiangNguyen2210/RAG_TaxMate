from contextlib import redirect_stdout

from application.pipelines.rag_pipeline import RAGPipeline
from application.evaluation.benchmark_questions import BENCHMARK_QUESTIONS
from application.evaluation.benchmark_evaluator import BenchmarkEvaluator
from application.evaluation.benchmark_reporter import BenchmarkReporter


def run_benchmark():
    pipeline = RAGPipeline()

    evaluations = []

    print("\n========== TAXMATE RAG BENCHMARK ==========\n")

    for item in BENCHMARK_QUESTIONS:
        result = pipeline.ask(item["question"])

        evaluation = BenchmarkEvaluator.evaluate(
            benchmark_item=item,
            result=result,
        )

        evaluations.append(evaluation)

        BenchmarkReporter.print_case(
            item=item,
            result=result,
            evaluation=evaluation,
        )

    BenchmarkReporter.print_summary(
        evaluations=evaluations,
        items=BENCHMARK_QUESTIONS,
    )


def main():
    output_file = "benchmark_report.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        with redirect_stdout(f):
            run_benchmark()

    print(f"\nBenchmark saved to: {output_file}")


if __name__ == "__main__":
    main()