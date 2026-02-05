"""Content Crawler Service - SNS, 유튜브, 블로그 등에서 콘텐츠 수집.

전문가의 공개된 콘텐츠를 자동으로 수집하여 지식베이스에 추가합니다.
"""

import re
from dataclasses import dataclass
from typing import Any

import httpx
from bs4 import BeautifulSoup

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None


@dataclass
class CrawledContent:
    """Crawled content from a source."""

    title: str
    content: str
    source_url: str
    source_type: str
    metadata: dict[str, Any]


class ContentCrawler:
    """Service for crawling content from various sources."""

    def __init__(self):
        """Initialize Content Crawler."""
        self.timeout = 30.0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def _extract_youtube_id(self, url: str) -> str | None:
        """Extract YouTube video ID from URL."""
        patterns = [
            r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)",
            r"youtube\.com/shorts/([^&\n?#]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    async def crawl_youtube(self, url: str) -> CrawledContent | None:
        """Crawl YouTube video transcript.

        Args:
            url: YouTube video URL

        Returns:
            CrawledContent with transcript or None if failed
        """
        if YouTubeTranscriptApi is None:
            return None

        video_id = self._extract_youtube_id(url)
        if not video_id:
            return None

        try:
            # Get transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # Try Korean first, then auto-generated, then any
            transcript = None
            try:
                transcript = transcript_list.find_transcript(["ko"])
            except Exception:
                try:
                    transcript = transcript_list.find_generated_transcript(["ko", "en"])
                except Exception:
                    transcripts = list(transcript_list)
                    if transcripts:
                        transcript = transcripts[0]

            if not transcript:
                return None

            # Fetch transcript text
            transcript_data = transcript.fetch()
            content = " ".join([item["text"] for item in transcript_data])

            # Get video title via HTTP
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"https://www.youtube.com/watch?v={video_id}",
                    headers=self.headers,
                )
                soup = BeautifulSoup(response.text, "html.parser")
                title_tag = soup.find("title")
                title = title_tag.text.replace(" - YouTube", "") if title_tag else f"YouTube {video_id}"

            return CrawledContent(
                title=title,
                content=content,
                source_url=url,
                source_type="youtube",
                metadata={"video_id": video_id, "language": transcript.language},
            )

        except Exception as e:
            print(f"Error crawling YouTube: {e}")
            return None

    async def crawl_webpage(self, url: str) -> CrawledContent | None:
        """Crawl generic webpage content.

        Args:
            url: Webpage URL

        Returns:
            CrawledContent with article text or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers, follow_redirects=True)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove unwanted elements
            for tag in soup(["script", "style", "nav", "header", "footer", "aside", "ad"]):
                tag.decompose()

            # Get title
            title = ""
            if soup.title:
                title = soup.title.text.strip()
            elif soup.find("h1"):
                title = soup.find("h1").text.strip()

            # Try to find main content
            content = ""

            # Look for article or main content areas
            main_content = (
                soup.find("article")
                or soup.find("main")
                or soup.find(class_=re.compile(r"article|content|post|entry", re.I))
                or soup.find(id=re.compile(r"article|content|post|entry", re.I))
            )

            if main_content:
                # Get all paragraphs from main content
                paragraphs = main_content.find_all(["p", "h2", "h3", "li"])
                content = "\n\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
            else:
                # Fallback: get all paragraphs
                paragraphs = soup.find_all("p")
                content = "\n\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())

            if not content:
                return None

            # Determine source type from URL
            source_type = "article"
            if "blog" in url.lower() or "tistory" in url.lower() or "naver.com" in url.lower():
                source_type = "blog"
            elif "linkedin.com" in url.lower():
                source_type = "linkedin"
            elif "twitter.com" in url.lower() or "x.com" in url.lower():
                source_type = "twitter"
            elif "threads.net" in url.lower():
                source_type = "threads"

            return CrawledContent(
                title=title,
                content=content,
                source_url=url,
                source_type=source_type,
                metadata={},
            )

        except Exception as e:
            print(f"Error crawling webpage: {e}")
            return None

    async def crawl(self, url: str) -> CrawledContent | None:
        """Crawl content from URL, auto-detecting source type.

        Args:
            url: URL to crawl

        Returns:
            CrawledContent or None if failed
        """
        # Check if YouTube
        if "youtube.com" in url or "youtu.be" in url:
            return await self.crawl_youtube(url)

        # Generic webpage crawl
        return await self.crawl_webpage(url)

    async def crawl_and_chunk(
        self,
        url: str,
        chunk_size: int = 1000,
    ) -> list[CrawledContent]:
        """Crawl content and split into chunks.

        Args:
            url: URL to crawl
            chunk_size: Maximum characters per chunk

        Returns:
            List of CrawledContent chunks
        """
        content = await self.crawl(url)
        if not content:
            return []

        if len(content.content) <= chunk_size:
            return [content]

        # Split into chunks
        chunks = []
        text = content.content
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))

            # Find a good break point
            if end < len(text):
                for sep in ["\n\n", "\n", "。", ".", " "]:
                    break_point = text.rfind(sep, start + chunk_size // 2, end)
                    if break_point > start:
                        end = break_point + len(sep)
                        break

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    CrawledContent(
                        title=f"{content.title} (Part {len(chunks) + 1})",
                        content=chunk_text,
                        source_url=content.source_url,
                        source_type=content.source_type,
                        metadata={**content.metadata, "chunk_index": len(chunks)},
                    )
                )

            start = end

        return chunks


def get_content_crawler() -> ContentCrawler:
    """Get ContentCrawler instance."""
    return ContentCrawler()
