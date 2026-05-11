import re

from infrastructure.loaders.pdf_loader import PdfLoader
from infrastructure.parser.legal_parser import LegalDocumentParser
from infrastructure.refiner.legal_chunk_refiner import LegalChunkRefiner


def normalize_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def contains_phrase(text: str, phrase: str) -> bool:
    return phrase in normalize_text(text)


def main():
    loader = PdfLoader()
    parser = LegalDocumentParser()
    refiner = LegalChunkRefiner(
        max_chars=2500,
        overlap_chars=200,
        keep_full_article=True,
        always_split_clauses=True,
        split_points=True,
        enrich_context=True,
    )

    page_docs = loader.load("data/raw/legal/108-2025-QH15.pdf")

    article_chunks = parser.parse_articles(
        page_docs=page_docs,
        ten_van_ban="Luật quản lý thuế 108/2025/QH15",
        ma_van_ban="108_2025_QH15",
        loai_van_ban="luật",
        cap_ban_hanh="trung_ương",
        dung_truoc_phu_luc=True,
    )

    refined = refiner.refine_chunks(article_chunks)

    print("Article chunks:", len(article_chunks))
    print("Refined chunks:", len(refined))

    full_article_chunks = [c for c in refined if c["metadata"].get("la_chunk_toan_dieu") is True]
    clause_chunks = [c for c in refined if c["metadata"].get("level") == 2]
    point_chunks = [c for c in refined if c["metadata"].get("level") == 3]

    print("Full article chunks:", len(full_article_chunks))
    print("Clause chunks:", len(clause_chunks))
    print("Point chunks:", len(point_chunks))

    assert full_article_chunks, "Must have full article chunks"
    assert all(c["metadata"].get("chunk_id") for c in refined), "Every chunk must have chunk_id"
    assert all(c["metadata"].get("level") in [1, 2, 3] for c in refined), "Every chunk must have level"

    print("\\n=== Điều 5 chunks ===")
    dieu5 = [c for c in refined if c["metadata"].get("dieu") == 5]
    for c in dieu5:
        m = c["metadata"]
        print({
            "chunk_id": m.get("chunk_id"),
            "dieu": m.get("dieu"),
            "khoan": m.get("khoan"),
            "diem": m.get("diem"),
            "level": m.get("level"),
            "don_vi_con": m.get("don_vi_con"),
            "la_chunk_toan_dieu": m.get("la_chunk_toan_dieu"),
        })
        print(normalize_text(c["text"])[:500])
        print("---")

    assert any(c["metadata"].get("la_chunk_toan_dieu") for c in dieu5), "Điều 5 must have full article chunk"
    assert any(c["metadata"].get("khoan") == 1 for c in dieu5), "Điều 5 must have Khoản 1 chunk"
    assert any(c["metadata"].get("khoan") == 2 for c in dieu5), "Điều 5 must have Khoản 2 chunk"
    assert not any(
        c["metadata"].get("khoan") == 5 and c["metadata"].get("level") == 2
        for c in dieu5
    ), "Điều 5 must NOT create fake Khoản 5 from article number"

    dieu5_khoan1 = [
        c for c in dieu5
        if c["metadata"].get("khoan") == 1
        and c["metadata"].get("level") == 2
    ]

    assert dieu5_khoan1, "Điều 5 must have Khoản 1 level-2 chunk"
    assert any(contains_phrase(c["text"], "Khoản 1.") for c in dieu5_khoan1), "Khoản 1 text must contain 'Khoản 1.'"
    assert not any(
        contains_phrase(c["text"], "Điều 1. Cơ quan thuế")
        for c in dieu5_khoan1
    ), "Khoản 1 must not be formatted as Điều 1"

    print("\\n=== Điều 16 chunks ===")
    dieu16 = [c for c in refined if c["metadata"].get("dieu") == 16]
    for c in dieu16[:25]:
        m = c["metadata"]
        print({
            "chunk_id": m.get("chunk_id"),
            "dieu": m.get("dieu"),
            "khoan": m.get("khoan"),
            "diem": m.get("diem"),
            "level": m.get("level"),
            "don_vi_con": m.get("don_vi_con"),
            "la_chunk_toan_dieu": m.get("la_chunk_toan_dieu"),
        })
        print(normalize_text(c["text"])[:500])
        print("---")

    assert any(c["metadata"].get("la_chunk_toan_dieu") for c in dieu16), "Điều 16 must have full article chunk"
    assert any(c["metadata"].get("khoan") == 1 for c in dieu16), "Điều 16 must have Khoản 1 chunk"
    assert any(c["metadata"].get("khoan") == 2 for c in dieu16), "Điều 16 must have Khoản 2 chunk"
    assert any(c["metadata"].get("khoan") == 5 for c in dieu16), "Điều 16 must have Khoản 5 chunk"
    assert not any(
        c["metadata"].get("khoan") == 16 and c["metadata"].get("level") == 2
        for c in dieu16
    ), "Điều 16 must NOT create fake Khoản 16 from article number"

    diem_a = [
        c for c in dieu16
        if c["metadata"].get("khoan") == 1
        and c["metadata"].get("diem") == "a"
        and c["metadata"].get("level") == 3
    ]

    assert diem_a, "Điều 16 Khoản 1 must have Điểm a chunk"
    assert any(
        contains_phrase(c["text"], "Điểm a)")
        for c in diem_a
    ), "Point chunk must contain formatted 'Điểm a)'"

    print("\\nAll chunking tests passed.")


if __name__ == "__main__":
    main()
