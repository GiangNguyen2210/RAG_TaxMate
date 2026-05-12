from application.pipelines.rag_pipeline import RAGPipeline


def main():
    pipeline = RAGPipeline()

    questions = [
        "cho mình biết nội dung điều 1 của luật quản lý thuế",
        "khoản 2 điều 5 quy định gì",
        "trường hợp nào được miễn tiền chậm nộp",
        "thủ tục đăng ký thuế gồm những gì",
        "quản lý thuế quốc tế gồm những nội dung nào",
    ]

    for q in questions:
        print("\n" + "=" * 100)
        print("QUESTION:", q)

        result = pipeline.ask(q)

        print("\nANSWER:")
        print(result["answer"])

        print("\nSOURCES:")
        for s in result["sources"]:
            print({
                "source": s.get("retrieval_source"),
                "score": s.get("score"),
                "dieu": s.get("dieu"),
                "khoan": s.get("khoan"),
                "diem": s.get("diem"),
                "title": s.get("tieu_de_dieu"),
            })


if __name__ == "__main__":
    main()
