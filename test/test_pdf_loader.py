from infrastructure.loaders.pdf_loader import PdfLoader

loader = PdfLoader()
docs = loader.load("data/sample.pdf")

print("TOTAL PAGES LOADED:", len(docs))
print(docs[0]["metadata"] if docs else "NO DOCS")
print(docs[0]["text"][:500] if docs else "NO TEXT")