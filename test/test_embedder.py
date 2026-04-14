from infrastructure.embeddings.gemini_embedder import GeminiEmbedder

embedder = GeminiEmbedder()
vector = embedder.embed_text("What is retrieval augmented generation?")

print("VECTOR TYPE:", type(vector))
print("VECTOR LENGTH:", len(vector))
print("FIRST 10 VALUES:", vector[:10])