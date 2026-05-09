from application.pipelines.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()

result = pipeline.ask("cho mình biết nội dung điều 1 của luật quản lý thuế")

print("QUESTION:", result["question"])
print("ANSWER:", result["answer"])
print("SOURCES:", result["sources"])