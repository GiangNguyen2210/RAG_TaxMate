from typing import List, Dict, Any


class RecursiveChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        text = (text or "").strip()
        if not text:
            return []

        separators = ["\n\n", "\n", ". ", " ", ""]
        chunks = self._recursive_split(text, separators)

        final_chunks = []
        for chunk in chunks:
            chunk = chunk.strip()
            if chunk:
                final_chunks.append(chunk)

        return final_chunks

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text]

        if not separators:
            return self._fixed_window_split(text)

        sep = separators[0]

        if sep == "":
            return self._fixed_window_split(text)

        parts = text.split(sep)
        if len(parts) == 1:
            return self._recursive_split(text, separators[1:])

        merged = []
        current = ""

        for part in parts:
            candidate = part if not current else current + sep + part
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    merged.append(current)
                current = part

        if current:
            merged.append(current)

        result = []
        for item in merged:
            if len(item) <= self.chunk_size:
                result.append(item)
            else:
                result.extend(self._recursive_split(item, separators[1:]))

        return self._apply_overlap(result)

    def _fixed_window_split(self, text: str) -> List[str]:
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk = text[start:end]
            chunks.append(chunk)

            if end == text_len:
                break

            start = end - self.chunk_overlap

        return chunks

    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        if not chunks:
            return []

        result = [chunks[0]]

        for i in range(1, len(chunks)):
            prev = chunks[i - 1]
            curr = chunks[i]

            overlap_text = prev[-self.chunk_overlap:] if len(prev) > self.chunk_overlap else prev
            combined = overlap_text + curr

            if len(combined) > self.chunk_size + self.chunk_overlap:
                combined = combined[: self.chunk_size + self.chunk_overlap]

            result.append(combined)

        return result

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunked_docs: List[Dict[str, Any]] = []

        for doc in documents:
            text = doc["text"]
            metadata = doc.get("metadata", {})
            chunks = self.split_text(text)

            for idx, chunk in enumerate(chunks):
                chunked_docs.append(
                    {
                        "text": chunk,
                        "metadata": {
                            **metadata,
                            "chunk_index": idx,
                        },
                    }
                )

        return chunked_docs