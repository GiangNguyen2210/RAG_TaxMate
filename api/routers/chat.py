from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from application.pipelines.rag_pipeline import RAGPipeline

router = APIRouter(prefix="/chat", tags=["chat"])
rag_pipeline = RAGPipeline()


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = rag_pipeline.ask(request.question)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))