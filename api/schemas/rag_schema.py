from typing import Any

from pydantic import BaseModel, Field


class RagAskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2,
        max_length=2000,
        description="Câu hỏi được gửi đến hệ thống RAG.",
        examples=[
            "Hộ kinh doanh dưới 1 tỷ đồng có phải nộp thuế không?"
        ],
    )


class RagSourceResponse(BaseModel):
    document: str | None = None
    document_code: str | None = None

    dieu: int | None = None
    khoan: int | str | None = None
    diem: str | None = None

    title: str | None = None
    score: float | None = None
    retrieval_source: str | None = None

    page: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagAskResponse(BaseModel):
    success: bool = True
    question: str
    answer: str
    sources: list[RagSourceResponse] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    service: str