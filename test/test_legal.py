from application.retrieval.legal_hybrid_retriever import TaxLegalHybridRetriever
from pprint import pprint

retriever = TaxLegalHybridRetriever()

queries = [
    "141-2026-NĐ-CP",
    "01 tỷ đồng",
    "1 tỷ đồng",
    "sửa đổi nghị định 68",
]

for q in queries:
    print("\n" + "=" * 80)
    print(q)

    docs = retriever.retrieve(q)

    for d in docs[:10]:
        md = d["metadata"]

        print(
            md.get("ten_van_ban"),
            md.get("dieu"),
            md.get("khoan"),
            d.get("score")
        )