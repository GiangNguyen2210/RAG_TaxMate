from infrastructure.loaders.pdf_loader import PdfLoader
from infrastructure.chunking.generic_chunking.recursive_chunker import RecursiveChunker

loader = PdfLoader()
chunker = RecursiveChunker(chunk_size=1000, chunk_overlap=200)

docs = loader.load("data/sample.pdf")
chunk_docs = chunker.chunk_documents(docs)

print("TOTAL CHUNKS:", len(chunk_docs))

if chunk_docs:
    print("FIRST CHUNK METADATA:", chunk_docs[0]["metadata"])
    print("FIRST CHUNK LENGTH:", len(chunk_docs[0]["text"]))
    print(chunk_docs[0]["text"][:500])