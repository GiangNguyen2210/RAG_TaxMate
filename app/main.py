from fastapi import FastAPI
from api.routers.chat import router as chat_router

app = FastAPI(title="Gemini RAG MVP")

app.include_router(chat_router)