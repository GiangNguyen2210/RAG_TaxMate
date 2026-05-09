from application.pipelines.rag_pipeline import RAGPipeline


def main():
    pipeline = RAGPipeline()

    questions = [
        "cho mình biết nội dung điều 1 của luật quản lý thuế",
        "khoản 2 điều 5 quy định gì",
        "trường hợp nào được miễn tiền chậm nộp",
        "thủ tục đăng ký thuế gồm những gì",
    ]

    for q in questions:
        print("\n" + "=" * 80)
        result = pipeline.ask(q)

        print("QUESTION:", result["question"])
        print("\nANSWER:")
        print(result["answer"])

        print("\nSOURCES:")
        for s in result["sources"]:
            print(s)


if __name__ == "__main__":
    main()
