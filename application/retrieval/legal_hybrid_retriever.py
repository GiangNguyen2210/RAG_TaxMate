from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from application.retrieval.query_analyzer import analyze_query, QueryInfo
from application.retrieval.bm25_retriever import BM25Retriever
from infrastructure.vectorstores.chroma_store import ChromaStore
from infrastructure.embeddings.collab_embedder import ColabEmbedder
from application.retrieval.reranker import Reranker


@dataclass
class RetrievedChunk:
    id: str
    score: float
    text: str
    metadata: Dict[str, Any]
    retrieval_source: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "score": self.score,
            "text": self.text,
            "metadata": self.metadata,
            "retrieval_source": self.retrieval_source,
        }


class TaxLegalHybridRetriever:
    """
    Legal-aware hybrid retriever for TaxMate.

    Flow:
    1. Query understanding: Điều / Khoản / Điểm / intent / exact phrases.
    2. Structured retrieval: metadata filtering, e.g. dieu=16.
    3. Exact retrieval: document text contains legal phrases.
    4. BM25 lexical retrieval.
    5. Dense retrieval through Chroma + ColabEmbedder.
    6. RRF fusion + rule boosts.
    7. Sibling expansion: attach all chunks in the same Điều/Khoản when needed.
    """

    def __init__(
        self,
        vectorstore: Optional[ChromaStore] = None,
        embedder: Optional[ColabEmbedder] = None,
        bm25_retriever: Optional[BM25Retriever] = None,
        rrf_k: int = 60,
        candidates_per_retriever: int = 20,
        sibling_neighbors: int = 1,
        sibling_expand_limit: int = 30,
        enable_reranker: bool | None = None,
        reranker: Optional[Reranker] = None,
        rerank_top_k: int | None = None,
    ):
        self.vectorstore = vectorstore or ChromaStore()
        self.embedder = embedder or ColabEmbedder()
        self.rrf_k = rrf_k
        self.candidates_per_retriever = candidates_per_retriever
        self.sibling_neighbors = sibling_neighbors
        self.sibling_expand_limit = sibling_expand_limit

        if enable_reranker is None:
            enable_reranker = os.getenv("RAG_ENABLE_RERANKER", "false").lower() == "true"

        self.enable_reranker = enable_reranker
        self.rerank_top_k = rerank_top_k or int(os.getenv("RAG_RERANK_TOP_K", "5"))
        self.reranker = reranker or (Reranker() if self.enable_reranker else None)

        if bm25_retriever is None:
            all_docs = self.vectorstore.get_all_documents()
            self.bm25 = BM25Retriever(all_docs)
        else:
            self.bm25 = bm25_retriever

        self._all_docs_cache = getattr(self.bm25, "docs", [])
        self._location_index = self._build_location_index(self._all_docs_cache)

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
        candidate_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        debug: bool = False,
    ) -> List[Dict[str, Any]]:
        candidate_k = candidate_k or max(20, top_k * 4)
        filters = filters or {}

        qinfo = analyze_query(question)

        structured = self._structured_retrieval(qinfo, filters)
        exact = self._exact_retrieval(qinfo, filters)
        bm25 = self._bm25_retrieval(question, candidate_k, filters)
        dense = self._dense_retrieval(question, candidate_k, filters)

        fused = self._rrf_fuse(
            ranked_lists=[
                ("structured", structured),
                ("exact", exact),
                ("bm25", bm25),
                ("dense", dense),
            ],
            qinfo=qinfo,
            top_k=candidate_k,
        )

        enriched = self._attach_siblings(fused, qinfo)

        # Attach legal siblings, especially all Điểm under the same Khoản.
        expanded = self._expand_sibling_chunks(
            retrieved_chunks=enriched,
            qinfo=qinfo,
            filters=filters,
            max_expand=self.sibling_expand_limit,
        )

        # Do not cut too early when the user asks a specific Điều/Khoản,
        # because the answer may need all Điểm under that Khoản.
        final_limit = self._final_limit(top_k=top_k, qinfo=qinfo, expanded_count=len(expanded))

        # Reranker is useful for broad/semantic queries.
        # For explicit Điều + Khoản queries, keep hierarchy-expanded chunks intact
        # so all Điểm under that Khoản are not accidentally removed.
        if self.enable_reranker and self.reranker is not None and not self._should_skip_rerank(qinfo):
            final = self.reranker.rerank(
                query=question,
                chunks=expanded,
                top_k=min(self.rerank_top_k, final_limit),
            )
        else:
            final = expanded[:final_limit]

        if debug:
            self._debug_print(qinfo, structured, exact, bm25, dense, final)

        return [c.to_dict() for c in final]

    get_relevant_chunks = retrieve

    def get_chunks_by_location(
        self,
        ma_van_ban: Optional[str] = None,
        dieu: Optional[int] = None,
        khoan: Optional[int] = None,
        diem: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if dieu is None:
            return []

        results: List[RetrievedChunk] = []
        keys = []

        if ma_van_ban:
            keys.append((ma_van_ban, int(dieu)))
        else:
            keys.extend([k for k in self._location_index.keys() if k[1] == int(dieu)])

        for key in keys:
            for doc in self._location_index.get(key, []):
                meta = doc.get("metadata", {})

                if khoan is not None and str(meta.get("khoan", "")) != str(khoan):
                    continue

                if diem is not None and str(meta.get("diem", "")).lower() != str(diem).lower():
                    continue

                results.append(self._to_chunk(doc, score=1.0, source="location"))

        return [r.to_dict() for r in results]

    def _structured_retrieval(self, qinfo, filters):
        docs = []
        where = self._base_where(filters)

        if qinfo.dieu is not None:
            where_dieu = dict(where)
            where_dieu["dieu"] = qinfo.dieu
            docs.extend(self.vectorstore.get_by_metadata(where=where_dieu, limit=30))

            if qinfo.khoan is not None:
                where_khoan = dict(where_dieu)
                where_khoan["khoan"] = qinfo.khoan
                docs.extend(self.vectorstore.get_by_metadata(where=where_khoan, limit=30))

            if qinfo.khoan is not None and qinfo.diem is not None:
                where_diem = dict(where_khoan)
                where_diem["diem"] = qinfo.diem
                docs.extend(self.vectorstore.get_by_metadata(where=where_diem, limit=10))

            return [self._to_chunk(d, score=1.0, source="structured") for d in docs]

        if qinfo.loai_van_ban:
            where_type = dict(where)
            where_type["loai_van_ban"] = qinfo.loai_van_ban
            docs.extend(self.vectorstore.get_by_metadata(where=where_type, limit=20))

        if qinfo.chu_de:
            where_topic = dict(where)
            where_topic["chu_de"] = qinfo.chu_de
            docs.extend(self.vectorstore.get_by_metadata(where=where_topic, limit=20))

        return [self._to_chunk(d, score=1.0, source="structured") for d in docs]

    def _exact_retrieval(
        self,
        qinfo: QueryInfo,
        filters: Dict[str, Any],
    ) -> List[RetrievedChunk]:
        docs: List[Dict[str, Any]] = []
        phrases = list(qinfo.cum_tu_chinh_xac)

        if qinfo.dieu is not None:
            phrases.append(f"Điều {qinfo.dieu}")

        if qinfo.khoan is not None:
            phrases.append(f"Khoản {qinfo.khoan}")
            phrases.append(f"khoản {qinfo.khoan}")

        if qinfo.diem is not None:
            phrases.append(f"Điểm {qinfo.diem}")
            phrases.append(f"điểm {qinfo.diem}")

        for phrase in phrases:
            if not phrase:
                continue
            try:
                found = self.vectorstore.get_by_document_filter(
                    where_document={"$contains": phrase},
                    limit=20,
                )
                docs.extend(self._apply_python_filters(found, filters))
            except Exception:
                docs.extend(self._manual_contains_search(phrase, filters, limit=20))

        return [self._to_chunk(d, score=1.0, source="exact") for d in docs]

    def _bm25_retrieval(
        self,
        question: str,
        top_k: int,
        filters: Dict[str, Any],
    ) -> List[RetrievedChunk]:
        docs = self.bm25.search(question, top_k=top_k * 2)
        docs = self._apply_python_filters(docs, filters)
        docs = docs[:top_k]

        out: List[RetrievedChunk] = []
        for d in docs:
            score = float(d.get("bm25_score", 0.0))
            out.append(self._to_chunk(d, score=score, source="bm25"))
        return out

    def _dense_retrieval(
        self,
        question: str,
        top_k: int,
        filters: Dict[str, Any],
    ) -> List[RetrievedChunk]:
        query_embedding = self.embedder.embed_text(question)
        where = self._base_where(filters)

        docs = self.vectorstore.similarity_search_by_vector(
            query_embedding=query_embedding,
            k=top_k,
            where=where or None,
        )

        out: List[RetrievedChunk] = []
        for d in docs:
            distance = d.get("distance")
            score = 1.0 - float(distance) if distance is not None else 0.0
            out.append(self._to_chunk(d, score=score, source="dense"))
        return out

    def _rrf_fuse(
        self,
        ranked_lists: List[Tuple[str, List[RetrievedChunk]]],
        qinfo: QueryInfo,
        top_k: int,
    ) -> List[RetrievedChunk]:
        scores: Dict[str, float] = {}
        chunks: Dict[str, RetrievedChunk] = {}

        for source_name, items in ranked_lists:
            for rank, chunk in enumerate(items, start=1):
                key = self._chunk_key(chunk)
                scores[key] = scores.get(key, 0.0) + 1.0 / (self.rrf_k + rank)

                if key not in chunks:
                    chunks[key] = chunk
                else:
                    old_sources = chunks[key].retrieval_source
                    if source_name not in old_sources:
                        chunks[key].retrieval_source = old_sources + "+" + source_name

        boosted: List[Tuple[float, RetrievedChunk]] = []
        for key, chunk in chunks.items():
            score = scores.get(key, 0.0)
            score += self._rule_boost(chunk, qinfo)
            chunk.score = score
            boosted.append((score, chunk))

        boosted.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in boosted[:top_k]]

    def _rule_boost(self, chunk: RetrievedChunk, qinfo: QueryInfo) -> float:
        meta = chunk.metadata
        text = (chunk.text or "").lower()
        title = str(meta.get("tieu_de_dieu", "")).lower()
        boost = 0.0

        if qinfo.dieu is not None:
            if meta.get("dieu") == qinfo.dieu:
                boost += 0.35
            else:
                boost -= 0.08

        if qinfo.khoan is not None:
            if str(meta.get("khoan", "")) == str(qinfo.khoan):
                boost += 0.25
            elif meta.get("dieu") == qinfo.dieu and meta.get("khoan") in (None, ""):
                boost += 0.04

        if qinfo.diem is not None and str(meta.get("diem", "")).lower() == str(qinfo.diem).lower():
            boost += 0.10

        if qinfo.loai_van_ban and meta.get("loai_van_ban") == qinfo.loai_van_ban:
            boost += 0.05

        if qinfo.chu_de and meta.get("chu_de") == qinfo.chu_de:
            boost += 0.05

        for phrase in qinfo.cum_tu_chinh_xac:
            if phrase in text:
                boost += 0.08
            if phrase in title:
                boost += 0.10

        return boost

    def _attach_siblings(
        self,
        primaries: List[RetrievedChunk],
        qinfo: QueryInfo,
    ) -> List[RetrievedChunk]:
        if not primaries:
            return []

        seen = {self._chunk_key(c) for c in primaries}
        enriched = list(primaries)

        for primary in primaries:
            meta = primary.metadata
            ma_van_ban = meta.get("ma_van_ban", "")
            dieu = meta.get("dieu")
            khoan = meta.get("khoan")

            if not ma_van_ban or not dieu:
                continue

            try:
                dieu_int = int(dieu)
            except (TypeError, ValueError):
                continue

            siblings = self._location_index.get((ma_van_ban, dieu_int), [])

            try:
                khoan_int = int(khoan) if khoan not in (None, "") else None
            except (TypeError, ValueError):
                khoan_int = None

            for doc in siblings:
                sib = self._to_chunk(doc, score=0.0, source="sibling")
                key = self._chunk_key(sib)

                if key in seen:
                    continue

                sib_khoan = sib.metadata.get("khoan")
                should_attach = False

                if qinfo.dieu is not None and qinfo.dieu == dieu_int and qinfo.khoan is None:
                    should_attach = True

                if khoan_int is not None:
                    try:
                        sib_khoan_int = int(sib_khoan) if sib_khoan not in (None, "") else None
                    except (TypeError, ValueError):
                        sib_khoan_int = None

                    if sib_khoan_int is not None and 0 < abs(sib_khoan_int - khoan_int) <= self.sibling_neighbors:
                        should_attach = True

                if should_attach:
                    sib.metadata["la_ngu_canh_bo_sung"] = True
                    enriched.append(sib)
                    seen.add(key)

        return enriched

    @staticmethod
    def _to_chunk(doc: Dict[str, Any], score: float, source: str) -> RetrievedChunk:
        text = doc.get("text") or doc.get("content") or ""
        metadata = dict(doc.get("metadata", {}))
        doc_id = str(
            doc.get("id")
            or metadata.get("chunk_id")
            or metadata.get("ma_van_ban", "") + "_" + str(metadata.get("dieu", ""))
        )

        return RetrievedChunk(
            id=doc_id,
            score=float(score),
            text=text,
            metadata=metadata,
            retrieval_source=source,
        )

    @staticmethod
    def _chunk_key(chunk: RetrievedChunk) -> str:
        meta = chunk.metadata

        if meta.get("chunk_id"):
            return str(meta.get("chunk_id"))

        if chunk.id:
            return str(chunk.id)

        return "|".join([
            str(meta.get("ma_van_ban", "")),
            str(meta.get("dieu", "")),
            str(meta.get("khoan", "")),
            str(meta.get("diem", "")),
            chunk.text[:100],
        ])

    @staticmethod
    def _build_location_index(docs: List[Dict[str, Any]]) -> Dict[Tuple[str, int], List[Dict[str, Any]]]:
        index: Dict[Tuple[str, int], List[Dict[str, Any]]] = {}

        for doc in docs:
            meta = doc.get("metadata", {})
            ma_van_ban = meta.get("ma_van_ban", "")
            dieu = meta.get("dieu")

            try:
                dieu_int = int(dieu) if dieu not in (None, "") else None
            except (TypeError, ValueError):
                dieu_int = None

            if ma_van_ban and dieu_int is not None:
                index.setdefault((ma_van_ban, dieu_int), []).append(doc)

        return index

    @staticmethod
    def _base_where(filters: Dict[str, Any]) -> Dict[str, Any]:
        where: Dict[str, Any] = {}

        for key in [
            "ma_van_ban",
            "loai_van_ban",
            "trang_thai_hieu_luc",
            "chu_de",
            "co_quan_ban_hanh",
        ]:
            value = filters.get(key)
            if value not in (None, "", "all"):
                where[key] = value

        return where

    @staticmethod
    def _doc_passes_filters(doc: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        meta = doc.get("metadata", {})

        for key in [
            "ma_van_ban",
            "loai_van_ban",
            "trang_thai_hieu_luc",
            "chu_de",
            "co_quan_ban_hanh",
        ]:
            value = filters.get(key)
            if value not in (None, "", "all") and meta.get(key) != value:
                return False

        return True

    def _apply_python_filters(
        self,
        docs: List[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        if not filters:
            return docs
        return [d for d in docs if self._doc_passes_filters(d, filters)]

    def _manual_contains_search(
        self,
        phrase: str,
        filters: Dict[str, Any],
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        phrase_lower = phrase.lower()
        results = []

        for doc in self._all_docs_cache:
            text = (doc.get("text") or "").lower()
            title = str(doc.get("metadata", {}).get("tieu_de_dieu", "")).lower()

            if phrase_lower in text or phrase_lower in title:
                if self._doc_passes_filters(doc, filters):
                    results.append(doc)

            if len(results) >= limit:
                break

        return results

    @staticmethod
    def _debug_print(
        qinfo: QueryInfo,
        structured: List[RetrievedChunk],
        exact: List[RetrievedChunk],
        bm25: List[RetrievedChunk],
        dense: List[RetrievedChunk],
        final: List[RetrievedChunk],
    ) -> None:
        print("\n=== QUERY INFO ===")
        print(qinfo)

        print("\n=== RETRIEVAL COUNTS ===")
        print("structured:", len(structured))
        print("exact:", len(exact))
        print("bm25:", len(bm25))
        print("dense:", len(dense))

        print("\n=== FINAL TOP RESULTS ===")
        for i, c in enumerate(final, start=1):
            meta = c.metadata
            print(
                f"{i}. score={c.score:.4f} source={c.retrieval_source} "
                f"{meta.get('ten_van_ban')} | Điều {meta.get('dieu')} "
                f"Khoản {meta.get('khoan')} Điểm {meta.get('diem')}"
            )
            print((c.text or "")[:250].replace("\n", " "))
            print("---")

    def _expand_sibling_chunks(
        self,
        retrieved_chunks: List[RetrievedChunk],
        qinfo: QueryInfo,
        filters: Dict[str, Any],
        max_expand: int = 30,
    ) -> List[RetrievedChunk]:
        """
        Legal hierarchy expansion.

        Main case:
        - Query: "Khoản 2 Điều 5 quy định gì"
        - If anchor contains dieu=5, khoan=2
        - Attach all chunks with dieu=5 and khoan=2, including điểm a,b,c,d,đ,e.

        This method works on RetrievedChunk, not dict.
        """
        if not retrieved_chunks:
            return []

        if qinfo.khoan is None:
            return retrieved_chunks
        
        seen = {self._chunk_key(c) for c in retrieved_chunks}
        expanded = list(retrieved_chunks)

        expansion_targets = []

        if qinfo.dieu is not None and qinfo.khoan is not None:
            expansion_targets.append({
                "dieu": qinfo.dieu,
                "khoan": qinfo.khoan,
            })

        for chunk in retrieved_chunks:
            meta = chunk.metadata
            dieu = meta.get("dieu")
            khoan = meta.get("khoan")

            if dieu in (None, "") or khoan in (None, "", 0):
                continue

            expansion_targets.append({
                "dieu": dieu,
                "khoan": khoan,
            })

        unique_targets = []
        seen_targets = set()
        for target in expansion_targets:
            key = (str(target["dieu"]), str(target["khoan"]))
            if key in seen_targets:
                continue
            seen_targets.add(key)
            unique_targets.append(target)

        base_where = self._base_where(filters)

        for target in unique_targets:
            where = dict(base_where)
            where["dieu"] = target["dieu"]
            where["khoan"] = target["khoan"]

            sibling_docs = self.vectorstore.get_by_metadata(
                where=where,
                limit=max_expand,
            )

            sibling_chunks = [
                self._to_chunk(d, score=0.0, source="sibling_expand")
                for d in sibling_docs
            ]

            sibling_chunks.sort(key=self._legal_order_key)

            for sibling in sibling_chunks:
                key = self._chunk_key(sibling)
                if key in seen:
                    continue

                sibling.score = self._sibling_score(sibling, qinfo)
                sibling.retrieval_source = "sibling_expand"
                sibling.metadata["la_ngu_canh_bo_sung"] = True

                expanded.append(sibling)
                seen.add(key)

        expanded.sort(key=self._final_sort_key, reverse=True)
        return expanded

    def _sibling_score(self, chunk: RetrievedChunk, qinfo: QueryInfo) -> float:
        meta = chunk.metadata
        score = 0.18

        if qinfo.dieu is not None and meta.get("dieu") == qinfo.dieu:
            score += 0.10

        if qinfo.khoan is not None and str(meta.get("khoan", "")) == str(qinfo.khoan):
            score += 0.10

        if meta.get("level") == 2:
            score += 0.03

        if meta.get("level") == 3:
            score += 0.02

        return score

    def _final_sort_key(self, chunk: RetrievedChunk) -> Tuple[float, int, int, str]:
        """
        Score first, then legal hierarchy level, then legal order.
        """
        level = chunk.metadata.get("level")
        try:
            level_int = int(level) if level not in (None, "") else 99
        except (TypeError, ValueError):
            level_int = 99

        return (
            float(chunk.score),
            -level_int,
            -self._legal_order_number(chunk),
            str(chunk.metadata.get("diem", "")),
        )

    def _legal_order_key(self, chunk: RetrievedChunk) -> Tuple[int, int, int, int]:
        meta = chunk.metadata

        try:
            level = int(meta.get("level", 99))
        except (TypeError, ValueError):
            level = 99

        try:
            khoan = int(meta.get("khoan", 0)) if meta.get("khoan") not in (None, "") else 0
        except (TypeError, ValueError):
            khoan = 0

        point_order = self._point_order(str(meta.get("diem", "")))

        try:
            chunk_index = int(meta.get("chi_so_chunk", 0))
        except (TypeError, ValueError):
            chunk_index = 0

        return (khoan, level, point_order, chunk_index)

    def _legal_order_number(self, chunk: RetrievedChunk) -> int:
        meta = chunk.metadata

        try:
            khoan = int(meta.get("khoan", 0)) if meta.get("khoan") not in (None, "") else 0
        except (TypeError, ValueError):
            khoan = 0

        return khoan * 100 + self._point_order(str(meta.get("diem", "")))

    @staticmethod
    def _point_order(diem: str) -> int:
        order = {
            "": 0,
            "a": 1,
            "b": 2,
            "c": 3,
            "d": 4,
            "đ": 5,
            "e": 6,
            "g": 7,
            "h": 8,
            "i": 9,
            "k": 10,
            "l": 11,
            "m": 12,
            "n": 13,
        }
        return order.get((diem or "").lower(), 99)

    @staticmethod
    def _should_skip_rerank(qinfo: QueryInfo) -> bool:
        """
        Skip reranking for highly structured legal lookup.

        Reason:
        - Query like "Khoản 2 Điều 5" needs all sibling Điểm.
        - Reranker may keep only 5 chunks and accidentally drop Điểm c/đ/e.
        """
        return qinfo.dieu is not None and qinfo.khoan is not None

    def _final_limit(self, top_k: int, qinfo: QueryInfo, expanded_count: int) -> int:
        if qinfo.dieu is not None and qinfo.khoan is not None:
            return min(max(top_k, 12), expanded_count)

        if qinfo.dieu is not None:
            return min(max(top_k, 8), expanded_count)

        return min(top_k, expanded_count)