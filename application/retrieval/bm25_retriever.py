import re
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi


def simple_tokenize(text: str) -> List[str]:
    text = (text or "").lower()

    text = re.sub(
        r"[^\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩị"
        r"òóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]",
        " ",
        text,
    )

    return [tok for tok in text.split() if tok.strip()]


class BM25Retriever:
    def __init__(self, docs: List[Dict[str, Any]]):
        self.docs = docs
        self.corpus_tokens = [simple_tokenize(d.get("text", "")) for d in docs]
        self.bm25 = BM25Okapi(self.corpus_tokens)

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        q_tokens = simple_tokenize(query)
        scores = self.bm25.get_scores(q_tokens)

        ranked = sorted(
            zip(self.docs, scores),
            key=lambda x: x[1],
            reverse=True,
        )[:top_k]

        output = []
        for doc, score in ranked:
            item = dict(doc)
            item["bm25_score"] = float(score)
            item["retrieval_source"] = "bm25"
            output.append(item)

        return output