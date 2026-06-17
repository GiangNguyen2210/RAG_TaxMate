import re
from datetime import datetime, timezone
from typing import Any

import requests
from bs4 import BeautifulSoup


class HtmlArticleCrawler:
    def fetch_article(self, item: dict[str, Any]) -> dict[str, Any]:
        url = item.get("url")

        if not url:
            item["content"] = None
            item["article_crawled_at"] = datetime.now(timezone.utc).isoformat()
            item["crawl_error"] = "Missing URL"
            return item

        try:
            html = self._download_html(url)
            content = self._extract_content(html)
            published_at = self._extract_published_at(html)

            item["content"] = content
            item["published_at"] = item.get("published_at") or published_at
            item["article_crawled_at"] = datetime.now(timezone.utc).isoformat()
            item["crawl_error"] = None

            return item

        except Exception as ex:
            item["content"] = None
            item["article_crawled_at"] = datetime.now(timezone.utc).isoformat()
            item["crawl_error"] = str(ex)
            return item

    def _download_html(self, url: str) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or "utf-8"

        return response.text

    def _extract_content(self, html: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        candidates = []

        selectors = [
            ".article-content",
            ".news-detail",
            ".content-detail",
            ".detail-content",
            ".item-page",
            ".content",
            "article",
            "main",
        ]

        for selector in selectors:
            node = soup.select_one(selector)
            if node:
                text = node.get_text("\n", strip=True)
                if len(text) > 300:
                    candidates.append(text)

        if candidates:
            return max(candidates, key=len)

        body = soup.body
        if not body:
            return None

        text = body.get_text("\n", strip=True)

        lines = []
        for line in text.splitlines():
            line = line.strip()
            if len(line) >= 30:
                lines.append(line)

        cleaned_text = "\n".join(lines)

        return cleaned_text if len(cleaned_text) > 300 else None

    def _extract_published_at(self, html: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")

        selectors = [
            "time",
            ".date",
            ".news-date",
            ".article-date",
            ".publish-date",
            ".created-date",
            ".time",
        ]

        candidates = []

        for selector in selectors:
            for node in soup.select(selector):
                value = (
                    node.get("datetime")
                    or node.get_text(" ", strip=True)
                )

                if value:
                    candidates.append(value)

        candidates.append(
            soup.get_text(" ", strip=True)
        )

        patterns = [
            r"\b(\d{1,2}/\d{1,2}/\d{4})\b",
            r"\b(\d{1,2}-\d{1,2}-\d{4})\b",
            r"\b(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2})\b",
        ]

        for candidate in candidates:
            for pattern in patterns:
                match = re.search(pattern, candidate)

                if not match:
                    continue

                raw = match.group(1)

                for fmt in (
                    "%d/%m/%Y %H:%M",
                    "%d/%m/%Y",
                    "%d-%m-%Y",
                ):
                    try:
                        dt = datetime.strptime(raw, fmt)
                        return dt.isoformat()
                    except ValueError:
                        continue

        return None