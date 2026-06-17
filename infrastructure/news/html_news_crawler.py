from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class HtmlNewsCrawler:
    def fetch(self, source_name: str, page_url: str) -> list[dict[str, Any]]:
        html = self._download_html(page_url)
        soup = BeautifulSoup(html, "html.parser")

        items: list[dict[str, Any]] = []
        seen_urls = set()

        links = soup.find_all("a", href=True)

        for link in links:
            title = link.get_text(" ", strip=True)
            href = link.get("href")

            if not title or not href:
                continue

            url = urljoin(page_url, href)

            if url in seen_urls:
                continue

            if not self._is_probably_news_link(title, url):
                continue

            seen_urls.add(url)

            items.append(
                {
                    "source_name": source_name,
                    "title": title,
                    "url": url,
                    "summary": None,
                    "published_at": None,
                    "crawled_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        return items

    def _download_html(self, page_url: str) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        response = requests.get(page_url, headers=headers, timeout=30)
        response.raise_for_status()

        response.encoding = response.apparent_encoding or "utf-8"

        return response.text

    def _is_probably_news_link(self, title: str, url: str) -> bool:
        title_lower = title.lower()
        url_lower = url.lower()

        if len(title_lower) < 20:
            return False

        # GDT article thật thường có urile=wcm:path trong URL
        if "urile=wcm" not in url_lower:
            return False

        ignore_keywords = [
            "trang chủ",
            "liên hệ",
            "sơ đồ",
            "đăng nhập",
            "english",
            "rss",
            "facebook",
            "youtube",
            "hỏi đáp về thuế",
            "tổ chức ngành thuế",
            "địa chỉ cơ quan thuế",
            "tin bài về thuế",
            "chính sách thuế",
            "ứng dụng hỗ trợ người nộp thuế",
        ]

        if any(keyword in title_lower for keyword in ignore_keywords):
            return False

        taxmate_keywords = [
            "hộ kinh doanh",
            "cá nhân kinh doanh",
            "hóa đơn điện tử",
            "máy tính tiền",
            "thuế khoán",
            "bỏ phương thức thuế khoán",
            "kê khai",
            "nộp thuế điện tử",
            "thương mại điện tử",
            "sàn thương mại điện tử",
            "mã số thuế",
            "định danh cá nhân",
            "doanh thu",
            "thuế gtgt",
            "thuế tncn",
            "xử phạt",
            "chậm nộp",
        ]

        if any(keyword in title_lower for keyword in taxmate_keywords):
            return True

        return False