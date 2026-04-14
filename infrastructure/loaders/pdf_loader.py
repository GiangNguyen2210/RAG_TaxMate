from typing import List, Dict, Any
from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract

from scripts.ocr.ocr_cleaner import (
    clean_ocr_text,
    clean_extracted_text,
)


class PdfLoader:
    def load(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Return list of page-level documents:
        [
          {
            "text": "...",
            "metadata": {
                "source": file_path,
                "page": 1,
                "extract_method": "text" | "ocr"
            }
          }
        ]
        """
        reader = PdfReader(file_path)
        page_count = len(reader.pages)
        documents: List[Dict[str, Any]] = []

        # Chỉ render ảnh khi thật sự cần OCR fallback
        images = None

        for idx, page in enumerate(reader.pages):
            raw_text = page.extract_text() or ""
            raw_text = raw_text.strip()

            extract_method = "text"
            final_text = ""

            # Nếu extract_text thất bại hoặc quá ngắn thì fallback OCR
            if len(raw_text) < 50:
                if images is None:
                    images = convert_from_path(file_path)

                print(f"OCR fallback page {idx + 1}/{page_count}")
                ocr_text = pytesseract.image_to_string(images[idx], lang="vie")
                final_text = clean_ocr_text(ocr_text)
                extract_method = "ocr"
            else:
                final_text = clean_extracted_text(raw_text)

            documents.append(
                {
                    "text": final_text,
                    "metadata": {
                        "source": file_path,
                        "page": idx + 1,
                        "extract_method": extract_method,
                    },
                }
            )

        return documents