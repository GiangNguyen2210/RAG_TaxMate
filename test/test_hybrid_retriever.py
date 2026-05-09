from infrastructure.vectorstores.chroma_store import ChromaStore
from infrastructure.embeddings.collab_embedder import ColabEmbedder
from application.retrieval.bm25_retriever import BM25Retriever
from application.retrieval.legal_hybrid_retriever import TaxLegalHybridRetriever


def main():
    vectorstore = ChromaStore()
    embedder = ColabEmbedder()

    all_docs = vectorstore.get_all_documents()
    print("Loaded docs for BM25:", len(all_docs))

    bm25 = BM25Retriever(all_docs)

    retriever = TaxLegalHybridRetriever(
        vectorstore=vectorstore,
        embedder=embedder,
        bm25_retriever=bm25,
        candidates_per_retriever=20,
    )

    queries = [
        "cho mình biết nội dung điều 1 của luật quản lý thuế",
        "khoản 2 điều 5 quy định gì",
        "trường hợp nào được miễn tiền chậm nộp",
        "quy định về tiền chậm nộp thuế là gì",
        "thủ tục đăng ký thuế gồm những gì",
    ]

    for q in queries:
        print("\n" + "=" * 80)
        print("QUERY:", q)
        results = retriever.retrieve(q, top_k=5, debug=True)

        print("\nSOURCES:")
        for r in results:
            meta = r["metadata"]
            print({
                "score": r["score"],
                "source": r["retrieval_source"],
                "ten_van_ban": meta.get("ten_van_ban"),
                "dieu": meta.get("dieu"),
                "khoan": meta.get("khoan"),
                "diem": meta.get("diem"),
                "chu_de": meta.get("chu_de"),
            })


if __name__ == "__main__":
    main()
