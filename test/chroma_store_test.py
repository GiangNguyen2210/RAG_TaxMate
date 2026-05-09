from infrastructure.vectorstores.chroma_store import ChromaStore

store = ChromaStore()

docs = store.get_by_metadata(where={"article": 1}, limit=3)
print("By metadata:", len(docs))
for d in docs:
    print(d["metadata"].get("article_title"))

docs2 = store.get_by_document_filter(where_document={"$contains": "miễn tiền chậm nộp"}, limit=3)
print("By text filter:", len(docs2))
for d in docs2:
    print(d["metadata"].get("article_title"))