import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.dependencies import get_rag_pipeline
from api.routers.rag_router import router as rag_router


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    ),
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TaxMate RAG API...")

    # Warm up pipeline khi server khởi động.
    # Request đầu tiên sẽ không phải khởi tạo toàn bộ retriever.
    get_rag_pipeline()

    logger.info("TaxMate RAG pipeline initialized.")

    yield

    logger.info("Stopping TaxMate RAG API...")


app = FastAPI(
    title="TaxMate RAG API",
    description=(
        "REST API cung cấp câu trả lời từ hệ thống TaxMate RAG."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "RAG_ALLOWED_ORIGINS",
        "http://localhost:5086,https://localhost:5173"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(rag_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "TaxMate RAG API",
        "status": "running",
        "docs": "/docs",
    }