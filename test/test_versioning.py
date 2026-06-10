from application.pipelines.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()

questions = [
    # "ngưỡng doanh thu chịu thuế của hộ kinh doanh là bao nhiêu",
    "hộ kinh doanh dưới 1 tỷ có phải nộp thuế không",
    # "ngưỡng doanh thu sử dụng hóa đơn điện tử là bao nhiêu",
]

for q in questions:
    print("="*80)
    print(q)

    result = pipeline.ask(q)

    for s in result["sources"][:10]:
        print(
            s.get("ten_van_ban"),
            s.get("dieu"),
            s.get("khoan"),
            s.get("score"),
        )