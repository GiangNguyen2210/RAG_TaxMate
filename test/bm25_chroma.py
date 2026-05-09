from infrastructure.vectorstores.chroma_store import ChromaStore
from application.retrieval.bm25_retriever import BM25Retriever

store = ChromaStore()
all_docs = store.get_all_documents(batch_size=500)

print("Loaded docs:", len(all_docs))

bm25 = BM25Retriever(all_docs)

results = bm25.search("miễn tiền chậm nộp", top_k=5)
for r in results:
    print(r["metadata"].get("article_title"), r.get("bm25_score"))