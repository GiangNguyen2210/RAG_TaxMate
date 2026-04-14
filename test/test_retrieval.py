from infrastructure.embeddings.gemini_embedder import GeminiEmbedder
from infrastructure.vectorstores.chroma_store import ChromaStore

embedder = GeminiEmbedder()
store = ChromaStore()

question = "What is the main topic of this document?"
query_embedding = embedder.embed_text(question)
results = store.similarity_search_by_vector(query_embedding, k=3)

print("RESULT COUNT:", len(results))

for i, item in enumerate(results, start=1):
    print(f"\n--- RESULT {i} ---")
    print("METADATA:", item["metadata"])
    print("DISTANCE:", item["distance"])
    print("TEXT:", item["text"][:500])