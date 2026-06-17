from datetime import datetime, timezone
from typing import Any
import html
import re

import feedparser
import requests


class RssCrawler:
    def fetch(self, source_name: str, rss_url: str) -> list[dict[str, Any]]:
        xml_text = self._download_rss(rss_url)
        cleaned_xml = self._clean_xml(xml_text)

        feed = feedparser.parse(cleaned_xml)

        if feed.bozo:
            print(f"[WARN] RSS parse warning for {source_name}: {feed.bozo_exception}")

        items: list[dict[str, Any]] = []

        for entry in feed.entries:
            item = {
                "source_name": source_name,
                "title": self._clean_text(entry.get("title")),
                "url": entry.get("link"),
                "summary": self._clean_text(entry.get("summary")),
                "published_at": entry.get("published"),
                "crawled_at": datetime.now(timezone.utc).isoformat(),
            }

            if item["title"] and item["url"]:
                items.append(item)

        return items

    def _download_rss(self, rss_url: str) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
        }

        response = requests.get(rss_url, headers=headers, timeout=30)
        response.raise_for_status()

        # GDT thường dùng UTF-8, nhưng để chắc hơn thì để requests tự detect
        response.encoding = response.apparent_encoding or "utf-8"

        return response.text

    def _clean_xml(self, xml_text: str) -> str:
        # Một số RSS site chèn HTML entity không hợp lệ với XML.
        # Ta thay các entity phổ biến trước.
        replacements = {
            "&nbsp;": " ",
            "&ndash;": "-",
            "&mdash;": "-",
            "&hellip;": "...",
            "&lsquo;": "'",
            "&rsquo;": "'",
            "&ldquo;": '"',
            "&rdquo;": '"',
            "&amp;nbsp;": " ",
        }

        for old, new in replacements.items():
            xml_text = xml_text.replace(old, new)

        # Loại bỏ các entity không thuộc 5 entity chuẩn của XML
        # XML chỉ hiểu: amp, lt, gt, quot, apos
        xml_text = re.sub(
            r"&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)",
            "&amp;",
            xml_text,
        )

        return xml_text

    def _clean_text(self, value: str | None) -> str | None:
        if value is None:
            return None

        value = html.unescape(value)
        value = re.sub(r"<[^>]+>", " ", value)
        value = re.sub(r"\s+", " ", value)

        return value.strip()