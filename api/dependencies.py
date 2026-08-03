from functools import lru_cache

from application.pipelines.rag_pipeline import RAGPipeline


@lru_cache(maxsize=1)
def get_rag_pipeline() -> RAGPipeline:
    """
    Khởi tạo duy nhất một RAGPipeline trong vòng đời process API.
    """
    return RAGPipeline()