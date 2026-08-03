import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from starlette.concurrency import run_in_threadpool

from api.dependencies import get_rag_pipeline
from api.schemas.rag_schema import (
    HealthResponse,
    RagAskRequest,
    RagAskResponse,
    RagSourceResponse,
)
from application.pipelines.rag_pipeline import RAGPipeline


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/rag",
    tags=["RAG"],
)


def normalize_source(source: dict[str, Any]) -> RagSourceResponse:
    """
    Chuyển source nội bộ của RAG thành response ổn định cho Backend.

    Hỗ trợ cả hai cấu trúc:
    1. Metadata đã được flatten lên source.
    2. Metadata nằm trong source["metadata"].
    """
    metadata = source.get("metadata") or {}

    def get_value(key: str, default: Any = None) -> Any:
        value = source.get(key)

        if value is not None:
            return value

        return metadata.get(key, default)

    return RagSourceResponse(
        document=get_value("ten_van_ban"),
        document_code=get_value("ma_van_ban"),
        dieu=get_value("dieu"),
        khoan=get_value("khoan"),
        diem=get_value("diem"),
        title=get_value("tieu_de_dieu"),
        score=source.get("score"),
        retrieval_source=source.get("retrieval_source"),
        page=get_value("trang_bat_dau"),
        metadata=metadata,
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Kiểm tra trạng thái RAG API",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="taxmate-rag-api",
    )


@router.post(
    "/ask",
    response_model=RagAskResponse,
    status_code=status.HTTP_200_OK,
    summary="Gửi câu hỏi đến TaxMate RAG",
)
async def ask_rag(
    request: RagAskRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
) -> RagAskResponse:
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question must not be empty.",
        )

    try:
        # pipeline.ask hiện là synchronous và có thể chạy lâu.
        # Chạy trong threadpool để không block event loop của FastAPI.
        result = await run_in_threadpool(
            pipeline.ask,
            question,
        )

        if not isinstance(result, dict):
            raise ValueError(
                "RAGPipeline.ask() must return a dictionary."
            )

        answer = str(result.get("answer") or "").strip()
        raw_sources = result.get("sources") or []

        if not answer:
            answer = (
                "Hệ thống chưa tạo được câu trả lời từ dữ liệu hiện có."
            )

        sources = [
            normalize_source(source)
            for source in raw_sources
            if isinstance(source, dict)
        ]

        return RagAskResponse(
            question=question,
            answer=answer,
            sources=sources,
        )

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "RAG request failed. Question=%s",
            question,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RAG service failed to process the question.",
        ) from exc