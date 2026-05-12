import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from infrastructure.embeddings.collab_embedder import ColabEmbedder
from infrastructure.vectorstores.chroma_store import ChromaStore
from infrastructure.llm.gemini_client import GeminiClient

from application.retrieval.bm25_retriever import BM25Retriever
from application.retrieval.legal_hybrid_retriever import TaxLegalHybridRetriever

load_dotenv()


class RAGPipeline:
    """
    TaxMate RAG pipeline using legal-aware hybrid retrieval.

    Flow:
    Question
    -> TaxLegalHybridRetriever
       - metadata retrieval
       - exact phrase retrieval
       - BM25
       - dense retrieval
       - RRF fusion
       - sibling expansion
    -> build legal context
    -> Gemini answer
    """

    def __init__(self):
        self.embedder = ColabEmbedder()
        self.vectorstore = ChromaStore()
        self.llm = GeminiClient()

        self.top_k = int(os.getenv("RAG_TOP_K", "5"))
        self.max_context_chars = int(os.getenv("RAG_MAX_CONTEXT_CHARS", "12000"))
        self.debug = os.getenv("RAG_DEBUG", "false").lower() == "true"

        all_docs = self.vectorstore.get_all_documents()
        self.bm25 = BM25Retriever(all_docs)

        self.retriever = TaxLegalHybridRetriever(
            vectorstore=self.vectorstore,
            embedder=self.embedder,
            bm25_retriever=self.bm25,
            candidates_per_retriever=int(os.getenv("RAG_CANDIDATES_PER_RETRIEVER", "20")),
            sibling_neighbors=int(os.getenv("RAG_SIBLING_NEIGHBORS", "1")),
        )

    def _build_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        context_parts = []
        total_chars = 0

        for i, item in enumerate(retrieved_docs, start=1):
            meta = item.get("metadata", {})
            text = (item.get("text") or item.get("content") or "").strip()

            if not text:
                continue

            ten_van_ban = meta.get("ten_van_ban", "không_xác_định")
            ma_van_ban = meta.get("ma_van_ban", "không_xác_định")
            loai_van_ban = meta.get("loai_van_ban", "")
            co_quan_ban_hanh = meta.get("co_quan_ban_hanh", "")
            ngay_hieu_luc = meta.get("ngay_hieu_luc", "")
            trang_thai = meta.get("trang_thai_hieu_luc", "")

            chuong = meta.get("chuong", "")
            dieu = meta.get("dieu", "")
            khoan = meta.get("khoan", "")
            diem = meta.get("diem", "")
            tieu_de_dieu = meta.get("tieu_de_dieu", "")
            trang_bat_dau = meta.get("trang_bat_dau", "")

            score = item.get("score")
            retrieval_source = item.get("retrieval_source", "")

            location_parts = []
            if chuong:
                location_parts.append(str(chuong))
            if dieu not in (None, ""):
                location_parts.append(f"Điều {dieu}")
            if khoan not in (None, ""):
                location_parts.append(f"Khoản {khoan}")
            if diem not in (None, ""):
                location_parts.append(f"Điểm {diem}")

            location = " | ".join(location_parts) if location_parts else "Không rõ vị trí"

            header = (
                f"[Nguồn {i}]\n"
                f"Văn bản: {ten_van_ban}\n"
                f"Mã văn bản: {ma_van_ban}\n"
                f"Loại văn bản: {loai_van_ban}\n"
                f"Cơ quan ban hành: {co_quan_ban_hanh}\n"
                f"Hiệu lực: {trang_thai} | Ngày hiệu lực: {ngay_hieu_luc}\n"
                f"Vị trí: {location}\n"
                f"Tiêu đề điều: {tieu_de_dieu}\n"
                f"Trang bắt đầu: {trang_bat_dau}\n"
                f"Retrieval: {retrieval_source} | Score: {score}\n"
            )

            block = f"{header}\nNội dung:\n{text}\n"

            if total_chars + len(block) > self.max_context_chars:
                break

            context_parts.append(block)
            total_chars += len(block)

        return "\n---\n".join(context_parts)

    def ask(self, question: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        question = (question or "").strip()
        if not question:
            raise ValueError("Question must not be empty.")

        retrieved_docs = self.retriever.retrieve(
            question=question,
            top_k=self.top_k,
            filters=filters,
            debug=self.debug,
        )

        context = self._build_context(retrieved_docs)

        if self.debug:
            print("\n=== FINAL CONTEXT SENT TO LLM ===")
            print(context[:3000])

        # answer = self.llm.generate_answer(
        #     question=question,
        #     context=context,
        # )

        answer = "Đây là câu trả lời giả định từ LLM dựa trên ngữ cảnh đã cho. Câu trả lời thực tế sẽ được tạo ra bởi mô hình Gemini của Google dựa trên câu hỏi và ngữ cảnh pháp lý được cung cấp."

        if self.debug:
            print("\n=== ANSWER FROM LLM ===")
            print(answer)

        return {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "ten_van_ban": d.get("metadata", {}).get("ten_van_ban"),
                    "ma_van_ban": d.get("metadata", {}).get("ma_van_ban"),
                    "loai_van_ban": d.get("metadata", {}).get("loai_van_ban"),
                    "co_quan_ban_hanh": d.get("metadata", {}).get("co_quan_ban_hanh"),
                    "trang_thai_hieu_luc": d.get("metadata", {}).get("trang_thai_hieu_luc"),
                    "ngay_hieu_luc": d.get("metadata", {}).get("ngay_hieu_luc"),
                    "chuong": d.get("metadata", {}).get("chuong"),
                    "dieu": d.get("metadata", {}).get("dieu"),
                    "khoan": d.get("metadata", {}).get("khoan"),
                    "diem": d.get("metadata", {}).get("diem"),
                    "tieu_de_dieu": d.get("metadata", {}).get("tieu_de_dieu"),
                    "trang_bat_dau": d.get("metadata", {}).get("trang_bat_dau"),
                    "chu_de": d.get("metadata", {}).get("chu_de"),
                    "score": d.get("score"),
                    "retrieval_source": d.get("retrieval_source"),
                }
                for d in retrieved_docs
            ],
        }
