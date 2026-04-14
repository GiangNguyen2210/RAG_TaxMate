from application.pipelines.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()

result = pipeline.ask("cho mình biết chi tiết một phần nội dung trong thông tư")

print("QUESTION:", result["question"])
print("ANSWER:", result["answer"])
print("SOURCES:", result["sources"])